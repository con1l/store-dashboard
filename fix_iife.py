import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Fix 1: (function init() { -> function init() {
c = c.replace('(function init() {', 'function init() {')

# Fix 2: Remove trailing })();
idx = c.find('})();')
print('Found })(); at:', idx)
if idx >= 0:
    c = c[:idx] + c[idx+5:]
    print('Removed });')

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

# Verify
scripts = re.findall(r'<script[^>]*>(.*?)</script>', c, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) > 20:
        with open(f'_vf{i}.js', 'w', encoding='utf-8') as out:
            out.write(s.strip())

funcs = re.findall(r'function\s+(\w+)', c)
print(f'Functions: {funcs}')
print(f'Has (function init(): {(\"(function init()\" in c)}')
print(f'Has function init(): {(\"function init()\" in c)}')
