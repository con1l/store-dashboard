import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

def find_and_show(c, name, ctx=100):
    idx = c.find(name)
    if idx == -1:
        return f"{name}: NOT FOUND"
    return f"{name}: ...{repr(c[max(0,idx-20):idx+ctx])}..."

# ══════════════════════════════════════════
# 1. channels 数组：去掉 '采购'
# ══════════════════════════════════════════
old = "'总支付','美团验券','采购','微信支付','支付宝','现金','京东外卖','美团外卖','淘宝闪购','抖音外卖'"
new = "'总支付','美团验券','微信支付','支付宝','现金','京东外卖','美团外卖','淘宝闪购','抖音外卖'"
if old in c:
    c = c.replace(old, new, 1)
    print("patched channels")
else:
    # 已经 patch 过了，确认一下
    idx = c.find("const channels")
    line = c[idx:idx+300]
    if "'采购'" in line:
        # 手动去掉
        c = c.replace("'采购',", "", 1)
        print("patched channels (manual remove)")
    else:
        print("channels already ok")

# ══════════════════════════════════════════
# 2. chShort 数组：去掉 '采购'（如果存在）
# ══════════════════════════════════════════
idx = c.find("const chShort")
if idx > -1:
    end = c.find(';', idx)
    line = c[idx:end]
    if "'采购'" in line:
        # 去掉采购
        new_line = line.replace("'采购',", "").replace(", '采购'", "")
        c = c[:idx] + new_line + c[end:]
        print("patched chShort")
    else:
        print("chShort ok (no 采购)")

# ══════════════════════════════════════════
# 3. showDetail 里的 keyCh：去掉 '采购'
# ══════════════════════════════════════════
# keyCh 在 showDetail 里
sd_idx = c.find('function showDetail(')
if sd_idx > -1:
    sd_end = c.find('\nfunction ', sd_idx + 10)
    if sd_end == -1:
        sd_end = c.find('function closeDetail', sd_idx)
    if sd_end > sd_idx:
        sd_block = c[sd_idx:sd_end]
        if "'采购'" in sd_block:
            # 找 keyCh 行
            m = re.search(r"const keyCh\s*=\s*\[([^\]]+)\];", sd_block)
            if m:
                items = [x.strip().strip("'\"") for x in m.group(1).split(',') if '采购' not in x]
                new_keyCh = "const keyCh=['" + "','".join(items) + "'];"
                c = c[:sd_idx] + c[sd_idx:sd_end].replace(m.group(0), new_keyCh) + c[sd_end:]
                print("patched keyCh in showDetail")
            else:
                # 直接替换字符串
                before = c[sd_idx:sd_end]
                after = before.replace("'采购',", "").replace(",'采购'", "")
                c = c[:sd_idx] + after + c[sd_end:]
                print("patched keyCh (string replace)")
        else:
            print("keyCh ok (no 采购)")

# ══════════════════════════════════════════
# 4. 确认 procurementSection HTML 存在
# ══════════════════════════════════════════
if 'procurementSection' not in c:
    html = """
    <div class="procurement-section" id="procurementSection" style="display:none">
      <div class="chart-card">
        <h3>📦 采购成本</h3>
        <div id="procStats"></div>
      </div>
    </div>
"""
    c = c.replace('<div class="stats-grid" id="dStats">', html + '    <div class="stats-grid" id="dStats">')
    print("added procurementSection HTML")
else:
    print("procurementSection HTML exists")

# ══════════════════════════════════════════
# 5. 确认 showDetail 里有采购渲染 JS
# ══════════════════════════════════════════
if 'procVal' not in c:
    # 需要在 showDetail 里 dStats 渲染后插入采购渲染
    sd_idx = c.find('function showDetail(')
    if sd_idx > -1:
        # 找 dStats.innerHTML = ...join 后面的 );
        sd_block_start = sd_idx
        sd_block_end = c.find('\n  // ', sd_idx + 10)
        if sd_block_end == -1:
            sd_block_end = c.find('function closeDetail', sd_idx)
        
        if sd_block_end > sd_idx:
            sd_content = c[sd_idx:sd_block_end]
            # 找最后一个 });
            last_br = sd_content.rfind('});')
            if last_br > -1:
                insert_pos = sd_idx + last_br + 3  # after });
                proc_js = """
  // 采购单独显示
  const procVal = (DATA[dates[dates.length-1]][name]||{})['采购']||0;
  const procSection = document.getElementById('procurementSection');
  const procEl = document.getElementById('procStats');
  if (procVal > 0 || dates.some(d=>(DATA[d][name]||{})['采购']>0)) {
    procSection.style.display = 'block';
    let procHtml = '<div style="padding:10px;background:#fff3e0;border-radius:10px"><div style="font-size:13px;color:#888">最新日期采购金额</div><div style="font-size:22px;font-weight:700;color:#e65100">¥'+procVal.toFixed(2)+'</div></div>';
    const procDays = dates.map(d=>{
      const pv=(DATA[d][name]||{})['采购']||0;
      return pv>0 ? '<div style="padding:6px 10px;background:#fff8e1;border-radius:8px;font-size:13px">'+d+'：¥'+pv.toFixed(2)+'</div>' : '';
    }).filter(Boolean).join('');
    if (procDays) procHtml += '<div style="margin-top:10px;display:grid;grid-template-columns:repeat(auto-fill,minmax(180px,1fr));gap:8px">'+procDays+'</div>';
    procEl.innerHTML = procHtml;
  } else {
    procSection.style.display = 'none';
  }
"""
                c = c[:insert_pos] + proc_js + c[insert_pos:]
                print("inserted procurement JS into showDetail")
else:
    print("procurement JS already in place")

# ══════════════════════════════════════════
# 6. 写入文件
# ══════════════════════════════════════════
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

# ══════════════════════════════════════════
# 7. 验证
# ══════════════════════════════════════════
with open('index.html', 'r', encoding='utf-8') as f:
    c2 = f.read()

results = []
for name, pattern in [
    ('channels has 采购', r"const channels\s*=\s*\[([^\]]+)\]"),
    ('chShort has 采购', r"const chShort\s*=\s*\[([^\]]+)\]"),
    ('keyCh in showDetail has 采购', r"const keyCh\s*=\s*\[([^\]]+)\]"),
    ('procurementSection exists', 'procurementSection'),
    ('procVal JS exists', 'procVal'),
    ('FIELD_MAP has 采购', r"'采购'"),
]:
    if pattern.startswith('const') or pattern.startswith("'"):
        m = re.search(pattern, c2)
        if m:
            has_proc = "'采购'" in m.group(0) or "'采购'" in (m.group(1) if len(m.groups()) > 0 else '')
            results.append(f"{name}: {'YES (BAD)' if has_proc else 'NO (OK)'}")
        else:
            results.append(f"{name}: not found (check manually)")
    else:
        results.append(f"{name}: {'YES' if pattern in c2 else 'NO'}")

with open('__final_verify.txt', 'w', encoding='utf-8') as f:
    f.write('\n'.join(results))

print("Done! Verify results in __final_verify.txt")
for r in results:
    print(" ", r)
