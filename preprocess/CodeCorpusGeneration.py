import os
import shutil
import csv

def collect_and_copy_java(src_dir, dest_dir, mapping_file_path):
    """
    Traverses src_dir for .java files (sorted for deterministic order),
    prints each subfolder path that contains .java files with its count,
    copies each to dest_dir named sequentially (1.java, 2.java, ...),
    and writes a mapping file of the numeric name to the original full path.
    Finally prints the total number of .java files found.
    """
    os.makedirs(dest_dir, exist_ok=True)

    mapping = {}
    counter = 1
    folder_counts = {}

    for root, dirs, files in os.walk(src_dir):
        dirs.sort()
        files.sort()

        # Find .java files in this directory
        java_files = [f for f in files if f.lower().endswith(".java")]
        if java_files:
            folder_counts[root] = len(java_files)
            print(f"{root}: {len(java_files)} .java file(s)")

            for file in java_files:
                src_path = os.path.join(root, file)
                dest_filename = f"{counter}.java"
                dest_path = os.path.join(dest_dir, dest_filename)

                shutil.copy2(src_path, dest_path)
                mapping[counter] = src_path
                counter += 1

    # Write the mapping file
    with open(mapping_file_path, "w", encoding="utf-8") as map_file:
        for num, original_path in mapping.items():
            map_file.write(f"{num}:{original_path}\n")

    total_files = counter - 1
    print(f"Total .java files found: {total_files}")


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
                shutil.copy2(src_path, dest_path)
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
    source_directory = r"/home/ishita/BugLocalization/Data-22k/Code Corpus/aspectj"
    destination_directory = r"Corpus/aspectj"
    mapping_file_directory = r"Lucene-Index2File-Mapping"
    mapping_file = os.path.join(mapping_file_directory, "aspectj.ckeys")
    stats_csv_file = os.path.join(mapping_file_directory, "aspectj.csv")

    collect_and_copy_java(source_directory, destination_directory, mapping_file, stats_csv_file)
    print(f"Copied {len(os.listdir(destination_directory)) - 1} files to '{destination_directory}'")
    print(f"Mapping written to '{mapping_file}'")
# 7121