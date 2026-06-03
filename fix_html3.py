import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 去掉 importmap
content = re.sub(r'<script type="importmap">.*?</script>', '', content, flags=re.DOTALL)

# 在 </body> 前加本地 SheetJS 引用（确保在所有其他script之前）
local_script = '<script src="libs/xlsx.full.min.js"></script>'
if 'libs/xlsx.full.min.js' not in content:
    # 找到第一个 <script 标签前插入
    first_script = content.find('<script')
    content = content[:first_script] + local_script + '\n' + content[first_script:]

# 恢复上传函数为使用全局 XLSX
start = content.find('// ─')
end = content.find('// ═', start + 10)

new_func = '''// ──────────────────────────────────────────────
// 用本地SheetJS解析Excel（支持.xls和.xlsx）
// ──────────────────────────────────────────────
async function handleUpload(file) {
  if (!file) return;
  const status = document.getElementById('uploadStatus');
  status.style.display = 'block';
  status.innerHTML = '⏳ 正在解析文件...';

  try {
    if (typeof XLSX === 'undefined') {
      throw new Error('SheetJS库未加载，请刷新页面重试');
    }

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

    if (storeOrder.length === 0) throw new Error('未找到门店数据');

    const total = Object.values(stores).reduce((sum, s) => sum + (s['总支付金额']||0), 0);
    status.innerHTML = '✅ 解析成功！日期: ' + dateStr + '，' + storeOrder.length + ' 家门店，总金额 ¥' + total.toFixed(2);

    DATA[dateStr] = stores;
    for (const n of storeOrder) { if (!allStores.find(s => s.name === n)) allStores.push({ name: n }); }
    window.__appInited = false; window.__charts = null; initApp();

  } catch (e) {
    status.innerHTML = '❌ 解析失败: ' + e.message;
  }
}'''

content = content[:start] + new_func + content[end:]
content = content.replace('accept=".json,.csv,.tsv,.txt"', 'accept=".xls,.xlsx,.csv"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done:', len(content))
