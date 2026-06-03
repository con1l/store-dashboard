import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'fs';
import { join } from 'path';
import { mkdir } from 'fs/promises';

const DATA_DIR = join(process.cwd(), 'data');

// 确保 data 目录存在
async function ensureDataDir() {
  try {
    await mkdir(DATA_DIR, { recursive: true });
  } catch (e) {}
}

export async function getAllData() {
  await ensureDataDir();
  const file = join(DATA_DIR, 'stores.json');
  if (!existsSync(file)) return {};
  try {
    return JSON.parse(readFileSync(file, 'utf-8'));
  } catch { return {}; }
}

export async function saveAllData(data) {
  await ensureDataDir();
  const file = join(DATA_DIR, 'stores.json');
  writeFileSync(file, JSON.stringify(data, null, 2), 'utf-8');
}

export async function getFileList() {
  await ensureDataDir();
  const file = join(DATA_DIR, 'files.json');
  if (!existsSync(file)) return [];
  try { return JSON.parse(readFileSync(file, 'utf-8')); } catch { return []; }
}

export async function saveFileList(list) {
  await ensureDataDir();
  const file = join(DATA_DIR, 'files.json');
  writeFileSync(file, JSON.stringify(list, null, 2), 'utf-8');
}