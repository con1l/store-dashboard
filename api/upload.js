// api/upload.js - Vercel Serverless Function
// 后端用xlsx库解析Excel文件，前端只负责传文件

export const config = { runtime: 'nodejs20' };

// 动态导入xlsx（Vercel会从package.json安装）
let XLSX;
async function getXLSX() {
  if (!XLSX) {
    XLSX = (await import('xlsx')).default;
  }
  return XLSX;
}

export default async function handler(req, res) {
  // CORS
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: '只支持POST' });
  }

  try {
    // 解析multipart form data
    const chunks = [];
    const buf = await new Promise((resolve, reject) => {
      req.on('data', c => chunks.push(c));
      req.on('end', () => resolve(Buffer.concat(chunks)));
      req.on('error', reject);
    });

    // 简单解析multipart boundary
    const boundary = req.headers['content-type'].split('boundary=')[1];
    if (!boundary) {
      return res.status(400).json({ error: '缺少boundary' });
    }

    const parts = buf.toString('binary').split('--' + boundary);
    let authToken = '';
    let fileData = null;
    let fileName = '';

    for (const part of parts) {
      if (!part || part.trim() === '' || part === '--') continue;
      
      const headerEnd = part.indexOf('\r\n\r\n');
      if (headerEnd < 0) continue;
      
      const header = part.substring(0, headerEnd);
      const body = part.substring(headerEnd + 4);
      
      if (header.includes('name="auth"')) {
        authToken = body.replace(/\r\n/g, '').trim();
      }
      if (header.includes('name="file"') && header.includes('filename=')) {
        const match = header.match(/filename="(.+?)"/);
        if (match) fileName = match[1];
        fileData = Buffer.from(body, 'binary');
      }
    }

    if (authToken !== 'ft2024') {
      return res.status(403).json({ error: '密码错误' });
    }

    if (!fileData || fileData.length === 0) {
      return res.status(400).json({ error: '没有收到文件' });
    }

    // 用xlsx库解析
    const xlsx = await getXLSX();
    const workbook = xlsx.read(fileData, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const rows = xlsx.utils.sheet_to_json(sheet, { header: 1 });

    // 提取日期
    let dateStr = '';
    if (rows[1] && rows[1][0]) {
      dateStr = String(rows[1][0]).split('-')[0].trim();
    }

    // 解析门店数据
    const stores = {};
    const storeOrder = [];
    const colNames = ['总支付金额','美团验券','美团验券笔数','采购','微信支付','微信支付笔数','支付宝','支付宝笔数','现金','现金笔数','京东外卖','京东外卖笔数','美团外卖','美团外卖笔数','淘宝闪购','淘宝闪购笔数','美团验券','美团验券笔数','抖音外卖','抖音外卖笔数'];

    for (let i = 3; i < rows.length; i++) {
      const row = rows[i];
      if (!row || !row[0]) continue;
      const name = String(row[0]).trim();
      if (!name || name === '汇总') continue;
      const storeData = {};
      for (let c = 1; c <= 20 && c < row.length; c++) {
        if (colNames[c-1]) storeData[colNames[c-1]] = typeof row[c] === 'number' ? row[c] : 0;
      }
      stores[name] = storeData;
      storeOrder.push(name);
    }

    if (storeOrder.length === 0) {
      return res.status(400).json({ error: '未找到门店数据' });
    }

    const total = Object.values(stores).reduce((sum, s) => sum + (s['总支付金额'] || 0), 0);

    return res.status(200).json({
      ok: true,
      date: dateStr,
      store_count: storeOrder.length,
      store_order: storeOrder,
      data: stores,
      total: total
    });

  } catch (err) {
    console.error('Upload error:', err);
    return res.status(500).json({ error: '处理失败: ' + err.message });
  }
}
