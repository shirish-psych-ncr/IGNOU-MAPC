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
    
    # Fix case: </strong>text** -> </strong>text</strong>
    content = re.sub(r'</strong>([^<]+?)\*\*', r'</strong>\1</strong>', content)
    
    # Fix case: **text<strong> -> <strong>text<strong> (then fix double strong)
    content = re.sub(r'\*\*([^<]+?)<strong>', r'<strong>\1<strong>', content)
    
    # Fix double strong tags
    content = content.replace('<strong><strong>', '<strong>')
    content = content.replace('</strong></strong>', '</strong>')
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

print("\nDone!")
