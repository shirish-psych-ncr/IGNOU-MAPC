#!/usr/bin/env python3

# Read the current index.html
with open('/workspace/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# New CSS that matches the MPC/MPCE pages color theme
new_css = '''<style>
    /* Match MPC/MPCE pages color theme */
    :root {
      --bg: #f5f1e8;
      --surface: #fffdf8;
      --surface-strong: #f9f5ed;
      --ink: #20231f;
      --muted: #697063;
      --line: #ddd5c7;
      --accent: #146c70;
      --accent-strong: #0d4b4e;
      --gold: #c4842f;
      --green: #4e7d52;
      --red: #b64d4b;
      --blue: #4f6f91;
    }
    
    body.dark {
      --bg: #181a18;
      --surface: #232620;
      --surface-strong: #2c3029;
      --ink: #f2eee4;
      --muted: #b8bdad;
      --line: #3f463b;
      --accent: #66c0bd;
      --accent-strong: #92d8d5;
      --gold: #dda85a;
      --green: #82b884;
      --red: #df817e;
      --blue: #91acd0;
    }

    /* Dynamic Gradient Background - matching course pages */
    .animated-bg {
      background: linear-gradient(180deg, rgba(20, 108, 112, 0.1), var(--bg));
      background-size: 400% 400%;
      animation: gradientShift 15s ease infinite;
    }

    @keyframes gradientShift {
      0% { background-position: 0% 50%; }
      50% { background-position: 100% 50%; }
      100% { background-position: 0% 50%; }
    }

    /* Glassmorphism Effect - updated for course page theme */
    .glass {
      background: color-mix(in srgb, var(--surface) 94%, transparent);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid var(--line);
      box-shadow: 0 22px 60px rgba(42, 35, 24, 0.13);
    }

    .dark .glass {
      background: color-mix(in srgb, var(--surface) 96%, transparent);
      border: 1px solid var(--line);
      box-shadow: 0 22px 60px rgba(0, 0, 0, 0.35);
    }

    .glass-card {
      background: color-mix(in srgb, var(--surface) 94%, transparent);
      backdrop-filter: blur(10px);
      -webkit-backdrop-filter: blur(10px);
      border: 1px solid var(--line);
      box-shadow: 0 16px 38px rgba(42, 35, 24, 0.09);
      transition: all 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .dark .glass-card {
      background: color-mix(in srgb, var(--surface) 94%, transparent);
      border: 1px solid var(--line);
    }

    .glass-card:hover {
      transform: translateY(-3px);
      box-shadow: 0 22px 60px rgba(42, 35, 24, 0.21);
      border-color: var(--accent);
    }

    /* Custom Scrollbar */
    ::-webkit-scrollbar {
      width: 10px;
    }

    ::-webkit-scrollbar-track {
      background: rgba(255, 255, 255, 0.1);
    }

    ::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.3);
      border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.5);
    }

    /* Floating Animation */
    .floating {
      animation: float 6s ease-in-out infinite;
    }

    @keyframes float {
      0%, 100% { transform: translateY(0px); }
      50% { transform: translateY(-20px); }
    }

    /* Search Input Focus */
    .search-input:focus {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px color-mix(in srgb, var(--accent) 22%, transparent);
    }

    /* Badge Styles - matching course pages */
    .badge-theory {
      background: linear-gradient(135deg, var(--gold) 0%, var(--accent) 100%);
    }

    .badge-lab {
      background: linear-gradient(135deg, var(--red) 0%, var(--green) 100%);
    }

    .badge-project {
      background: linear-gradient(135deg, var(--blue) 0%, var(--accent) 100%);
    }

    /* Smooth Transitions */
    * {
      transition-property: background-color, border-color, color, fill, stroke;
      transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1);
      transition-duration: 180ms;
    }
    
    /* Mobile responsive adjustments */
    @media (max-width: 860px) {
      .hero-title {
        font-size: clamp(2.5rem, 8vw, 4rem) !important;
      }
      .grid-cols-3 {
        grid-template-columns: repeat(2, minmax(0, 1fr)) !important;
      }
    }
    
    @media (max-width: 560px) {
      .hero-title {
        font-size: clamp(2rem, 10vw, 3rem) !important;
      }
      .grid-cols-3 {
        grid-template-columns: 1fr !important;
      }
      .nav-container {
        padding-left: 12px !important;
        padding-right: 12px !important;
      }
      .hero-section {
        padding-top: 60px !important;
      }
    }
  </style>'''

# Find and replace the old style section
import re

# Pattern to match the entire <style>...</style> block
pattern = r'<style>\s*/\* Dynamic Gradient Background \*/.*?</style>'
replacement = new_css

new_content = re.sub(pattern, replacement, content, flags=re.DOTALL)

if new_content == content:
    print("Pattern not found, trying alternative...")
    # Try a simpler pattern
    start = content.find('<style>')
    end = content.find('</style>', start) + 8
    if start != -1 and end != -1:
        new_content = content[:start] + new_css + content[end:]
    else:
        print("Could not find style tags!")
        exit(1)

with open('/workspace/index.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Updated index.html with matching color theme!")
