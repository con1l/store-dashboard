with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix: '总支付' -> '总支付金额' in totals references
c = c.replace("totals['总支付']", "totals['总支付金额']")
c = c.replace("totals[\"总支付\"]", "totals[\"总支付金额\"]")

# Check for remaining standalone '总支付' (not followed by 金额)
import re
remaining = []
for m in re.finditer('总支付', c):
    if c[m.end():m.end()+2] != '金额':
        start = max(0, m.start()-15)
        end = min(len(c), m.end()+15)
        ctx = c[start:end]
        remaining.append(f'  pos {m.start()}: ...{ctx}...')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

if remaining:
    print(f'Remaining occurrences:')
    for r in remaining:
        print(r)
else:
    print('All fixed - no remaining standalone 总支付')
