import os
import shutil

def organize_files_from_list(input_file_path, source_root_dir, destination_root_dir):
    """
    Reads a file with a specific format, creates a nested directory structure,
    and copies files from a source directory into the new structure.

    The input file format is expected to be:
    "GHRB/folder-name file-id folder-category"

    Args:
        input_file_path (str): The path to the text file containing the list.
        source_dir (str): The directory where the files to be copied are located.
        destination_root_dir (str): The root directory where the new folder structure
                                    will be created.
    """
    print(f"Starting file organization process...")
    
    # Ensure the destination root directory exists.
    # The exist_ok=True flag prevents an error if the directory already exists.
    os.makedirs(destination_root_dir, exist_ok=True)

    try:
        # Open and read the input file line by line
        with open(input_file_path, 'r') as file:
            for line in file:
                # Remove leading/trailing whitespace
                line = line.strip()

                # Skip any empty lines
                if not line:
                    continue

                # Split the line into three parts
                parts = line.split()

                # Ensure the line has the expected format (3 parts)
                if len(parts) != 3:
                    print(f"Skipping malformed line: '{line}'")
                    continue

                # Extract the required information from the line
                repo_with_prefix, file_id, category = parts

                # 1. Create the top-level folder name by taking last part segment after backslash
                repo_name = repo_with_prefix.split("/")[-1]

                # Construct the path for the destination directory.
                # This will be 'destination_root_dir/repo_name/category'
                destination_path = os.path.join(destination_root_dir, repo_name, category)

                # 2. Create the folder structure, including parent directories.
                # The exist_ok=True flag ensures no error is raised if the folders already exist.
                os.makedirs(destination_path, exist_ok=True)
                print(f"Ensured folder exists: {destination_path}")

                # 3. Find and copy the file
                # Assuming the file name in the source directory is just the file_id.
                source_file_name = f"{file_id}.txt" 
                source_file_path = os.path.join(source_root_dir, repo_name, source_file_name)
                
                # Check if the source file actually exists before attempting to copy
                if os.path.exists(source_file_path):
                    # Use shutil.copy2 to copy the file and preserve metadata
                    shutil.copy2(source_file_path, destination_path)
                    print(f"Copied '{source_file_name}' to '{destination_path}'")
                else:
                    print(f"Warning: Source file not found: '{source_file_path}'.")
                    
    except FileNotFoundError:
        print(f"Error: The input file '{input_file_path}' was not found.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

source_root_dir = "BR-Raw/GHRB"
destination_root_dir = "ReportGroup/GHRB"
input_file_path = "ReportGroup/ReportGroupLists.txt"
organize_files_from_list(input_file_path, source_root_dir, destination_root_dir)