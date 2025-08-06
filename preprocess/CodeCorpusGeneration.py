import os
import csv
import re

# Test code cleaning for a specific file 
def test_file_fixing():
    """
    Reads a Java file, applies the text block fixing, and prints the result.
    """
    with open("Corpus/jdt/3488.java", 'r', encoding='utf-8') as f:
        content = f.read()
    fixed_content = fix_text_blocks(content)

    with open("Corpus/jdt/3488.java", 'w', encoding='utf-8') as f:
        f.write(fixed_content)

# Regex to detect Java text block ("""...""")
TEXT_BLOCK_PATTERN = re.compile(r'"""\s*(.*?)\s*"""', re.DOTALL)
def fix_text_blocks(code):
    """"
    1) Convert Java text blocks (\"\"\"...\"\"\") into safe concatenated string literals.
    2) Remove illegal backslash-newline sequences (e.g. '\\\\\n').
    3) Replace stray '\\s' escapes with a plain space.
    4) Escape any remaining double-quotes.
    """
    def replace_block(match):
        content = match.group(1)
        # Remove backslash + newline inside the block
        content = re.sub(r'\\\s*\n', '', content)
        # Replace stray '\s' escapes with space
        content = re.sub(r'\\s', ' ', content)
        # Strip any backslash followed by spaces or tabs
        content = re.sub(r'\\[ \t]+', '', content)
        # Escape any embedded double-quotes
        content = content.replace('"', r'\"')
        # strip a trailing '\' on the very end of the block
        content = re.sub(r'\\\s*$', '', content)
        
        # Split into lines and join as concatenated string
        lines = content.splitlines()
        return '"{}"'.format('" +\n"'.join(lines)) 
    code = re.sub(TEXT_BLOCK_PATTERN, replace_block, code)
    code = re.sub(r'\\u000[aA]', r'\\n', code)
    code = re.sub(r'\\u000[cC]', r'\\f', code)
    code = re.sub(r'\\u000[dD]', r'\\r', code)
    code = re.sub(r'\\u000[9]',  r'\\t', code)
    code = re.sub(r'\\u0020', ' ', code)
    # code = re.sub(r'\\(?="(?=[,\s\)\}]))', '', code)
    # code = re.sub(r'\\(?="(?=[,;]))', '\\', code)
    return code

def collect_and_copy_java(src_dir, dest_dir, mapping_file_path, stats_csv_path):
    """
    Traverses src_dir for .java files, copies them to dest_dir as 1.java, 2.java, ...,
    writes a mapping file of number:original_path, and writes stats CSV of folder, count.
    """
    os.makedirs(dest_dir, exist_ok=True)

    mapping = {}
    counter = 1
    folder_counts = []

    for root, dirs, files in os.walk(src_dir):
        dirs.sort()
        files.sort()
        # Find .java files in this directory
        java_files = [f for f in files if f.lower().endswith(".java")]
        if java_files:
            count = len(java_files)
            folder_counts.append((root, count))
            for file in java_files:
                src_path = os.path.join(root, file)
                dest_path = os.path.join(dest_dir, f"{counter}.java")
                
                # cleaning needed for java parser compatibility issues raised in Blizzard
                # Read and fix content
                with open(src_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                fixed_content = fix_text_blocks(content)
                # Write fixed content to destination
                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(fixed_content)


                # shutil.copy2(src_path, dest_path)
                mapping[counter] = src_path
                counter += 1

    # Write the mapping file
    with open(mapping_file_path, "w", encoding="utf-8") as map_file:
        for num, original_path in mapping.items():
            map_file.write(f"{num}:{original_path}\n")

    # Write the stats CSV
    with open(stats_csv_path, "w", newline='', encoding="utf-8") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(["folder_path", "java_file_count"])
        for folder, count in folder_counts:
            writer.writerow([folder, count])

    total_files = counter - 1
    print(f"Total .java files found and copied: {total_files}")

if __name__ == "__main__":

    # test_file_fixing()  # Uncomment to test the text block fixing function
    
    # Example usage
    project_name = "tomcat"  # replace with your project name, [aspectj, birt, eclipse, jdt, swt, tomcat]
    source_directory = f"/home/ishita/BugLocalization/Data-22k/Code Corpus/{project_name}"  # replace with your source directory if needed
    destination_directory = f"Corpus/{project_name}"  # directory to hold the copied .java files
    os.makedirs(destination_directory, exist_ok=True)
    mapping_file_directory = r"Lucene-Index2File-Mapping"
    os.makedirs(mapping_file_directory, exist_ok=True)
    # Define paths for mapping and stats CSV
    mapping_file = os.path.join(mapping_file_directory, f"{project_name}.ckeys")
    stats_csv_file = os.path.join(mapping_file_directory, f"{project_name}.csv")

    collect_and_copy_java(source_directory, destination_directory, mapping_file, stats_csv_file)
    print(f"Copied {len(os.listdir(destination_directory))} files to '{destination_directory}'")
    print(f"Mapping written to '{mapping_file}'")