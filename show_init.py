with open('index.html', 'r', encoding='utf-8') as f:
    c = f.read()

# Extract and print the full init() function
import re
idx = c.find('function init()')
# Find the end - look for the next function definition or init();
end = c.find('\ninit();', idx)
if end < 0:
    # fallback: find next function
    end = c.find('\nfunction ', idx + 20)
print(c[idx:end+10])
