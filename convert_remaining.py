#!/usr/bin/env python3
"""Convert MPC-003 to MPC-006 to MPCE-012 format."""

import re
import json
from pathlib import Path
import shutil


def extract_questions(html_content):
    """Extract questions from MPC-003/004/005/006 style HTML."""
    questions = []
    
    # Find all details elements
    pattern = r'<details[^>]*>(.*?)</details>'
    details_matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    for details in details_matches:
        summary_match = re.search(r'<summary[^>]*>(.*?)</summary>', details, re.DOTALL | re.IGNORECASE)
        if not summary_match:
            continue
        
        summary_text = summary_match.group(1)
        # Remove time tags and other elements
        summary_clean = re.sub(r'<time[^>]*>[^<]*</time>', '', summary_text)
        summary_clean = re.sub(r'<span[^>]*>[^<]*</span>', '', summary_clean)
        summary_clean = re.sub(r'<[^>]+>', ' ', summary_clean).strip()
        summary_clean = ' '.join(summary_clean.split())
        
        # Extract year from time tag if present
        year_match = re.search(r'<time[^>]*datetime="([^"]+)"[^>]*>', summary_text)
        years = ""
        if year_match:
            date_str = year_match.group(1)
            year = date_str.split('-')[0]
            month = "Jun" if date_str.split('-')[1] == "06" else "Dec"
            years = f"{month} {year}"
        
        question_title = summary_clean.strip()
        question_title = re.sub(r'^[\s•\-\*🔹]+|[\s•\-\*🔹]+$', '', question_title)
        
        # Extract answer from div class="content p-4..."
        answer_match = re.search(r'<div[^>]*class="content[^"]*"[^>]*>(.*?)<button', details, re.DOTALL | re.IGNORECASE)
        
        if answer_match:
            answer_html = answer_match.group(1)
            # Clean answer
            answer_clean = re.sub(r'<button[^>]*>.*?</button>', '', answer_html, flags=re.DOTALL | re.IGNORECASE)
            answer_clean = re.sub(r'<br\s*/?>', '\n', answer_clean)
            answer_clean = re.sub(r'</h3>', '\n\n', answer_clean)
            answer_clean = re.sub(r'</h4>', '\n\n', answer_clean)
            answer_clean = re.sub(r'<h[34][^>]*>', '', answer_clean)
            answer_clean = re.sub(r'<strong>', '**', answer_clean)
            answer_clean = re.sub(r'</strong>', '**', answer_clean)
            answer_clean = re.sub(r'<b>', '**', answer_clean)
            answer_clean = re.sub(r'</b>', '**', answer_clean)
            answer_clean = re.sub(r'<[^>]+>', '', answer_clean)
            answer_clean = re.sub(r'\n{3,}', '\n\n', answer_clean)
            answer_clean = answer_clean.strip()
            
            if question_title and answer_clean and len(answer_clean) > 50:
                questions.append({'section': 'Questions', 'title': question_title, 'years': years, 'answer': answer_clean})
    
    return questions


def convert_answer_to_blocks(answer_text):
    """Convert plain text to MPCE-012 block format."""
    blocks = []
    paragraphs = re.split(r'\n\n+', answer_text.strip())
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        lines = para.split('\n')
        numbered_items = []
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.\s+', line) or (line.startswith('- ') and len(line) > 3):
                line_clean = re.sub(r'\*\*', '', line)
                numbered_items.append(line_clean)
        
        if numbered_items and len(numbered_items) > 1:
            blocks.append({'type': 'list', 'items': numbered_items})
        elif para.startswith('**') and '**:' in para:
            match = re.match(r'\*\*([^*]+)\*\*:\s*(.+)', para)
            if match:
                blocks.append({'type': 'paragraph', 'text': f"**{match.group(1)}**: {match.group(2)}"})
            else:
                blocks.append({'type': 'paragraph', 'text': re.sub(r'\*\*', '', para)})
        elif len(para) < 150 and not para.endswith('.') and not para.endswith('?'):
            blocks.append({'type': 'heading', 'level': 4, 'text': re.sub(r'\*\*', '', para)})
        else:
            blocks.append({'type': 'paragraph', 'text': re.sub(r'\*\*', '', para)})
    
    return blocks if blocks else [{'type': 'paragraph', 'text': answer_text}]


def process_file(input_path, output_path, template_path):
    """Process a single MPC file."""
    course_code = input_path.stem
    
    print(f"\n{'='*60}")
    print(f"Processing {course_code}...")
    print(f"{'='*60}")
    
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    questions = extract_questions(html_content)
    print(f"  Found {len(questions)} questions")
    
    if not questions:
        print(f"  Warning: No questions extracted")
        return False
    
    mpce_questions = []
    for idx, q in enumerate(questions, 1):
        answer_blocks = convert_answer_to_blocks(q['answer'])
        first_sentence = q['answer'].split('.')[0][:100] + "..."
        
        mpce_q = {
            'id': f"{course_code}-Q{idx:03d}",
            'segment': q['section'],
            'title': q['title'],
            'years': q['years'],
            'answer': answer_blocks,
            'cue': f"Key Concept: {first_sentence}",
            'examUse': "Format: Universal. Rule: Address all parts systematically."
        }
        mpce_questions.append(mpce_q)
    
    with open(template_path, 'r', encoding='utf-8') as f:
        template = f.read()
    
    titles = {
        'MPC-003': 'Personality Theories and Assessment',
        'MPC-004': 'Advanced Social Psychology',
        'MPC-005': 'Research Methods in Psychology',
        'MPC-006': 'Psychological Assessment'
    }
    
    title = titles.get(course_code, course_code)
    config = f'window.__IGNOU_STUDY_CONFIG__ = {{"courseTitle":"{title}","eyebrow":"IGNOU {title.lower()} desk","storageKey":"ignou-study-companion-{course_code.lower().replace("-","")}-v1"}};'
    template = re.sub(r'window\.__IGNOU_STUDY_CONFIG__\s*=\s*[^;]+;', config, template)
    
    q_start = template.find('window.__IGNOU_QUESTIONS__')
    q_end = template.find('];', q_start) + 2
    q_json = json.dumps(mpce_questions, ensure_ascii=False)
    template = template[:q_start] + f'window.__IGNOU_QUESTIONS__ = {q_json};' + template[q_end:]
    
    template = re.sub(r'<title>[^<]+</title>', f'<title>{course_code}: {title}</title>', template)
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template)
    
    print(f"  ✓ Created {output_path}")
    return True


def main():
    workspace = Path('/workspace')
    template = workspace / 'MPCE-012.html'
    
    courses = ['MPC-003', 'MPC-004', 'MPC-005', 'MPC-006']
    success = 0
    
    for course in courses:
        inp = workspace / f'{course}.html'
        out = workspace / f'{course}_new.html'
        
        if inp.exists() and process_file(inp, out, template):
            backup = workspace / f'{course}_backup.html'
            shutil.copy2(inp, backup)
            shutil.copy2(out, inp)
            out.unlink()
            print(f"  ✓ {course} converted (backup: {backup.name})")
            success += 1
    
    print(f"\n{'='*60}")
    print(f"Complete! {success}/{len(courses)} files converted.")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
