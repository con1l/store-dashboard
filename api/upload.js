import { getAllData, saveAllData, getFileList, saveFileList } from '../server/store.js';

export const config = { api: { bodyParser: { sizeLimit: '10mb' } } };

export default async function handler(req, res) {
  if (req.method !== 'POST') return res.status(405).end();

  const url = new URL(req.url, `https://${req.headers.host}`);
  if (url.searchParams.get('key') !== 'ft2024') {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const { storeData, fileDate, fileName } = req.body;
    
    if (!storeData || !fileDate) {
      return res.status(400).json({ error: 'Missing storeData or fileDate' });
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
    const safeName = (fileName || 'data.xlsx').replace(/[^a-zA-Z0-9._-]/g, '_');
    if (fileDate && !fileList.find(f => f.date === fileDate)) {
      fileList.push({ name: safeName, date: fileDate });
      await saveFileList(fileList);
    }

    const storeCount = storeData[fileDate] ? Object.keys(storeData[fileDate]).length : 0;
    res.status(200).json({ ok: true, date: fileDate, stores: storeCount });
  } catch (e) {
    console.error('Upload error:', e);
    res.status(500).json({ error: e.message });
  }
}
