import os
import subprocess
import xml.etree.ElementTree as ET

def find_commit_and_files(xml_path, table_name, bug_id):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    for table in root.findall(".//table"):
        if table.get("name") == table_name:
            bug_id_elem = table.find("./column[@name='bug_id']")
            if bug_id_elem is not None and bug_id_elem.text.strip() == str(bug_id):
                commit_elem = table.find("./column[@name='commit']")
                files_elem = table.find("./column[@name='files']")

                if commit_elem is None or files_elem is None:
                    raise ValueError("Missing commit or files column in XML")

                commit = commit_elem.text.strip()
                files_text = files_elem.text.strip()

                # Properly split .java file paths
                files = [f.strip() + ".java" for f in files_text.split(".java") if f.strip()]
                return commit, files
    return None, None

def verify_keywords_in_commit(repo_path, commit, files, keywords):
    results = {}
    for file_path in files:
        try:
            # Read file content from the given commit without checking out
            cmd = ["git", "-C", repo_path, "show", f"{commit}:{file_path}"]
            completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
            content = completed.stdout

            keyword_hits = {kw: (kw in content) for kw in keywords}
            results[file_path] = keyword_hits
        except subprocess.CalledProcessError:
            results[file_path] = {kw: False for kw in keywords}  # file not found
    return results

if __name__ == "__main__":
    table_name = "assertj"
    xml_path = f"/home/ishita/BugLocalization/Data-GHRB/{table_name}.xml"  # Your XML file
    bug_id = 2364
    keywords = ["IntrospectionError", "Optional", "PropertyOrFieldSupport", "getSimpleValue", "ByNameSingleExtractor"]  # keywords to check

    commit, files = find_commit_and_files(xml_path, table_name, bug_id)
    if commit is None:
        print(f"No entry found for table={table_name} and bug_id={bug_id}")
    else:
        print(f"Found commit: {commit}")
        print("Files to check:", files)

        repo_path = os.path.join("/home/ishita/BugLocalization/Data-GHRB/Code corpus",table_name)
        print(f"Code Repository path: {repo_path}")
        results = verify_keywords_in_commit(repo_path, commit, files, keywords)

        for file, hits in results.items():
            print(f"\nFile: {file}")
            for kw, found in hits.items():
                print(f"  {kw}: {'FOUND' if found else 'NOT FOUND'}")
