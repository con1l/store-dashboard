import { kv } from '@vercel/kv';

const DATA_KEY = 'store:all_data';
const FILES_KEY = 'store:file_list';

export async function getAllData() {
  const data = await kv.get(DATA_KEY);
  return data || {};
}

export async function saveAllData(data) {
  await kv.set(DATA_KEY, data);
}

export async function getFileList() {
  const list = await kv.get(FILES_KEY);
  return list || [];
}

export async function saveFileList(list) {
  await kv.set(FILES_KEY, list);
}