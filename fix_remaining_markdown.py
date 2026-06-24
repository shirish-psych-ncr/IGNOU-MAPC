#!/usr/bin/env python3
import re
import os

files = [
    '/workspace/MPC-001.html',
    '/workspace/MPC-002.html', 
    '/workspace/MPC-003.html',
    '/workspace/MPC-004.html',
    '/workspace/MPC-005.html',
    '/workspace/MPC-006.html',
    '/workspace/MPCE-011.html',
    '/workspace/MPCE-012.html',
    '/workspace/MPCE-013.html'
]

for filepath in files:
    if not os.path.exists(filepath):
        print(f"Skipping {filepath} - file not found")
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original = content
    
    # More aggressive pattern to catch remaining **text** patterns
    # This handles cases where there might be nested tags or special characters
    def replace_bold(match):
        inner = match.group(1)
        # Skip if already has HTML tags inside
        if '<' in inner or '>' in inner:
            return match.group(0)
        return f'<strong>{inner}</strong>'
    
    # Replace **text** patterns more aggressively
    content = re.sub(r'\*\*([^*]+?)\*\*', replace_bold, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

print("\nDone!")
