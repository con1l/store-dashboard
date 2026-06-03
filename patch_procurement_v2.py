import re

with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# ══════════════════════════════════════════════════
# 1. channels 数组：确认没有 '采购'
# ══════════════════════════════════════════════════
old_ch = "'总支付','美团验券','采购','微信支付','支付宝','现金','京东外卖','美团外卖','淘宝闪购','抖音外卖'"
new_ch = "'总支付','美团验券','微信支付','支付宝','现金','京东外卖','美团外卖','淘宝闪购','抖音外卖'"
if old_ch in c:
    c = c.replace(old_ch, new_ch, 1)
    print("patched channels: removed 采购")
else:
    print("channels already patched or format changed, skipping")

# ══════════════════════════════════════════════════
# 2. showDetail：keyCh 去掉 '采购'
# ══════════════════════════════════════════════════
old_keyCh = "const keyCh=['总支付','抖音验券','微信支付','支付宝','美团外卖','采购'];"
new_keyCh = "const keyCh=['总支付','抖音验券','微信支付','支付宝','美团外卖'];"
if old_keyCh in c:
    c = c.replace(old_keyCh, new_keyCh, 1)
    print("patched keyCh: removed 采购")
else:
    # 尝试找真实内容
    m = re.search(r"const keyCh\s*=\s*\[([^\]]+)\];", c)
    if m:
        print(f"keyCh found: [{m.group(1)}]")
        # 去掉里面的 '采购'
        new_arr = [x.strip().strip("'\"") for x in m.group(1).split(',') if '采购' not in x]
        new_str = "const keyCh=['" + "','".join(new_arr) + "'];"
        c = c.replace(m.group(0), new_str, 1)
        print(f"patched keyCh -> {new_str}")
    else:
        print("WARNING: keyCh not found")

# ══════════════════════════════════════════════════
# 3. 在 showDetail 的 dStats 渲染后插入采购渲染
#    找 dStats.innerHTML = keyCh.map(...).join('')
# ══════════════════════════════════════════════════
proc_js = """
  // 采购单独显示
  const procVal = (DATA[dates[dates.length-1]][name]||{})['采购']||0;
  const procSection = document.getElementById('procurementSection');
  const procEl = document.getElementById('procStats');
  if (procVal > 0 || dates.some(d=>(DATA[d][name]||{})['采购']>0)) {
    procSection.style.display = 'block';
    let procHtml = '<div style="padding:10px;background:#fff3e0;border-radius:10px"><div style="font-size:13px;color:#888">最新日期采购金额</div><div style="font-size:22px;font-weight:700;color:#e65100">¥'+procVal.toFixed(2)+'</div></div>';
    // 各日期采购明细
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

# 插入到 dStats.innerHTML = ... 之后
marker = "}).join('');"
# 找 showDetail 函数里这个 marker 的位置
sd_idx = c.find('function showDetail(')
if sd_idx > -1:
    after_sd = c[sd_idx:]
    m_idx = after_sd.find(marker)
    if m_idx > -1:
        insert_at = sd_idx + m_idx + len(marker)
        # 检查是否已经插入过
        if 'procVal' not in after_sd[:m_idx+100]:
            c = c[:insert_at] + proc_js + c[insert_at:]
            print("inserted procurement rendering JS")
        else:
            print("procurement JS already inserted, skipping")
    else:
        print("WARNING: marker not found in showDetail")
else:
    print("WARNING: showDetail function not found")

# ══════════════════════════════════════════════════
# 4. 确认 HTML 里 procurementSection 存在，不存在则插入
# ══════════════════════════════════════════════════
if 'procurementSection' not in c:
    procurement_html = """
    <div class="procurement-section" id="procurementSection" style="display:none">
      <div class="chart-card">
        <h3>📦 采购成本</h3>
        <div id="procStats"></div>
      </div>
    </div>
"""
    # 插入到 detail-wrap 的 stats-grid 前
    c = c.replace(
        '<div class="stats-grid" id="dStats">',
        procurement_html + '    <div class="stats-grid" id="dStats">'
    )
    print("inserted procurementSection HTML")
else:
    print("procurementSection HTML already exists")

# ══════════════════════════════════════════════════
# 5. 首页 Header 统计：总金额不含采购（channels 已不含采购，确认一下）
#    首页 sTotal 显示的是 allStores 总支付合计，不受采购影响，无需改动
# ══════════════════════════════════════════════════

# ══════════════════════════════════════════════════
# 6. 写入
# ══════════════════════════════════════════════════
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(c)

print("all done")
