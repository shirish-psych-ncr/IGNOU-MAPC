#!/usr/bin/env python3
import re

def transform_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    output_lines = []
    output_lines.append("# MPCE-013 CLEANED NOTES - PSYCHOTHERAPEUTIC INTERVENTIONS")
    
    current_theme = None
    current_question = None
    
    i = 0
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        if len(output_lines) == 1 and line.strip() == '':
            i += 1
            continue
        
        # RULE 2: Theme detection
        if line.strip() == '---':
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                next_line = lines[j].rstrip('\n')
                if re.match(r'^#\s+(.*(?:THERAPY|MODULE|UNIT).*)$', next_line, re.IGNORECASE):
                    theme_text = re.sub(r'^#\s+', '', next_line).strip()
                    output_lines.append("")
                    output_lines.append(f"## THEME: {theme_text}")
                    current_theme = theme_text
                    current_question = None
                    i = j + 1
                    continue
            if current_question:
                output_lines.append("- ---")
            i += 1
            continue
        
        if re.match(r'^#\s+(.*(?:THERAPY|MODULE|UNIT).*)$', line, re.IGNORECASE):
            theme_text = re.sub(r'^#\s+', '', line).strip()
            output_lines.append("")
            output_lines.append(f"## THEME: {theme_text}")
            current_theme = theme_text
            current_question = None
            i += 1
            continue
        
        if re.match(r'^#\s*$', line):
            i += 1
            continue
        
        # RULE 3: Question detection
        question_match = re.match(r'^\s*##(\d+):\s+(.+)$', line)
        if question_match:
            q_num = question_match.group(1)
            q_text = question_match.group(2).strip()
            output_lines.append("")
            output_lines.append(f"- QUESTION {q_num}: {q_text}")
            current_question = f"QUESTION {q_num}"
            i += 1
            continue
        
        # RULE 4: Internal heading downgrading
        roman_heading = re.match(r'^\s*##([IVX]+)\.?\s*(.*)$', line)
        if roman_heading:
            roman = roman_heading.group(1)
            text = roman_heading.group(2).strip()
            output_lines.append(f"### {roman}. {text}")
            i += 1
            continue
        
        numbered_subheading = re.match(r'^\s*##(\d+)\.\s*(.*)$', line)
        if numbered_subheading:
            num = numbered_subheading.group(1)
            text = numbered_subheading.group(2).strip()
            output_lines.append(f"### {num}. {text}")
            i += 1
            continue
        
        if re.match(r'^\s*##\s+', line):
            text = re.sub(r'^\s*##\s+', '', line).strip()
            output_lines.append(f"### {text}")
            i += 1
            continue
        
        if re.match(r'^#\s+$', line):
            i += 1
            continue
        
        if re.match(r'^#\s+', line) and current_question:
            text = re.sub(r'^#\s+', '', line).strip()
            if text:
                output_lines.append(f"### {text}")
            i += 1
            continue
        
        # RULE 6: Recall_Cues (single line only)
        recall_match = re.match(r'^\s*"Recall_Cues":\s*"(.+)"[,]?\s*$', line)
        if recall_match:
            text = recall_match.group(1)
            output_lines.append(f"- 🎯 Recall: {text}")
            i += 1
            continue
        
        # RULE 6: Exam_usse - may span multiple lines (ends when we see ## or empty line after content)
        exam_match = re.match(r'^\s*"Exam_usse":\s*"(.+)$', line)
        if exam_match:
            text = exam_match.group(1)
            # Look ahead for closing quote on subsequent lines
            j = i + 1
            while j < len(lines):
                next_l = lines[j].rstrip('\n')
                if next_l.strip().endswith('"'):
                    # Found closing quote
                    final_part = next_l.strip()[:-1]  # Remove trailing "
                    if final_part:
                        text += " " + final_part
                    output_lines.append(f"- 📝 Exam Tip: {text.strip()}")
                    i = j + 1
                    break
                elif re.match(r'^\s*##\d+:', next_l) or next_l.strip() == '':
                    # No closing quote found, end here
                    output_lines.append(f"- 📝 Exam Tip: {text.strip()}")
                    i = j
                    break
                else:
                    text += " " + next_l.strip()
                    j += 1
            else:
                # Reached end of file without closing quote
                output_lines.append(f"- 📝 Exam Tip: {text.strip()}")
                i = j
            continue
        
        # RULE 5: ASCII table/box conversion
        if re.match(r'^[+|]', line):
            cleaned = re.sub(r'[+\-]', ' ', line)
            cleaned = cleaned.strip()
            if cleaned and '|' in cleaned:
                cells = [c.strip() for c in cleaned.split('|') if c.strip()]
                if len(cells) > 1:
                    output_lines.append(f"- {' | '.join(cells)}")
                elif cleaned:
                    output_lines.append(f"- {cleaned}")
            elif cleaned:
                output_lines.append(f"- {cleaned}")
            i += 1
            continue
        
        # Regular content under a question
        if current_question and line.strip():
            stripped = line.strip()
            if re.match(r'^\*\*.*\*\*$', stripped):
                output_lines.append(f"  {stripped}")
            elif re.match(r'^[-*]\s+', stripped):
                output_lines.append(f"  {stripped}")
            elif re.match(r'^\d+\.\s+', stripped):
                output_lines.append(f"  {stripped}")
            else:
                output_lines.append(f"  - {stripped}")
            i += 1
            continue
        
        if line.strip() == '':
            pass
        
        i += 1
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

if __name__ == '__main__':
    transform_file('/workspace/MPCE_CLEAN.txt', '/workspace/MPCE2_Clean2.txt')
    print("Transformation complete!")
