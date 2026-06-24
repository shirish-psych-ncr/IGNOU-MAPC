#!/usr/bin/env python3
import re

def transform_file(input_path, output_path):
    with open(input_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    lines = content.split('\n')
    output_lines = []
    
    # RULE 1: Forced root title - always start with this
    output_lines.append("# MPCE-013 CLEANED NOTES - PSYCHOTHERAPEUTIC INTERVENTIONS")
    
    current_theme = None
    current_question = None
    in_metadata = False
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Skip empty lines at very start (before first theme)
        if i == 0 and line.strip() == '':
            i += 1
            continue
        
        # RULE 2: Theme detection - look for --- followed by # THEME
        if line.strip() == '---':
            # Check if next non-empty line is a theme header
            j = i + 1
            while j < len(lines) and lines[j].strip() == '':
                j += 1
            if j < len(lines):
                next_line = lines[j]
                # Check if it's a theme line (# THERAPY or # MODULE or # UNIT)
                if re.match(r'^#\s+(.*(?:THERAPY|MODULE|UNIT).*)$', next_line, re.IGNORECASE):
                    # This is a theme section - skip the --- and convert the header
                    theme_text = re.sub(r'^#\s+', '', next_line).strip()
                    output_lines.append(f"## THEME: {theme_text}")
                    current_theme = theme_text
                    current_question = None
                    i = j + 1
                    continue
            # Otherwise it's an internal separator - RULE 7
            if current_question:
                output_lines.append("- ---")
            i += 1
            continue
        
        # Check for standalone # headers that are themes
        if re.match(r'^#\s+(.*(?:THERAPY|MODULE|UNIT).*)$', line, re.IGNORECASE):
            theme_text = re.sub(r'^#\s+', '', line).strip()
            output_lines.append(f"## THEME: {theme_text}")
            current_theme = theme_text
            current_question = None
            i += 1
            continue
        
        # RULE 3: Question detection - ##\d+: pattern
        question_match = re.match(r'^\s*##(\d+):\s+(.+)$', line)
        if question_match:
            q_num = question_match.group(1)
            q_text = question_match.group(2).strip()
            output_lines.append(f"- QUESTION {q_num}: {q_text}")
            current_question = f"QUESTION {q_num}"
            i += 1
            continue
        
        # RULE 4: Internal heading downgrading - ##I., ##II., etc. (Roman numerals)
        roman_heading = re.match(r'^\s*##([IVX]+)\.?\s*(.*)$', line)
        if roman_heading and current_question:
            roman = roman_heading.group(1)
            text = roman_heading.group(2).strip()
            output_lines.append(f"### {roman}. {text}")
            i += 1
            continue
        
        # RULE 4: Also handle ##\d+\. patterns inside questions (like ##1. Oral Stage)
        numbered_subheading = re.match(r'^\s*##(\d+)\.\s*(.*)$', line)
        if numbered_subheading and current_question:
            num = numbered_subheading.group(1)
            text = numbered_subheading.group(2).strip()
            output_lines.append(f"### {num}. {text}")
            i += 1
            continue
        
        # Handle other ## headings inside questions - convert to ###
        if re.match(r'^\s*##\s+', line) and current_question:
            text = re.sub(r'^\s*##\s+', '', line).strip()
            output_lines.append(f"### {text}")
            i += 1
            continue
        
        # Handle lone # inside questions (not themes) - convert to ###
        if re.match(r'^#\s+$', line) and current_question:
            # Lone # - skip it
            i += 1
            continue
        
        if re.match(r'^#\s+', line) and current_question:
            text = re.sub(r'^#\s+', '', line).strip()
            if text:
                output_lines.append(f"### {text}")
            i += 1
            continue
        
        # RULE 6: Inline metadata handling
        recall_match = re.match(r'^\s*"Recall_Cues":\s*"(.+)"$', line)
        if recall_match:
            text = recall_match.group(1)
            output_lines.append(f"- 🎯 Recall: {text}")
            i += 1
            continue
        
        exam_match = re.match(r'^\s*"Exam_usse":\s*"(.+)"$', line)
        if exam_match:
            text = exam_match.group(1)
            output_lines.append(f"- 📝 Exam Tip: {text}")
            i += 1
            continue
        
        # RULE 5: ASCII table/box conversion
        if re.match(r'^[+|]', line) or ('|' in line and '+---' in line):
            # Remove border characters, keep content
            cleaned = re.sub(r'[+\-]', ' ', line)
            cleaned = re.sub(r'\|', '|', cleaned)
            cleaned = cleaned.strip()
            if cleaned and '|' in cleaned:
                cells = [c.strip() for c in cleaned.split('|') if c.strip()]
                if len(cells) > 1:
                    output_lines.append(f"- {' | '.join(cells)}")
                else:
                    output_lines.append(f"- {cleaned}")
            elif cleaned:
                output_lines.append(f"- {cleaned}")
            i += 1
            continue
        
        # RULE 7: Section separators inside answer blocks
        if line.strip() == '---' and current_question:
            output_lines.append("- ---")
            i += 1
            continue
        
        # RULE 9: Orphaned content - attach as list item under current question
        if current_question and line.strip() and not line.startswith('##'):
            # Regular content line - prefix with proper indentation
            stripped = line.strip()
            if stripped:
                # Check if it's already a list item
                if re.match(r'^[-*]\s+', stripped):
                    output_lines.append(f"  {stripped}")
                elif re.match(r'^\d+\.\s+', stripped):
                    output_lines.append(f"  {stripped}")
                elif re.match(r'^\*\*\s*.*\*\*$', stripped):
                    # Bold heading
                    output_lines.append(f"  {stripped}")
                else:
                    output_lines.append(f"  - {stripped}")
            i += 1
            continue
        
        # Empty lines between content
        if line.strip() == '' and output_lines and output_lines[-1].strip():
            # Keep some spacing but not too much
            pass
        
        i += 1
    
    # Write output
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(output_lines))

if __name__ == '__main__':
    transform_file('/workspace/MPCE_CLEAN.txt', '/workspace/MPCE2_Clean2.txt')
    print("Transformation complete!")
