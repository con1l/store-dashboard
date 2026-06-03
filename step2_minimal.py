import re, os

with open('_orig_full.html', 'r', encoding='utf-8') as f:
    content = f.read()

# CHANGE 1: Add SheetJS <script> tag before first <script
insert = '<script src="libs/xlsx.full.min.js"></script>\n'
first = content.find('<script')
content = content[:first] + insert + content[first:]
print(f'After add SheetJS: {len(content)} chars')

# CHANGE 2: Replace handleUpload body
start = content.find('async function handleUpload(file) {')
bs = content.find('{', start)
depth = 0; pos = bs
while pos < len(content):
    if content[pos] == '{': depth += 1
    elif content[pos] == '}':
        depth -= 1
        if depth == 0: break
    pos += 1

old_body = content[bs+1:pos]
print(f'Old handleUpload body: {len(old_body)} chars')

new_body = """
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
    const cn=["总支付金额","美团验券","美团验券笔数","采购","微信支付","微信支付笔数","支付宝","支付宝笔数","现金","现金笔数","京东外卖","京东外卖笔数","美团外卖","美团外卖笔数","淘宝闪购","淘宝闪购笔数","美团验券","美团验券笔数","抖音外卖","抖音外卖笔数"];
    for(let i=3;i<rows.length;i++){const r=rows[i];if(!r||!r[0])continue;const n=String(r[0]).trim();if(!n||n==="汇总")continue;const sd={};for(let c=1;c<=20&&c<r.length;c++){if(cn[c-1]){const v=parseFloat(r[c]);sd[cn[c-1]]=isNaN(v)?0:v;}}stores[n]=sd;so.push(n);}
    if(so.length===0) throw new Error("No data");
    const tot=Object.values(stores).reduce((s,x)=>s+(x["总支付金额"]||0),0);
    st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);
    DATA[ds]=stores;
    for(const n of so){if(!allStores.find(s=>s.name===n)) allStores.push({name:n});}
    window.__appInited=false; window.__charts=null; initApp();
  } catch(e) { st.innerHTML="ERR: "+e.message; }
"""

content = content[:bs+1] + new_body + content[pos+1:]

# CHANGE 3: accept attr
content = content.replace('accept=".xls,.xlsx"', 'accept=".xls,.xlsx,.csv"')

# DO NOT touch the IIFE or init() at all!

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify syntax
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_test{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())

funcs = re.findall(r'function\s+(\w+)', content)
print(f'Result: {len(content)} chars, funcs: {funcs}')
os.system('node --check _test2.js 2>&1')

# Check: is the IIFE still intact?
has_iife = '(function init()' in content
has_init_call = 'init();' in content
print(f'IIFE intact: {has_iife}, init() call exists: {has_init_call}')
