with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# The real issue: init() runs at page load time (line 52237: "init();")
# At that point, it reads embedded DATA. If there's ANY key mismatch, it crashes.
# But we've verified DATA uses '总支付' and channels uses '总支付'...
# 
# WAIT - maybe the issue is that the error is caught somewhere and shown as "ERR:"
# Let me check if init() is wrapped in try-catch

idx = c.find('function init()')
end = c.find('\ninit();', idx) + len('\ninit();')
init_code = c[idx:end]

# Check if there's a try-catch around the auto-call
after_init = c[end:end+50]
print(f"After init(); : {repr(after_init)}")

# Check: is the standalone init(); inside a try-catch or DOMContentLoaded?
# Let's see what's around line 52237
with open('_around_init.txt', 'w', encoding='utf-8') as out:
    # Go back 200 chars from init();
    init_call_pos = c.find('\ninit();', 52200)
    start = max(0, init_call_pos - 300)
    end2 = min(len(c), init_call_pos + 50)
    out.write(f"Position around init(): {start}-{end2}\n")
    out.write(c[start:end2])
print("Written _around_init.txt")
