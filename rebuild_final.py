import subprocess, re

result = subprocess.run(['git', 'show', '205a607:index.html'], capture_output=True)
raw = result.stdout
if raw[:2] == b'\xff\xfe':
    content = raw.decode('utf-16')
else:
    content = raw.decode('utf-8')

print(f'Original size: {len(content)}')

# Change 1: Add local SheetJS <script> before first <script tag
local_script = '<script src="libs/xlsx.full.min.js"></script>\n'
first_script = content.find('<script')
content = content[:first_script] + local_script + content[first_script:]

# Change 2: In handleUpload, only change the inner logic - keep function signature and wrapping intact
# Find the exact body of handleUpload: from { to matching }
start = content.find('async function handleUpload(file) {')
# Find the opening { of function body
brace_start = content.find('{', start)
# Find matching }
depth = 0
pos = brace_start
while pos < len(content):
    if content[pos] == '{': depth += 1
    elif content[pos] == '}':
        depth -= 1
        if depth == 0:
            brace_end = pos
            break
    pos += 1

old_body = content[brace_start+1:brace_end]
print(f'handleUpload body: {len(old_body)} chars, from {brace_start} to {brace_end}')

new_body = '''
  if (!file) return;
  const status = document.getElementById('uploadStatus');
  status.style.display = 'block';
  status.innerHTML = 'Parsing...';

  try {
    if (typeof XLSX === 'undefined') throw new Error('SheetJS not loaded');
    const data = await file.arrayBuffer();
    const workbook = XLSX.read(data, { type: 'array' });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    let dateStr = '';
    if (rows[1] && rows[1][0] !== undefined) dateStr = String(rows[1][0]).split('-')[0].trim();

    const stores = {};
    const storeOrder = [];
    const colNames = ['总支付金额','美团验券','美团验券笔数','采购','微信支付','微信支付笔数','支付宝','支付宝笔数','现金','现金笔数','京东外卖','京东外卖笔数','美团外卖','美团外卖笔数','淘宝闪购','淘宝闪购笔数','美团验券','美团验券笔数','抖音外卖','抖音外卖笔数'];

    for (let i = 3; i < rows.length; i++) {
      const row = rows[i];
      if (!row || !row[0]) continue;
      const n = String(row[0]).trim();
      if (!n || n === '汇总') continue;
      const sd = {};
      for (let c = 1; c <= 20 && c < row.length; c++) {
        if (colNames[c-1]) { const v = parseFloat(row[c]); sd[colNames[c-1]] = isNaN(v) ? 0 : v; }
      }
      stores[n] = sd; storeOrder.push(n);
    }

    if (storeOrder.length === 0) throw new Error('No data');

    const total = Object.values(stores).reduce((sum, s) => sum + (s['总支付金额']||0), 0);
    status.innerHTML = 'OK! ' + dateStr + ' ' + storeOrder.length + ' stores Y' + total.toFixed(2);

    DATA[dateStr] = stores;
    for (const n of storeOrder) { if (!allStores.find(s => s.name === n)) allStores.push({ name: n }); }
    window.__appInited = false; window.__charts = null; initApp();
  } catch (e) {
    status.innerHTML = 'ERR: ' + e.message;
  }
'''

content = content[:brace_start+1] + new_body + content[brace_end:]
# Update accept attr
content = content.replace('accept=".xls,.xlsx"', 'accept=".xls,.xlsx,.csv"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 20:
        with open(f'_verify{i}.js', 'w', encoding='utf-8') as f:
            f.write(s.strip())

funcs = re.findall(r'function\s+(\w+)', content)
print(f'New size: {len(content)}')
print(f'Functions ({len(funcs)}): {funcs}')
