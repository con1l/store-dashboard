import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

checks = {
    'channels 含采购': "'采购'" in c.split('const channels')[1].split(';')[0] if 'const channels' in c else 'N/A',
    'keyCh 含采购': "'采购'" in c.split('const keyCh')[1].split(';')[0] if 'const keyCh' in c else 'N/A',
    'procurementSection 存在': 'procurementSection' in c,
    'procVal JS 已插入': 'procVal' in c,
    'procStats 元素存在': 'procStats' in c,
    'showDetail 有采购渲染': 'procVal' in c.split('function showDetail')[1] if 'function showDetail' in c else 'N/A',
}

with open('__verify.txt', 'w', encoding='utf-8') as f:
    for k, v in checks.items():
        f.write(f'{k}: {v}\n')

print('verify results written to __verify.txt')
