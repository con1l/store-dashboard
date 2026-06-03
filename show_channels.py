with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

import re
m = re.search(r'const channels\s*=\s*\[([^\]]+)\]', c)
if m:
    with open('_channels.txt', 'w', encoding='utf-8') as out:
        out.write(m.group(0))
    print(f"Found channels: {len(m.group(0))} chars")
else:
    print("channels NOT found!")
    # Try other patterns
    for pat in ['channels', 'Channels', 'CHANNELS']:
        idx = c.find(pat)
        if idx >= 0:
            print(f"Found '{pat}' at {idx}: ...{c[max(0,idx-20):idx+80]}...")
