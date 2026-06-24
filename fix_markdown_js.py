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
    
    # Fix markdown bold **text** -> <strong>text</strong> in JavaScript strings
    # We need to be careful to only replace in the JSON data, not in HTML/JS code
    
    # Pattern for **bold** in JSON string values (within the window.__IGNOU_QUESTIONS__ array)
    # Match ** followed by non-* characters followed by **
    def replace_bold(match):
        inner = match.group(1)
        return f'<strong>{inner}</strong>'
    
    # Replace **text** patterns (but not already converted ones)
    content = re.sub(r'\*\*([^*]+)\*\*', replace_bold, content)
    
    # Pattern for *italic* (single asterisks around words)
    # Be more careful here to avoid matching other uses of single asterisks
    def replace_italic(match):
        # Check if this is likely italic (word characters only)
        inner = match.group(1)
        if re.match(r'^[\w\s\-\']+$', inner.strip()):
            return f'<em>{inner}</em>'
        return match.group(0)
    
    # Replace *text* patterns for italics (more conservative)
    # Only replace when surrounded by word boundaries and not part of other syntax
    content = re.sub(r'(?<![\\*])\*([a-zA-Z][\w\s\-]{1,50}[a-zA-Z])\*(?![\\*])', replace_italic, content)
    
    if content != original:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"Fixed {filepath}")
    else:
        print(f"No changes needed for {filepath}")

print("\nDone!")
