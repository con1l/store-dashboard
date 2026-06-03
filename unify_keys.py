with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Simpler fix: in handleUpload, just rename the key from 总支付金额 to 总支付
# Find the cn array in handleUpload and change the first element
old_cn = '''const cn=["总支付金额","美团验券","美团验券笔数","采购"'''
new_cn = '''const cn=["总支付","美团验券","美团验券笔数","采购"'''

c = c.replace(old_cn, new_cn)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

import re, os
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_cn{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _cn{i}.js 2>&1')
        print(f'Script {i}: {"OK" if r==0 else "FAIL"}')

# Also verify the normalization code is still there
has_norm = 'Normalize keys' in c or 'nk =' in c or 'normalize' in c.lower()
print(f'Has normalization: {has_norm}')
print('Done - unified all keys to 总支付')
