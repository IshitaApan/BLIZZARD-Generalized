import os
import shutil
import csv
import re

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
        
        # Split into lines and join as concatenated string
        lines = content.splitlines()
        return '"{}"'.format('" +\n"'.join(lines)) 
    return re.sub(TEXT_BLOCK_PATTERN, replace_block, code)


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
    # Example usage
    source_directory = r"/home/ishita/BugLocalization/Data-22k/Code Corpus/eclipse" # replace project names with aspectj, birt, eclipse, 
    destination_directory = r"Corpus/eclipse"
    mapping_file_directory = r"Lucene-Index2File-Mapping"
    mapping_file = os.path.join(mapping_file_directory, "eclipse.ckeys")
    stats_csv_file = os.path.join(mapping_file_directory, "eclipse.csv")

    collect_and_copy_java(source_directory, destination_directory, mapping_file, stats_csv_file)
    print(f"Copied {len(os.listdir(destination_directory))} files to '{destination_directory}'")
    print(f"Mapping written to '{mapping_file}'")
# 7121 java files for aspectj