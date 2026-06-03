import subprocess, re, os

result = subprocess.run(['git', 'show', '205a607:index.html'], capture_output=True)
raw = result.stdout
if raw[:2] == b'\xff\xfe':
    content = raw.decode('utf-16')
elif raw[:3] == b'\xef\xbb\xbf':
    content = raw.decode('utf-8-sig')
else:
    content = raw.decode('utf-8')

print(f'Original: {len(content)} chars')

# === ALL CHANGES IN ONE PASS ===

# 1. Add SheetJS <script> tag
content = content.replace(
    '<script>',
    '<script src="libs/xlsx.full.min.js"></script>\n<script>',
    1
)

# 2. Replace handleUpload + Fix IIFE in one operation
# Find the region from "async function handleUpload" to end of IIFE "})();"
hu_start = content.find('async function handleUpload(file) {')
iife_end_marker = '\n})();\n'
iife_end_pos = content.find(iife_end_marker, hu_start)
# iife ends at the } before )();
actual_iife_end = content.rfind('}', hu_start, iife_end_pos) + 1
region_end = iife_end_pos + len(iife_end_marker)  # include });()

print(f'Replacing region: {hu_start} to {region_end} ({region_end-hu_start} chars)')

new_region = '''async function handleUpload(file) {
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
    const cn=["总支付金额","美团验券","美团验券笔数","采购","微信支付","微信支付笔数","支付宝","支付宝笔号","现金","现金笔数","京东外卖","京东外卖笔数","美团外卖","美团外卖笔数","淘宝闪购","淘宝闪购笔数","美团验券","美团验券笔数","抖音外卖","抖音外卖笔数"];
    for(let i=3;i<rows.length;i++){const r=rows[i];if(!r||!r[0])continue;const n=String(r[0]).trim();if(!n||n==="汇总")continue;const sd={};for(let c=1;c<=20&&c<r.length;c++){if(cn[c-1]){const v=parseFloat(r[c]);sd[cn[c-1]]=isNaN(v)?0:v;}}stores[n]=sd;so.push(n);}
    if(so.length===0) throw new Error("No data");
    const tot=Object.values(stores).reduce((s,x)=>s+(x["总支付金额"]||0),0);
    st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);
    DATA[ds]=stores;
    for(const n of so){if(!allStores.find(s=>s.name===n)) allStores.push({name:n});}
    window.__appInited=false; window.__charts=null; initApp();
  } catch(e) { st.innerHTML="ERR: "+e.message; }
  }

function init() {
  const seen = {};
  for (const dt of dates) {
    for (const name in DATA[dt]) {
      if (!seen[name]) {
        seen[name] = true;
        const totals = {};
        for (const ch of channels) {
          let s = 0;
          for (const d of dates) { s += (DATA[d][name]||{})[ch]||0; }
          totals[ch] = Math.round(s*100)/100;
        }
        allStores.push({name, totals});
      }
    }
  }
  allStores.sort((a,b)=>b.totals['总支付']-a.totals['总支付']);
  
  document.getElementById('sStores').textContent = allStores.length;
  document.getElementById('sDates').textContent = dates.length;
  const grand = allStores.reduce((a,b)=>a+b.totals['总支付'],0);
  document.getElementById('sTotal').textContent = '¥'+(grand/10000).toFixed(1)+'万';
  
  renderTopCards();
  renderOverviewCharts();
  renderDailyTable();
  renderStoreList();
}
init();

'''

content = content[:hu_start] + new_region + content[region_end:]

# 3. accept attr
content = content.replace('accept=".xls,.xlsx"', 'accept=".xls,.xlsx,.csv"')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_ok{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _ok{i}.js 2>&1')
        print(f'Script {i} ({len(s)} chars): {"OK" if r==0 else "FAIL"}')

funcs = re.findall(r'function\s+(\w+)', content)
print(f'Total: {len(content)}, funcs: {funcs}')

# Verify the fix
assert '(function init()' not in content, 'IIFE should be gone!'
assert 'function init()' in content, 'init() declaration should exist!'
assert content.count('init();') >= 2, 'Should have init() calls'
print('All assertions passed!')
