with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Find embedded DATA sample to see actual keys
import re
# Look for store data pattern
idx = c.find('const DATA')
if idx >= 0:
    # Print first 500 chars of DATA
    print("DATA starts at", idx)
    print(c[idx:idx+600])
else:
    print("DATA not found!")

# Check if initApp calls init on page load
idx2 = c.find('function initApp()')
if idx2 >= 0:
    print("\n--- initApp ---")
    print(c[idx2:idx2+400])
