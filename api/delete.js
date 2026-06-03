import { getAllData, saveAllData, getFileList, saveFileList } from '../server/store.js';

export default async function handler(req, res) {
  if (req.method !== 'DELETE' && req.method !== 'POST') return res.status(405).end();

  const url = new URL(req.url, `https://${req.headers.host}`);
  if (url.searchParams.get('key') !== 'ft2024') {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const body = req.body || {};
    const { date, clearAll } = body;

    if (clearAll) {
      await saveAllData({});
      await saveFileList([]);
      return res.status(200).json({ ok: true, cleared: 'all' });
    }

    if (!date) {
      return res.status(400).json({ error: 'Missing date' });
    }

    const allData = await getAllData();
    delete allData[date];
    await saveAllData(allData);

    const fileList = await getFileList();
    const newFileList = fileList.filter(f => f.date !== date);
    await saveFileList(newFileList);

    res.status(200).json({ ok: true, deleted: date });
  } catch (e) {
    console.error('Delete error:', e);
    res.status(500).json({ error: e.message });
  }
}
