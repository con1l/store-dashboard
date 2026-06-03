import subprocess, re

# Get original file
result = subprocess.run(['git', 'show', '205a607:index.html'], capture_output=True)
raw = result.stdout
if raw[:2] == b'\xff\xfe':
    content = raw.decode('utf-16')
elif raw[:3] == b'\xef\xbb\xbf':
    content = raw.decode('utf-8-sig')
else:
    content = raw.decode('utf-8')

print(f'Original: {len(content)} chars')

# Save original for comparison
with open('_orig_full.html', 'w', encoding='utf-8') as f:
    f.write(content)

# Verify original is syntactically correct
scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
main_script = None
for i, s in enumerate(scripts):
    if len(s) > 100:
        main_script = s
        with open(f'_orig_main.js', 'w', encoding='utf-8') as f:
            f.write(s.strip())
        print(f'Main script: script tag {i}, {len(s)} chars')

import os
os.system('node --check _orig_main.js 2>&1')
print('Original syntax check done.')
