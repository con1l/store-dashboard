// api/upload.js - Vercel Serverless Function
const XLSX = require('xlsx');

module.exports = async (req, res) => {
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
    // 读取完整请求体
    const chunks = [];
    for await (const chunk of req) {
      chunks.push(chunk);
    }
    const body = Buffer.concat(chunks);
    
    // 解析 multipart
    const boundary = getBoundary(req.headers['content-type']);
    if (!boundary) {
      return res.status(400).json({ error: '无效的请求格式' });
    }
    
    const parts = parseMultipart(body, boundary);
    
    let fileBuffer = null;
    let fileName = '';
    let authToken = '';

    for (const part of parts) {
      if (part.name === 'auth') {
        authToken = part.data.toString().trim();
      } else if (part.name === 'file' && part.filename) {
        fileName = part.filename;
        fileBuffer = part.data;
      }
    }

    console.log('DEBUG auth:', JSON.stringify(authToken), 'file:', fileName);

    if (authToken !== 'ft2024') {
      return res.status(403).json({ error: '密码错误' });
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

function getBoundary(ct) {
  const match = ct && ct.match(/boundary=(?:"([^"]+)"|([^;\s]+))/i);
  return match ? (match[1] || match[2]) : null;
}

function parseMultipart(body, boundary) {
  const results = [];
  const delim = Buffer.from('--' + boundary);
  const endDelim = Buffer.from('--' + boundary + '--');
  
  let pos = 0;
  while (pos < body.length) {
    // 找下一个 delimiter
    let nextIdx = indexOf(body, delim, pos);
    if (nextIdx === -1) break;
    
    // 检查是否结束标记
    const afterDelim = nextIdx + delim.length;
    if (afterDelim + 2 <= body.length && 
        body[afterDelim] === 0x2D && body[afterDelim + 1] === 0x2D) {
      break;
    }
    
    // 跳过 \r\n
    let headerStart = afterDelim;
    if (headerStart < body.length && body[headerStart] === 0x0D) headerStart += 2;
    else if (headerStart < body.length && body[headerStart] === 0x0A) headerStart += 1;
    
    // 找到头部和数据的分隔 (\r\n\r\n)
    const headerEnd = indexOfSeq(body, [0x0D, 0x0A, 0x0D, 0x0A], headerStart);
    if (headerEnd === -1) break;
    
    const headerStr = body.slice(headerStart, headerEnd).toString('latin1');
    const dataStart = headerEnd + 4;
    
    // 解析 Content-Disposition
    const nameMatch = headerStr.match(/name="([^"]+)"/);
    const filenameMatch = headerStr.match(/filename="([^"]+)"/);
    
    // 找到下一个 delimiter 的位置来确定数据长度
    const nextDelim = indexOf(body, delim, dataStart);
    if (nextDelim === -1) break;
    
    // 数据末尾去掉前面的 \r\n
    let dataEnd = nextDelim;
    if (dataEnd > dataStart + 2 && body[dataEnd - 2] === 0x0D && body[dataEnd - 1] === 0x0A) {
      dataEnd -= 2;
    } else if (dataEnd > dataStart && body[dataEnd - 1] === 0x0A) {
      dataEnd -= 1;
    }
    
    results.push({
      name: nameMatch ? nameMatch[1] : null,
      filename: filenameMatch ? filenameMatch[1] : null,
      data: body.slice(dataStart, dataEnd)
    });
    
    pos = nextDelim;
  }
  
  return results;
}

function indexOf(buf, search, start) {
  start = start || 0;
  for (let i = start; i <= buf.length - search.length; i++) {
    let found = true;
    for (let j = 0; j < search.length; j++) {
      if (buf[i + j] !== search[j]) { found = false; break; }
    }
    if (found) return i;
  }
  return -1;
}

function indexOfSeq(buf, seq, start) {
  start = start || 0;
  for (let i = start; i <= buf.length - seq.length; i++) {
    let found = true;
    for (let j = 0; j < seq.length; j++) {
      if (buf[i + j] !== seq[j]) { found = false; break; }
    }
    if (found) return i;
  }
  return -1;
}
