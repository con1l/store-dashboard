with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
idx = c.find('function init()')
end = c.find('\ninit();', idx)
# Write to file to avoid console encoding issues
with open('_init_dump.txt', 'w', encoding='utf-8') as out:
    out.write(c[idx:end+10])
print(f'Written init() to _init_dump.txt, chars: {end-idx}')
