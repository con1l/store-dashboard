with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# 1. Guard init() against undefined totals
c = c.replace(
    "allStores.sort((a,b)=>b.totals['总支付']-a.totals['总支付']);",
    "allStores.sort((a,b)=>(b.totals['总支付']||0)-(a.totals['总支付']||0));"
)
c = c.replace(
    "const grand = allStores.reduce((a,b)=>a+b.totals['总支付'],0);",
    "const grand = allStores.reduce((a,b)=>a+(b.totals['总支付']||0),0);"
)

# 2. Add debug logging in handleUpload
old_ok = 'st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);'
new_ok = '''st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);
    const _dbg = so[0] ? stores[so[0]] : null;
    if(_dbg) console.log("STORE_KEYS:", Object.keys(_dbg), "VAL_总支付:", _dbg["总支付"], "VAL_总金额:", _dbg["总支付金额"]);'''
c = c.replace(old_ok, new_ok)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

import re, os
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_d{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _d{i}.js 2>&1')
        print(f'Script {i}: {"OK" if r==0 else "FAIL"}')
print('Done')
