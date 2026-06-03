// api/upload.js - Vercel Serverless Function
const XLSX = require('xlsx');

module.exports = async (req, res) => {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST,OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type, x-vercel-fallback');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: '只支持POST' });
  }

  try {
    const contentType = req.headers['content-type'] || '';
    const boundary = contentType.split('boundary=')[1];
    if (!boundary) {
      return res.status(400).json({ error: '无效的请求格式' });
    }

    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const body = Buffer.concat(chunks);
    
    const parts = body.toString('latin1').split('--' + boundary);
    
    let fileBuffer = null;
    let fileName = '';
    let authToken = '';

    for (const part of parts) {
      if (part.startsWith('--') || !part.includes('Content-Disposition')) continue;
      
      const isAuth = part.includes('name="auth"');
      const isFile = part.includes('name="file"');
      const nameMatch = part.match(/filename="([^"]+)"/);
      
      if (isAuth) {
        const authMatch = part.match(/\r\n\r\n([\s\S]*?)\r\n--/);
        if (authMatch) authToken = authMatch[1].trim();
      } else if (isFile && nameMatch) {
        fileName = nameMatch[1];
        const dataStart = part.indexOf('\r\n\r\n') + 4;
        const dataEnd = part.lastIndexOf('\r\n');
        const fileData = part.substring(dataStart, dataEnd);
        fileBuffer = Buffer.from(fileData, 'latin1');
      }
    }

    // 临时调试：打印收到的auth值
    console.log('DEBUG auth token:', JSON.stringify(authToken));
    if (authToken !== 'ft2024') {
      return res.status(403).json({ error: '密码错误 [debug:' + authToken + ']' });
    }
    if (!fileBuffer) {
      return res.status(400).json({ error: '没有文件' });
    }
    if (!fileName.match(/\.(xls|xlsx)$/i)) {
      return res.status(400).json({ error: '只支持.xls/.xlsx文件' });
    }

    const workbook = XLSX.read(fileBuffer, { type: 'buffer' });
    const sheetName = workbook.SheetNames[0];
    const sheet = workbook.Sheets[sheetName];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1 });

    let dateStr = '';
    if (rows[1] && rows[1][0]) {
      const rawDate = String(rows[1][0]);
      dateStr = rawDate.split('-')[0].trim();
      if (!isNaN(Number(rawDate)) && Number(rawDate) > 40000) {
        const d = new Date((Number(rawDate) - 25569) * 86400 * 1000);
        dateStr = `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`;
      }
    }

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

    return res.json({
      ok: true,
      date: dateStr,
      store_count: Object.keys(stores).length,
      store_order: storeOrder,
      data: stores,
      total: Object.values(stores).reduce((sum, s) => sum + (s['总支付金额'] || 0), 0)
    });

  } catch (err) {
    console.error('Upload error:', err);
    return res.status(500).json({ error: '解析失败: ' + err.message });
  }
};
