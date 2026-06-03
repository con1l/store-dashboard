import { getAllData, saveAllData, getFileList, saveFileList } from '../server/store.js';

let XLSX;
try {
  XLSX = await import('xlsx');
} catch (e) {
  console.error('XLSX import failed:', e.message);
}

export const config = { api: { bodyParser: false } };

function readBody(req) {
  return new Promise((resolve, reject) => {
    const chunks = [];
    req.on('data', chunk => chunks.push(chunk));
    req.on('end', () => resolve(Buffer.concat(chunks)));
    req.on('error', reject);
  });
}

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const url = new URL(req.url, `https://${req.headers.host}`);
  if (url.searchParams.get('key') !== 'ft2024') {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  if (!XLSX) {
    return res.status(500).json({ error: 'XLSX library not loaded' });
  }

  try {
    const buf = await readBody(req);
    const wb = XLSX.read(buf, { type: 'buffer' });

    const sheet = wb.Sheets[wb.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(sheet, { header: 1, defval: '' });

    if (rows.length < 3) return res.status(400).json({ error: 'Invalid format' });

    const headers = rows[0].map(h => String(h).trim());
    const storeData = {};
    let fileDate = '';

    const dateIdx = headers.findIndex(h => h.includes('日期'));
    if (dateIdx !== -1) {
      const rawDate = rows[2][dateIdx];
      if (rawDate) {
        const d = new Date(rawDate);
        if (!isNaN(d)) {
          fileDate = `${d.getFullYear()}/${String(d.getMonth()+1).padStart(2,'0')}/${String(d.getDate()).padStart(2,'0')}`;
        }
      }
    }

    const chMap = {
      '总支付金额': '总支付',
      '总支付': '总支付',
      '美团外卖': '美团外卖',
      '抖音验券': '抖音验券',
      '微信支付': '微信支付',
      '支付宝': '支付宝',
      '采购': '采购'
    };

    for (let i = 2; i < rows.length; i++) {
      const row = rows[i];
      if (!row.length) continue;
      const name = String(row[headers.findIndex(h => h.includes('门店'))] || '').trim();
      if (!name || name === 'undefined' || name === 'NaN') continue;
      if (!storeData[fileDate]) storeData[fileDate] = {};
      if (!storeData[fileDate][name]) storeData[fileDate][name] = { 总支付: 0, 美团外卖: 0, 抖音验券: 0, 微信支付: 0, 支付宝: 0, 采购: 0 };
      for (const [src, tgt] of Object.entries(chMap)) {
        const idx = headers.indexOf(src);
        if (idx !== -1) {
          const v = parseFloat(row[idx]);
          if (!isNaN(v)) storeData[fileDate][name][tgt] += v;
        }
      }
    }

    const allData = await getAllData();
    for (const [ds, stores] of Object.entries(storeData)) {
      if (!allData[ds]) allData[ds] = {};
      for (const [name, vals] of Object.entries(stores)) {
        allData[ds][name] = { ...(allData[ds][name] || {}), ...vals };
      }
    }
    await saveAllData(allData);

    const fileList = await getFileList();
    const fileName = (req.headers['x-filename'] || 'data.xlsx').replace(/[^a-zA-Z0-9._-]/g, '_');
    if (fileDate && !fileList.find(f => f.date === fileDate)) {
      fileList.push({ name: fileName, date: fileDate });
      await saveFileList(fileList);
    }

    res.status(200).json({ ok: true, date: fileDate, stores: Object.keys(storeData[fileDate] || {}).length });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}