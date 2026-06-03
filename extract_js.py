import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

m = re.search(r'<script>(.*?)</script>', c, re.DOTALL)
if m:
    with open('__check.js', 'w', encoding='utf-8') as f:
        f.write(m.group(1))
    print('extracted to __check.js')
else:
    print('no script tag found')
