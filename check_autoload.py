with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find window.onload or DOMContentLoaded or any auto-init
import re
for pat in ['window.onload', 'DOMContentLoaded', 'initApp()', 'init();']:
    positions = []
    start = 0
    while True:
        idx = c.find(pat, start)
        if idx < 0: break
        positions.append(idx)
        start = idx + 1
    if positions:
        print(f"'{pat}' found at: {positions}")

# The key question: is init() called automatically on page load?
# Or only after checkAuth passes?
auth_idx = c.find('function checkAuth')
print(f"\ncheckAuth at: {auth_idx}")
if auth_idx > 0:
    print(c[auth_idx:auth_idx+300])
