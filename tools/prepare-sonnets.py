import re

from gotaglio.shared import to_json_string

def read_sonnets(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    
    # Splitting based on Roman numeral lines followed by a blank line
    sonnet_pattern = re.compile(r'^(?=[IVXLCDM]+$)', re.MULTILINE)
    sonnet_sections = sonnet_pattern.split(text)
    
    sonnets = []
    for section in sonnet_sections[1:]:  # Skip the first empty section
        lines = section.strip().split('\n')
        if not lines:
            continue
        number = lines[0]  # Roman numeral
        body = '\n'.join(lines[2:])
        sonnets.append(f'Sonnet {number}\n\n{body}')
    
    return sonnets

def generate_python_source(sonnets):
    output_lines = ["sonnets = ["]
    output_lines.extend(f'"{sonnet},"' for sonnet in sonnets)
    output_lines.append("]\n")
    return '\n'.join(output_lines)

if __name__ == "__main__":
    input_file = "sonnets.txt"
    sonnets_list = read_sonnets(input_file)
    python_code = generate_python_source(sonnets_list)

    # Write the generated code to a Python file
    with open("sonnets.py", "w", encoding="utf-8") as output_file:
        output_file.write(to_json_string(sonnets_list))
    
    print("Python source file 'sonnets.py' generated successfully.")
