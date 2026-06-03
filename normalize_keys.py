with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# The real issue: handleUpload stores data with key '总支付金额'
# But embedded DATA uses key '总支付'
# init() needs to handle BOTH keys

# Find the init function and add a key normalization step
# After "const totals = {};" in init(), add normalization logic

old_init = '''function init() {
  const seen = {};
  for (const dt of dates) {
    for (const name in DATA[dt]) {
      if (!seen[name]) {
        seen[name] = true;
        const totals = {};
        for (const ch of channels) {'''

new_init = '''function init() {
  const seen = {};
  for (const dt of dates) {
    for (const name in DATA[dt]) {
      if (!seen[name]) {
        seen[name] = true;
        const raw = DATA[dt][name];
        // Normalize keys: map '总支付金额' -> '总支付' to match channels array
        const rec = {};
        for (const k in raw) {
          const nk = (k === '总支付金额') ? '总支付' : k;
          rec[nk] = raw[k];
        }
        const totals = {};
        for (const ch of channels) {'''

# Also need to change the reference from DATA[dt][name] to rec
old_ref = "s += (DATA[d][name]||{})[ch]||0;"
new_ref = "s += (DATA[d][name]&&DATA[d][name][ch]) ? DATA[d][name][ch] : ((DATA[d][name]&&DATA[d][name]['总支付金额'])&&ch==='总支付'?DATA[d][name]['总支付金额']:0);"

c = c.replace(old_init, new_init)
c = c.replace(old_ref, new_ref)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify syntax
import re, os
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_norm{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _norm{i}.js 2>&1')
        print(f'Script {i}: {"OK" if r==0 else "FAIL"}')

print('Done - added key normalization')
