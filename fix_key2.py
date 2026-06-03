with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# The embedded DATA uses '总支付' key, but channels array uses '总支付金额'
# Fix: in init(), when building totals, use the same key that DATA uses
# Strategy: make init() reference '总支付' (matching the data) instead of '总支付金额'

# First, revert the earlier fix (totals['总支付金额'] back to totals['总支付'])
# because the DATA object actually stores it as '总支付'
c = c.replace("totals['总支付金额']", "totals['总支付']")
c = c.replace('totals["总支付金额"]', 'totals["总支付"]')

# Now fix the grand total line too
c = c.replace("b.totals['总支付金额']", "b.totals['总支付']")
c = c.replace('b.totals["总支付金额"]', 'b.totals["总支付"]')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify syntax
import re, os
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 100:
        with open(f'_vk{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())
        r = os.system(f'node --check _vk{i}.js 2>&1')
        print(f'Script {i}: {"OK" if r==0 else "FAIL"}')

print('Done - using 总支付 to match DATA keys')
