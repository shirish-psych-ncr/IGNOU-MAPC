#!/usr/bin/env python3
"""
Convert MPC-001 to MPC-006 HTML files to use MPCE-012's React-based architecture.
"""

import re
import json
from pathlib import Path


def extract_questions_from_html(html_content):
    """Extract all questions from MPC HTML file using regex."""
    
    questions = []
    
    # Find all details elements with their content
    # Pattern for details element containing summary and answer
    pattern = r'<details[^>]*>(.*?)</details>'
    
    details_matches = re.findall(pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    print(f"  Found {len(details_matches)} details elements")
    
    for details in details_matches:
        # Extract summary (question)
        summary_match = re.search(r'<summary[^>]*>(.*?)</summary>', details, re.DOTALL | re.IGNORECASE)
        if not summary_match:
            continue
        
        summary_text = summary_match.group(1)
        summary_clean = re.sub(r'<[^>]+>', ' ', summary_text).strip()
        summary_clean = ' '.join(summary_clean.split())
        
        # Extract years from brackets
        years_match = re.search(r'\[([^\]]+)\]', summary_clean)
        years = years_match.group(1) if years_match else ""
        
        # Remove years from question title
        question_title = re.sub(r'\s*\[[^\]]+\]\s*', '', summary_clean).strip()
        # Remove emoji icons
        question_title = re.sub(r'^[\s•\-\*🔹]+|[\s•\-\*🔹]+$', '', question_title)
        
        # Extract answer from answer-box-content div
        answer_match = re.search(r'<div[^>]*class="[^"]*answer-box-content[^"]*"[^>]*>(.*?)<button', details, re.DOTALL | re.IGNORECASE)
        
        if answer_match:
            answer_html = answer_match.group(1)
            # Clean answer: remove buttons, convert formatting
            answer_clean = re.sub(r'<br\s*/?>', '\n', answer_html)
            answer_clean = re.sub(r'<b>', '**', answer_clean)
            answer_clean = re.sub(r'</b>', '**', answer_clean)
            answer_clean = re.sub(r'<strong>', '**', answer_clean)
            answer_clean = re.sub(r'</strong>', '**', answer_clean)
            answer_clean = re.sub(r'<[^>]+>', '', answer_clean)
            answer_clean = answer_clean.strip()
            
            if question_title and answer_clean and len(answer_clean) > 50:
                # Try to determine section from context
                section = "Questions"
                
                questions.append({
                    'section': section,
                    'title': question_title,
                    'years': years,
                    'answer': answer_clean
                })
    
    return questions


def convert_answer_to_blocks(answer_text):
    """Convert plain text answer to MPCE-012 block format."""
    blocks = []
    
    # Split by paragraphs (double newlines)
    paragraphs = re.split(r'\n\n+', answer_text.strip())
    
    for para in paragraphs:
        para = para.strip()
        if not para:
            continue
        
        # Check for numbered items
        lines = para.split('\n')
        numbered_items = []
        
        for line in lines:
            line = line.strip()
            if re.match(r'^\d+\.\s+', line):
                line_clean = re.sub(r'\*\*', '', line)
                numbered_items.append(line_clean)
        
        if numbered_items:
            blocks.append({'type': 'list', 'items': numbered_items})
        elif para.startswith('**') and '**:' in para:
            match = re.match(r'\*\*([^*]+)\*\*:\s*(.+)', para)
            if match:
                blocks.append({
                    'type': 'paragraph',
                    'text': f"**{match.group(1)}**: {match.group(2)}"
                })
            else:
                blocks.append({'type': 'paragraph', 'text': re.sub(r'\*\*', '', para)})
        elif len(para) < 150 and not para.endswith('.') and not para.endswith('?'):
            blocks.append({
                'type': 'heading',
                'level': 4,
                'text': re.sub(r'\*\*', '', para)
            })
        else:
            blocks.append({
                'type': 'paragraph',
                'text': re.sub(r'\*\*', '', para)
            })
    
    return blocks if blocks else [{'type': 'paragraph', 'text': answer_text}]


def generate_question_id(course_code, index):
    """Generate unique question ID."""
    return f"{course_code}-Q{index:03d}"


def process_mpc_file(input_path, output_path, mpce_template_path):
    """Process a single MPC file and convert it to MPCE format."""
    
    course_code = input_path.stem
    
    print(f"\n{'='*60}")
    print(f"Processing {course_code}...")
    print(f"{'='*60}")
    
    # Read input HTML
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract questions
    questions = extract_questions_from_html(html_content)
    print(f"  Extracted {len(questions)} valid questions")
    
    if not questions:
        print(f"Warning: No questions found in {input_path}")
        return False
    
    # Convert to MPCE-012 format
    mpce_questions = []
    for idx, q in enumerate(questions, 1):
        answer_blocks = convert_answer_to_blocks(q['answer'])
        first_sentence = q['answer'].split('.')[0][:100] + "..."
        
        mpce_q = {
            'id': generate_question_id(course_code, idx),
            'segment': q['section'],
            'title': q['title'],
            'years': q['years'],
            'answer': answer_blocks,
            'cue': f"Key Concept: {first_sentence}",
            'examUse': f"Format: Universal. Rule: Address all parts systematically."
        }
        mpce_questions.append(mpce_q)
    
    # Read MPCE-012 template
    with open(mpce_template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Update config
    course_title_map = {
        'MPC-001': 'Cognitive Psychology',
        'MPC-002': 'Life Span Psychology',
        'MPC-003': 'Personality Theories and Assessment',
        'MPC-004': 'Advanced Social Psychology',
        'MPC-005': 'Research Methods in Psychology',
        'MPC-006': 'Psychological Assessment'
    }
    
    course_title = course_title_map.get(course_code, course_code)
    eyebrow = f"IGNOU {course_title.lower()} desk"
    storage_key = f"ignou-study-companion-{course_code.lower().replace('-', '')}-v1"
    
    # Replace config
    config_pattern = r'window\.__IGNOU_STUDY_CONFIG__\s*=\s*[^;]+;'
    new_config = f'window.__IGNOU_STUDY_CONFIG__ = {{"courseTitle":"{course_title}","eyebrow":"{eyebrow}","storageKey":"{storage_key}"}};'
    template_content = re.sub(config_pattern, new_config, template_content)
    
    # Replace questions
    questions_start = template_content.find('window.__IGNOU_QUESTIONS__')
    if questions_start == -1:
        print("Error: Could not find questions array in template")
        return False
    
    questions_end = template_content.find('];', questions_start) + 2
    questions_json = json.dumps(mpce_questions, ensure_ascii=False)
    new_questions = f'window.__IGNOU_QUESTIONS__ = {questions_json};'
    template_content = template_content[:questions_start] + new_questions + template_content[questions_end:]
    
    # Update title
    title_pattern = r'<title>[^<]+</title>'
    new_title = f'<title>{course_code}: {course_title}</title>'
    template_content = re.sub(title_pattern, new_title, template_content)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✓ Successfully created {output_path}")
    print(f"  Questions: {len(questions)}")
    return True


def main():
    workspace = Path('/workspace')
    mpce_template = workspace / 'MPCE-012.html'
    
    if not mpce_template.exists():
        print(f"Error: Template file {mpce_template} not found!")
        return
    
    courses = ['MPC-001', 'MPC-002', 'MPC-003', 'MPC-004', 'MPC-005', 'MPC-006']
    
    success_count = 0
    for course in courses:
        input_path = workspace / f'{course}.html'
        output_path = workspace / f'{course}_converted.html'
        
        if input_path.exists():
            if process_mpc_file(input_path, output_path, mpce_template):
                success_count += 1
        else:
            print(f"Warning: {input_path} not found, skipping...")
    
    print(f"\n{'='*60}")
    print(f"Conversion complete! {success_count}/{len(courses)} files processed.")
    print(f"{'='*60}")
    
    # Backup and replace
    if success_count > 0:
        print("\nBacking up originals and replacing...")
        import shutil
        for course in courses:
            original = workspace / f'{course}.html'
            converted = workspace / f'{course}_converted.html'
            backup = workspace / f'{course}_backup.html'
            
            if converted.exists() and original.exists():
                shutil.copy2(original, backup)
                shutil.copy2(converted, original)
                converted.unlink()
                print(f"  ✓ {course} converted (backup: {backup.name})")
        
        print("\n✓ All conversions complete!")


if __name__ == '__main__':
    main()
