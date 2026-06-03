import { kv } from '@vercel/kv';

const DATA_KEY = 'store:all_data';
const FILES_KEY = 'store:file_list';

// In-memory fallback if KV fails
let memData = {};
let memFiles = [];

export async function getAllData() {
  try {
    const data = await kv.get(DATA_KEY);
    if (data) memData = data;
    return memData;
  } catch (e) {
    console.error('KV getAllData error:', e.message);
    return memData;
  }
}

export async function saveAllData(data) {
  memData = data;
  try {
    await kv.set(DATA_KEY, data);
  } catch (e) {
    console.error('KV saveAllData error:', e.message);
  }
}

export async function getFileList() {
  try {
    const list = await kv.get(FILES_KEY);
    if (list) memFiles = list;
    return memFiles;
  } catch (e) {
    console.error('KV getFileList error:', e.message);
    return memFiles;
  }
}

export async function saveFileList(list) {
  memFiles = list;
  try {
    await kv.set(FILES_KEY, list);
  } catch (e) {
    console.error('KV saveFileList error:', e.message);
  }
}
