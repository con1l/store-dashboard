import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 去掉所有外部Excel库CDN
content = content.replace(
    '<script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>',
    ''
)

# 找到上传函数区域
start = content.find('// ─')
end = content.find('// ═', start + 10)

new_func = '''// ──────────────────────────────────────────────
// 支持JSON和CSV上传（100%可靠，无需外部库）
// ──────────────────────────────────────────────
async function handleUpload(file) {
  if (!file) return;
  const status = document.getElementById('uploadStatus');
  status.style.display = 'block';
  status.innerHTML = '⏳ 正在解析文件...';

  try {
    const name = file.name.toLowerCase();
    let rows = [];

    if (name.endsWith('.json')) {
      const text = await file.text();
      const json = JSON.parse(text);
      if (json.data && json.date) {
        DATA[json.date] = json.data;
        for (const n of (json.store_order || Object.keys(json.data))) {
          if (!allStores.find(s => s.name === n)) allStores.push({ name: n });
        }
        const total = Object.values(json.data).reduce((sum, s) => sum + (s['总支付金额']||0), 0);
        status.innerHTML = '✅ 导入成功！日期: ' + json.date + '，' + Object.keys(json.data).length + ' 家门店，总金额 ¥' + total.toFixed(2);
        window.__appInited = false; window.__charts = null; initApp();
        return;
      }
      throw new Error('JSON格式不正确');
    }
    else if (name.endsWith('.csv') || name.endsWith('.tsv') || name.endsWith('.txt')) {
      const text = await file.text();
      const lines = text.split(/\\r?\\n/).filter(l => l.trim());
      const sep = text.includes('\\t') ? '\\t' : ',';
      rows = lines.map(line => line.split(sep).map(cell => {
        cell = cell.trim().replace(/^"|"$/g, '');
        const num = parseFloat(cell);
        return isNaN(num) ? cell : num;
      }));
    }
    else {
      throw new Error('请上传 .json 或 .csv 文件');
    }

    if (rows.length < 4) throw new Error('文件数据不足');

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
    status.innerHTML = '❌ ' + e.message;
  }
}'''

content = content[:start] + new_func + content[end:]
content = content.replace('accept=".xls,.xlsx"', 'accept=".json,.csv,.tsv,.txt"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print('Done:', len(content))
