import subprocess, re

result = subprocess.run(['git', 'show', '205a607:index.html'], capture_output=True)
raw = result.stdout
if raw[:2] == b'\xff\xfe':
    content = raw.decode('utf-16')
elif raw[:3] == b'\xef\xbb\xbf':
    content = raw.decode('utf-8-sig')
else:
    content = raw.decode('utf-8')

# 1. Add local SheetJS reference before first <script
local_script = '<script src="libs/xlsx.full.min.js"></script>'
first_script_pos = content.find('<script')
content = content[:first_script_pos] + local_script + '\n' + content[first_script_pos:]

# 2. Replace handleUpload only - use 'function init()' as end marker (no leading newline)
start = content.find('async function handleUpload')
end = content.find('function init()', start)  # this is the NEXT function after handleUpload

new_func = '''async function handleUpload(file) {
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

    if (storeOrder.length === 0) throw new Error('No store data found');

    const total = Object.values(stores).reduce((sum, s) => sum + (s['总支付金额']||0), 0);
    status.innerHTML = 'OK! Date:' + dateStr + ' Stores:' + storeOrder.length + ' Total:Y' + total.toFixed(2);

    DATA[dateStr] = stores;
    for (const n of storeOrder) { if (!allStores.find(s => s.name === n)) allStores.push({ name: n }); }
    window.__appInited = false; window.__charts = null; initApp();

  } catch (e) {
    status.innerHTML = 'ERROR: ' + e.message;
  }
}

'''

content = content[:start] + new_func + content[end:]
content = content.replace('accept=".xls,.xlsx"', 'accept=".xls,.xlsx,.csv"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

funcs = re.findall(r'function\s+(\w+)', content)
print(f'Done! Size: {len(content)}')
print(f'Functions ({len(funcs)}): {funcs}')
