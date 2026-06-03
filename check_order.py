with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Check order: is FIELD_MAP defined before handleUpload?
field_map_pos = c.find('const FIELD_MAP')
hu_pos = c.find('async function handleUpload')
norm_func_pos = c.find('function normalizeStoreKeys')

print(f"FIELD_MAP at:    {field_map_pos}")
print(f"normalizeStoreKeys at: {norm_func_pos}")
print(f"handleUpload at: {hu_pos}")

if field_map_pos > hu_pos:
    print("!!! PROBLEM: FIELD_MAP is AFTER handleUpload - it won't be visible!")
else:
    print("OK: order is correct")

# Also check: does the error happen on page load (before upload)?
# The error shows "ERR:" prefix which means it's from handleUpload catch block
# But user says it happens immediately...
# Let's check if there's any code that runs before upload that reads 总支付

# Check if init() is called on page load
idx = c.find('<body')
body_section = c[idx:idx+500]
with open('_body.txt', 'w', encoding='utf-8') as out:
    out.write(body_section)
print("\nBody section written to _body.txt")
