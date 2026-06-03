import { getAllData, getFileList } from '../server/store.js';

export default async function handler(req, res) {
  if (req.method !== 'GET') return res.status(405).end();

  const url = new URL(req.url, `https://${req.headers.host}`);
  if (url.searchParams.get('key') !== 'ft2024') {
    return res.status(401).json({ error: 'Unauthorized' });
  }

  try {
    const allData = await getAllData();
    const fileList = await getFileList();
    res.status(200).json({ data: allData, files: fileList });
  } catch (e) {
    res.status(500).json({ error: e.message });
  }
}