with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# === Strategy: Add FIELD_MAP + normalizeRow, use in handleUpload ===
# Insert FIELD_MAP and normalizeRow right before handleUpload
hu_start = c.find('async function handleUpload(file) {')

field_map_code = '''// Field name normalization - supports aliases from different Excel formats
const FIELD_MAP = {
  '总支付': ['总支付', '总支付金额', '支付总额', '总收款', '支付金额'],
  '美团验券': ['美团验券', '美团验券金额'],
  '美团验券笔数': ['美团验券笔数'],
  '采购': ['采购', '采购金额'],
  '微信支付': ['微信支付', '微信支付金额'],
  '微信支付笔数': ['微信支付笔数'],
  '支付宝': ['支付宝', '支付宝金额'],
  '支付宝笔号': ['支付宝笔号', '支付宝笔数'],
  '现金': ['现金', '现金金额'],
  '现金笔数': ['现金笔数'],
  '京东外卖': ['京东外卖', '京东外卖金额'],
  '京东外卖笔数': ['京东外卖笔数'],
  '美团外卖': ['美团外卖', '美团外卖金额'],
  '美团外卖笔数': ['美团外卖笔数'],
  '淘宝闪购': ['淘宝闪购', '淘宝闪购金额'],
  '淘宝闪购笔数': ['淘宝闪购笔数'],
  '抖音外卖': ['抖音外卖', '抖音外卖金额'],
  '抖音外卖笔数': ['抖音外卖笔数']
};

function normalizeStoreKeys(storeData) {
  const normalized = {};
  for (const [standardKey, aliases] of Object.entries(FIELD_MAP)) {
    for (const alias of aliases) {
      if (storeData[alias] !== undefined) {
        normalized[standardKey] = storeData[alias];
        break;
      }
    }
    if (normalized[standardKey] === undefined) {
      normalized[standardKey] = 0;
    }
  }
  return normalized;
}

'''

c = c[:hu_start] + field_map_code + c[hu_start:]

# Now replace handleUpload to use normalizeStoreKeys
old_hu = '''async function handleUpload(file) {
  if (!file) return;
  const st = document.getElementById("uploadStatus");
  st.style.display = "block"; st.innerHTML = "Parsing...";
  try {
    if (typeof XLSX === "undefined") throw new Error("No SheetJS");
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, {type:"array"});
    const ws = wb.Sheets[wb.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(ws, {header:1});
    let ds = ""; if (rows[1]&&rows[1][0]!==undefined) ds=String(rows[1][0]).split("-")[0].trim();
    const stores={}; const so=[];
    const cn=["总支付","美团验券","美团验券笔数","采购","微信支付","微信支付笔数","支付宝","支付宝笔号","现金","现金笔数","京东外卖","京东外卖笔数","美团外卖","美团外卖笔数","淘宝闪购","淘宝闪购笔数","美团验券","美团验券笔数","抖音外卖","抖音外卖笔数"];
    for(let i=3;i<rows.length;i++){const r=rows[i];if(!r||!r[0])continue;const n=String(r[0]).trim();if(!n||n==="汇总")continue;const sd={};for(let c=1;c<=20&&c<r.length;c++){if(cn[c-1]){const v=parseFloat(r[c]);sd[cn[c-1]]=isNaN(v)?0:v;}}stores[n]=sd;so.push(n);}
    if(so.length===0) throw new Error("No data");
    const tot=Object.values(stores).reduce((s,x)=>s+(x["总支付"]||0),0);
    st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);
    DATA[ds]=stores;
    for(const n of so){if(!allStores.find(s=>s.name===n)) allStores.push({name:n});}
    window.__appInited=false; window.__charts=null; initApp();
  } catch(e) { st.innerHTML="ERR: "+e.message; }
  }'''

new_hu = '''async function handleUpload(file) {
  if (!file) return;
  const st = document.getElementById("uploadStatus");
  st.style.display = "block"; st.innerHTML = "Parsing...";
  try {
    if (typeof XLSX === "undefined") throw new Error("No SheetJS");
    const data = await file.arrayBuffer();
    const wb = XLSX.read(data, {type:"array"});
    const ws = wb.Sheets[wb.SheetNames[0]];
    const rows = XLSX.utils.sheet_to_json(ws, {header:1});
    let ds = ""; if (rows[1]&&rows[1][0]!==undefined) ds=String(rows[1][0]).split("-")[0].trim();
    // Read header row (row index 2, 0-based: row 3 visually)
    const headerRow = rows[2] || [];
    const stores={}; const so=[];
    for(let i=3;i<rows.length;i++){const r=rows[i];if(!r||!r[0])continue;const n=String(r[0]).trim();if(!n||n==="汇总")continue;
      // Build raw store data from column positions using headers
      const raw={};
      for(let col=1;col<headerRow.length&&col<r.length;col++){
        const h=String(headerRow[col]).trim();
        if(h){const v=parseFloat(r[col]);raw[h]=isNaN(v)?0:v;}
      }
      // Normalize keys so all data uses standard field names
      stores[n]=normalizeStoreKeys(raw);
      so.push(n);
    }
    if(so.length===0) throw new Error("No data");
    const tot=Object.values(stores).reduce((s,x)=>s+(x["总支付"]||0),0);
    st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);
    DATA[ds]=stores;
    for(const n of so){if(!allStores.find(s=>s.name===n)) allStores.push({name:n});}
    window.__appInited=false; window.__charts=null; initApp();
  } catch(e) { st.innerHTML="ERR: "+e.message; }
  }'''

c = c.replace(old_hu, new_hu)

# Also clean up init() - remove the normalization code we added earlier if present
# The old normalize code used 'nk' variable
old_norm = '''        // Normalize keys: map '总支付金额' -> '总支付' to match channels array
        const rec = {};
        for (const k in raw) {
          const nk = (k === '总支付金额') ? '总支付' : k;
          rec[nk] = raw[k];
        }
        const totals = {};'''
new_simple = '''        const totals = {};'''
c = c.replace(old_norm, new_simple)

# Also fix the complex reference line we added
old_ref2 = "s += (DATA[d][name]&&DATA[d][name][ch]) ? DATA[d][name][ch] : ((DATA[d][name]&&DATA[d][name]['总支付金额'])&&ch==='总支付'?DATA[d][name]['总支付金额']:0);"
new_ref2 = "s += (DATA[d][name]||{})[ch]||0;"
c = c.replace(old_ref2, new_ref2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify syntax
import re, os
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_final{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _final{i}.js 2>&1')
        print(f'Script {i} ({len(s)} chars): {"OK" if r==0 else "FAIL"}')

funcs = re.findall(r'function\s+(\w+)', c)
print(f'Funcs: {funcs}')
print(f'Size: {len(c)}')
print(f'Has FIELD_MAP: {"FIELD_MAP" in c}')
print(f'Has normalizeStoreKeys: {"normalizeStoreKeys" in c}')
