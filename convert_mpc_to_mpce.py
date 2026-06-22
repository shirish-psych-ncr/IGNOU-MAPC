#!/usr/bin/env python3
"""
Convert MPC-001 to MPC-006 HTML files to use MPCE-012's React-based architecture.
This script extracts question data from static HTML and converts it to JSON format
for the React app, then generates new HTML files with the MPCE-012 template.
"""

import re
import json
from html.parser import HTMLParser
from pathlib import Path

class QuestionExtractor(HTMLParser):
    """Extract questions and answers from MPC HTML files."""
    
    def __init__(self):
        super().__init__()
        self.questions = []
        self.current_question = None
        self.in_details = False
        self.in_summary = False
        self.in_answer = False
        self.current_section = ""
        self.section_stack = []
        self.text_buffer = ""
        self.tag_stack = []
        
    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        
        if tag == 'details':
            self.in_details = True
            self.text_buffer = ""
            
        elif tag == 'summary' and self.in_details:
            self.in_summary = True
            self.text_buffer = ""
            
        elif tag == 'div' and 'answer-box-content' in attrs_dict.get('class', ''):
            self.in_answer = True
            self.text_buffer = ""
            
        elif tag == 'h3' and self.in_details == False:
            # Section heading
            pass
            
        self.tag_stack.append(tag)
        
    def handle_endtag(self, tag):
        if tag == 'details':
            self.in_details = False
            if self.current_question:
                self.questions.append(self.current_question)
                self.current_question = None
                
        elif tag == 'summary':
            self.in_summary = False
            if self.in_details and not self.current_question:
                # Extract question title and years from summary
                title, years = self.parse_summary(self.text_buffer)
                self.current_question = {
                    'title': title,
                    'years': years,
                    'answer_text': '',
                    'section': self.current_section
                }
                
        elif tag == 'div':
            if self.in_answer and self.current_question:
                self.current_question['answer_text'] = self.text_buffer.strip()
            self.in_answer = False
            
        if self.tag_stack and self.tag_stack[-1] == tag:
            self.tag_stack.pop()
            
    def handle_data(self, data):
        if self.in_summary or self.in_answer:
            self.text_buffer += data
            
    def parse_summary(self, text):
        """Parse summary text to extract question title and years."""
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Try to extract years from brackets like [Jun 2024 (1), Dec 2022 (1)]
        years_match = re.search(r'\[([^\]]+)\]', text)
        years = years_match.group(1) if years_match else ""
        
        # Remove the years part to get the question
        title = re.sub(r'\s*\[[^\]]+\]\s*', '', text).strip()
        # Remove any remaining span tags or extra formatting
        title = re.sub(r'<[^>]+>', '', title).strip()
        
        return title, years
    
    def set_current_section(self, section):
        self.current_section = section


def extract_questions_from_html(html_content):
    """Extract all questions from MPC HTML file."""
    parser = QuestionExtractor()
    
    # Find all sections and their questions
    # Pattern to match section headings and their question cards
    section_pattern = r'<h3[^>]*>([^<]*(?:<(?!/h3)[^<]*)*)</h3>\s*<div[^>]*class="grid[^>]*>(.*?)</div>'
    
    sections = re.findall(section_pattern, html_content, re.DOTALL | re.IGNORECASE)
    
    questions = []
    
    for section_title, section_content in sections:
        # Clean section title
        section_title = re.sub(r'<[^>]+>', '', section_title).strip()
        section_title = re.sub(r'^[\s•\-\*]+|[\s•\-\*]+$', '', section_title)
        
        # Find all details elements in this section
        details_pattern = r'<details[^>]*>.*?<summary[^>]*>(.*?)</summary>.*?<div[^>]*class="[^"]*answer-box-content[^"]*"[^>]*>(.*?)</div>\s*</details>'
        details_matches = re.findall(details_pattern, section_content, re.DOTALL | re.IGNORECASE)
        
        for summary, answer in details_matches:
            # Parse summary for question and years
            summary_text = re.sub(r'<[^>]+>', ' ', summary).strip()
            summary_text = ' '.join(summary_text.split())
            
            years_match = re.search(r'\[([^\]]+)\]', summary_text)
            years = years_match.group(1) if years_match else ""
            
            title = re.sub(r'\s*\[[^\]]+\]\s*', '', summary_text).strip()
            
            # Clean answer HTML - convert <br> to newlines, remove buttons
            answer_clean = re.sub(r'<button[^>]*>.*?</button>', '', answer, flags=re.DOTALL | re.IGNORECASE)
            answer_clean = re.sub(r'<br\s*/?>', '\n', answer_clean)
            answer_clean = re.sub(r'<b>', '**', answer_clean)
            answer_clean = re.sub(r'</b>', '**', answer_clean)
            answer_clean = re.sub(r'<strong>', '**', answer_clean)
            answer_clean = re.sub(r'</strong>', '**', answer_clean)
            answer_clean = re.sub(r'<[^>]+>', '', answer_clean)
            answer_clean = answer_clean.strip()
            
            if title and answer_clean:
                questions.append({
                    'section': section_title,
                    'title': title,
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
            
        # Check if it's a numbered list item
        if re.match(r'^\d+\.\s+\*\*', para) or re.match(r'^\d+\.\s+', para):
            # Extract list items from paragraph
            lines = para.split('\n')
            items = []
            for line in lines:
                line = line.strip()
                if line:
                    # Remove markdown bold markers
                    line = re.sub(r'\*\*', '', line)
                    items.append(line)
            if items:
                blocks.append({'type': 'list', 'items': items})
        elif para.startswith('**') and '**:' in para:
            # Bold term with definition
            match = re.match(r'\*\*([^*]+)\*\*:\s*(.+)', para)
            if match:
                blocks.append({
                    'type': 'paragraph',
                    'text': f"**{match.group(1)}**: {match.group(2)}"
                })
            else:
                blocks.append({'type': 'paragraph', 'text': re.sub(r'\*\*', '', para)})
        elif len(para) < 150 and not para.endswith('.'):
            # Might be a heading
            blocks.append({
                'type': 'heading',
                'level': 4,
                'text': re.sub(r'\*\*', '', para)
            })
        else:
            # Regular paragraph
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
    
    course_code = input_path.stem  # e.g., "MPC-001"
    
    print(f"\n{'='*60}")
    print(f"Processing {course_code}...")
    print(f"{'='*60}")
    
    # Read input HTML
    with open(input_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract questions
    questions = extract_questions_from_html(html_content)
    print(f"Found {len(questions)} questions")
    
    if not questions:
        print(f"Warning: No questions found in {input_path}")
        return False
    
    # Convert to MPCE-012 format
    mpce_questions = []
    for idx, q in enumerate(questions, 1):
        answer_blocks = convert_answer_to_blocks(q['answer'])
        
        # Generate cue and examUse from answer content
        first_sentence = q['answer'].split('.')[0][:100] + "..."
        
        mpce_q = {
            'id': generate_question_id(course_code, idx),
            'segment': q['section'],
            'title': q['title'],
            'years': q['years'],
            'answer': answer_blocks,
            'cue': f"Key Concept: {first_sentence}",
            'examUse': f"Format: Universal. Rule: Address all parts of the question systematically."
        }
        mpce_questions.append(mpce_q)
    
    # Read MPCE-012 template
    with open(mpce_template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()
    
    # Update config in template
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
    questions_pattern = r'window\.__IGNOU_QUESTIONS__\s*=\s*\[[^\]]*\];'
    questions_json = json.dumps(mpce_questions, ensure_ascii=False)
    new_questions = f'window.__IGNOU_QUESTIONS__ = {questions_json};'
    template_content = re.sub(questions_pattern, new_questions, template_content)
    
    # Update title
    title_pattern = r'<title>[^<]+</title>'
    new_title = f'<title>{course_code}: {course_title}</title>'
    template_content = re.sub(title_pattern, new_title, template_content)
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(template_content)
    
    print(f"✓ Successfully created {output_path}")
    return True


def main():
    workspace = Path('/workspace')
    mpce_template = workspace / 'MPCE-012.html'
    
    if not mpce_template.exists():
        print(f"Error: Template file {mpce_template} not found!")
        return
    
    # Courses to convert
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
    print(f"Conversion complete! {success_count}/{len(courses)} files processed successfully.")
    print(f"{'='*60}")
    
    # Optional: Replace original files with converted ones
    print("\nTo replace original files with converted versions, run:")
    for course in courses[:success_count]:
        print(f"  mv /workspace/{course}_converted.html /workspace/{course}.html")


if __name__ == '__main__':
    main()
