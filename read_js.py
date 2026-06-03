import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 找到 <script> 标签后的纯 JS 逻辑（handleUpload 之后）
# 先找 handleUpload 函数
idx = content.find('function handleUpload')
if idx == -1:
    idx = content.find('handleUpload')
    
with open('js_dump.txt', 'w', encoding='utf-8') as out:
    out.write("=== handleUpload function ===\n")
    out.write(content[max(0,idx-50):idx+5000])
    out.write("\n\n=== function init() ===\n")
    idx2 = content.find('function init()')
    out.write(content[max(0,idx2-50):idx2+3000])
    out.write("\n\n=== normalizeStoreKeys ===\n")
    idx3 = content.find('function normalizeStoreKeys')
    if idx3 > -1:
        out.write(content[idx3:idx3+2000])
    else:
        out.write("not found\n")
    out.write("\n\n=== const DATA line ===\n")
    idx4 = content.find('const DATA')
    if idx4 > -1:
        out.write(content[idx4:idx4+200])
print("done -> js_dump.txt")
