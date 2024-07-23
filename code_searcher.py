import os
import re
import subprocess


def extract_grep_output(line):
    # Regular expressions to match the grep output lines
    regex_colon = r'(.*):(\d+):(.*)'
    regex_dash = r'(.*?)-(\d+)-(.*)'
    match_colon = re.match(regex_colon, line)
    match_dash = re.match(regex_dash, line)

    if match_colon:
        filename, line_number, line_content = match_colon.groups()
        return [filename, line_number, line_content]
    elif match_dash:
        filename, line_number, line_content = match_dash.groups()
        return [filename, line_number, line_content]
    else:
        return ["", "", line]


def search_function_with_context(function_name, before_lines=5, after_lines=10, search_dir="./code_repo"):
    pattern = re.compile(function_name)
    grep_result = ""
    for root, dirs, files in os.walk(search_dir):
        for file in files:
            file_path = os.path.join(root, file)
            with open(file_path, 'r', encoding='utf-8',errors='ignore') as f:
                lines = f.readlines()
                for i, line in enumerate(lines):
                    if pattern.search(line):
                        start = max(0, i-before_lines)
                        end = min(len(lines), i+after_lines+1)
                        # print(''.join(lines[start:end]))
                        grep_result += f"{''.join(lines[start:end])}\n"
                        # print("--" * 40)
    
    command = [
        "grep",
        "-r",  # Recursive search
        "-n",  # Print line numbers
        f"-B{before_lines}",  # Show context before the match
        f"-A{after_lines}",  # Show context after the match
        f"{function_name}",  # The search pattern
        search_dir
    ]
    # Run the command and capture the output
    # result = subprocess.run(command, capture_output=True, text=True)

    # Split the output by lines
    # output_lines = result.stdout.splitlines()
    output_lines = grep_result.splitlines()

    # Group the lines by occurrence
    occurrences = []
    current_filename = None
    current_start_line = None
    current_lines = []
    for line in output_lines:
        if line.startswith("--"):  # This line separates occurrences
            if current_filename is not None:
                occurrences.append((current_filename, current_start_line, "\n".join(current_lines)))
            current_lines = []
        else:
            current_filename, line_number, line_text = extract_grep_output(line)
            if function_name in line_text:
                current_start_line = line_number + ":" + line_text
            current_lines.append(line_text)

    # Add the last occurrence if there is one
    if current_filename is not None:
        occurrences.append((current_filename, current_start_line, "\n".join(current_lines)))

    return occurrences


def get_function_context(function_name):
    results = search_function_with_context(function_name)
    output = ""
    for filename, start_line, context in results:
        output += f"Filename: {filename}\n"
        output += f"Start line: {start_line}\n"
        output += "Context:\n"
        output += context
        output += "\n\n"
    return output


if __name__ == "__main__":
    function_name = "set_visible_true"
    results = search_function_with_context(function_name)

    for filename, start_line, context in results:
        print(f"Filename: {filename}")
        print(f"Start line: {start_line}")
        print("Context:")
        print(context)
        print()
