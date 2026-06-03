with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Add safety: in init(), guard against undefined keys
old_sort = "allStores.sort((a,b)=>b.totals['总支付']-a.totals['总支付']);"
new_sort = """allStores.sort((a,b)=>(b.totals['总支付']||0)-(a.totals['总支付']||0));"""

c = c.replace(old_sort, new_sort)

old_grand = "const grand = allStores.reduce((a,b)=>a+b.totals['总支付'],0);"
new_grand = """const grand = allStores.reduce((a,b)=>a+(b.totals['总支付']||0),0);"""
c = c.replace(old_grand, new_grand)

# Also guard the totals[ch] access in init()
old_s = 's += (DATA[d][name]||{})[ch]||0;'
# This should already be safe with ||{}
# But let's also add debug info to handleUpload to see what's happening

# Add console.log to handleUpload to debug
old_st_ok = 'st.innerHTML="OK! '+ds+' "+so.length+"st Y"+tot.toFixed(2);'
new_st_ok = '''st.innerHTML="OK! "+ds+" "+so.length+"st Y"+tot.toFixed(2);
    // DEBUG: log first store's keys
    const firstStore = so[0];
    if(firstStore && stores[firstStore]) {
      console.log("DEBUG first store keys:", Object.keys(stores[firstStore]));
      console.log("DEBUG has 总支付:", stores[firstStore]["总支付"]);
      console.log("DEBUG has 总支付金额:", stores[firstStore]["总支付金额"]);
    }'''
c = c.replace(old_st_ok, new_st_ok)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

import re, os
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_dbg{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _dbg{i}.js 2>&1')
        print(f'Script {i}: {"OK" if r==0 else "FAIL"}')

print('Done - added safety guards + debug logs')
