import re, subprocess

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

scripts = re.findall(r'<script[^>]*>(.*?)</script>', content, re.DOTALL)
for i, s in enumerate(scripts):
    if len(s) < 20:
        continue
    code = s.strip()
    # Write to temp file and check with node
    with open('_check.js', 'w', encoding='utf-8') as f:
        f.write(code)
    result = subprocess.run(['node', '--check', '_check.js'], capture_output=True, text=True)
    if result.returncode != 0:
        print(f'Script {i} SYNTAX ERROR ({len(code)} chars):')
        print(result.stderr[:500])
    else:
        funcs = re.findall(r'function\s+(\w+)', code)
        print(f'Script {i} OK - {len(code)} chars, functions: {funcs}')
