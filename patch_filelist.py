import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. CSS：在 </style> 前插入文件列表样式 ──
css_addition = """
/* 文件列表 */
.file-section{background:#fff;border-radius:12px;padding:16px 20px;margin-bottom:16px;box-shadow:0 2px 8px rgba(0,0,0,.06);display:flex;align-items:center;gap:16px;flex-wrap:wrap}
.file-section h3{font-size:14px;color:#333;margin-right:8px;white-space:nowrap}
.file-tag{display:inline-flex;align-items:center;gap:6px;background:#f0f5ff;color:#4472C4;padding:5px 12px;border-radius:20px;font-size:13px}
.file-tag .del{color:#f5222d;cursor:pointer;font-weight:700;margin-left:4px;font-size:15px}
.file-tag .del:hover{color:#c41d3c}
.file-empty{color:#999;font-size:13px}
"""

content = content.replace('</style>', css_addition + '</style>', 1)

# ── 2. HTML：在 mainView 的 header 后、search-bar 前插入文件列表区 ──
html_addition = """
  <div class="file-section" id="fileSection">
    <h3>📂 已上传文件</h3>
    <div id="fileTags"></div>
    <button class="upload-btn" style="padding:6px 14px;font-size:13px" onclick="document.getElementById('fileInput').click()">+ 添加文件</button>
  </div>
"""

# 找 search-bar div，在它前面插入
content = content.replace(
    '<div class="search-bar">',
    html_addition + '\n  <div class="search-bar">',
    1
)

# ── 3. JS：在 const channels 行之前插入 FILE_LIST 和工具函数 ──
js_utils = """

// ═════════════════════════════════════
// 文件列表管理（localStorage 持久化）
// ═════════════════════════════════════
const FILE_STORAGE_KEY = 'ft_dashboard_files';

function loadFileList() {
  try { return JSON.parse(localStorage.getItem(FILE_STORAGE_KEY)) || []; } catch(e) { return []; }
}
function saveFileList(list) {
  localStorage.setItem(FILE_STORAGE_KEY, JSON.stringify(list));
}

// 渲染文件标签
function renderFileList() {
  const el = document.getElementById('fileTags');
  const files = loadFileList();
  if (files.length === 0) {
    el.innerHTML = '<span class="file-empty">暂无文件，请上传 Excel</span>';
    return;
  }
  el.innerHTML = files.map((f,i) =>
    `<span class="file-tag">${esc(f.name)} <span class="del" onclick="removeFile(${i})" title="删除">×</span></span>`
  ).join('');
}

// 删除文件并从 DATA 中移除对应日期
function removeFile(idx) {
  const files = loadFileList();
  if (idx < 0 || idx >= files.length) return;
  const removed = files[idx];
  files.splice(idx, 1);
  saveFileList(files);
  renderFileList();
  // 重建 DATA
  rebuildDataFromFiles(files);
}

// 根据文件列表重建 DATA + allStores + dates
function rebuildDataFromFiles(files) {
  // 清空
  Object.keys(DATA).forEach(k => delete DATA[k]);
  // 逐个解析存储的数据
  for (const f of files) {
    if (f.data) {
      // f.data 是 { 日期: { 门店: {字段:值} } }
      for (const [dt, stores] of Object.entries(f.data)) {
        if (!DATA[dt]) DATA[dt] = {};
        // 同日期：后上传的覆盖先上传的（merge）
        Object.assign(DATA[dt], stores);
      }
    }
  }
  // 重建 dates
  dates.length = 0;
  Object.keys(DATA).sort().forEach(k => dates.push(k));
  window.__appInited = false;
  initApp();
}

// 将解析好的数据存入 localStorage（只存关键数据，不存整个 DATA）
function storeFileData(name, dateStr, storesObj) {
  const files = loadFileList();
  // 避免重复
  if (files.find(f => f.name === name)) return;
  files.push({ name, date: dateStr, data: { [dateStr]: storesObj } });
  saveFileList(files);
  renderFileList();
}
"""

# 插入到 const channels 前面
channels_idx = content.find('const channels')
if channels_idx > -1:
    content = content[:channels_idx] + js_utils + '\n' + content[channels_idx:]

# ── 4. 改 handleUpload：追加模式，存入 localStorage，不清空 DATA ──
old_handleUpload_head = "async function handleUpload(file) {\n  if (!file) return;\n  const st = document.getElementById(\"uploadStatus\");\n  st.style.display = \"block\"; st.innerHTML = \"Parsing...\";\n  try {"
new_handleUpload_head = """async function handleUpload(file) {
  if (!file) return;
  const st = document.getElementById("uploadStatus");
  st.style.display = "block"; st.innerHTML = "Parsing...";
  try {"""

content = content.replace(old_handleUpload_head, new_handleUpload_head, 1)

# 把 handleUpload 里清空 DATA 的那行删掉，改为追加
content = content.replace(
    'Object.keys(DATA).forEach(k=>delete DATA[k]); allStores=[]; DATA[ds]=stores; dates.length=0; Object.keys(DATA).sort().forEach(k=>dates.push(k));',
    '// 追加模式：不清空 DATA，只写入新日期（同日期会覆盖）\n    if (!DATA[ds]) DATA[ds] = {};\n    Object.assign(DATA[ds], stores);\n    dates.length=0; Object.keys(DATA).sort().forEach(k=>dates.push(k));\n    // 存入 localStorage\n    storeFileData(file.name, ds, stores);'
)

# handleUpload 末尾的 allStores.push 也删掉（init() 会重建）
content = content.replace(
    'for(const n of so){if(!allStores.find(s=>s.name===n)) allStores.push({name:n});}\n    window.__appInited=false; window.__charts=null; initApp();',
    'window.__appInited=false; initApp();'
)

# ── 5. 页面加载时：从 localStorage 恢复文件列表 + 重建 DATA ──
# 在 init() 调用前插入恢复逻辑
# 找 "init();" 这一行（在 script 末尾附近）
init_call_idx = content.rfind('init();')
if init_call_idx > -1:
    restore_js = """
  // 从 localStorage 恢复文件列表并重建 DATA
  (function restoreFromStorage() {
    const files = loadFileList();
    renderFileList();
    if (files.length > 0) {
      rebuildDataFromFiles(files);
    } else {
      init();
    }
  })();
  // 不再直接调用 init()，由 restoreFromStorage 决定
"""
    # 替换原来的 init();
    content = content[:init_call_idx] + restore_js + content[init_call_idx + len('init();'):]

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("patch done")
