import os
import subprocess
import xml.etree.ElementTree as ET
import json
import csv

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

def verify_keywords_in_commit(repo_path, commit, files, kw_classes, kw_methods, kw_variables):
    # Track found/not-found per category
    found_classes, not_found_classes = set(), set(kw_classes)
    found_methods, not_found_methods = set(), set(kw_methods)
    found_variables, not_found_variables = set(), set(kw_variables)
    for file_path in files:
        try:
            # Read file content from the given commit without checking out
            cmd = ["git", "-C", repo_path, "show", f"{commit}:{file_path}"]
            completed = subprocess.run(cmd, capture_output=True, text=True, check=True)
            content = completed.stdout

            for kw in kw_classes:
                if kw in content:
                    found_classes.add(kw)
                    not_found_classes.discard(kw)

            for kw in kw_methods:
                if kw in content:
                    found_methods.add(kw)
                    not_found_methods.discard(kw)

            for kw in kw_variables:
                if kw in content:
                    found_variables.add(kw)
                    not_found_variables.discard(kw)

        except subprocess.CalledProcessError:
            print(f"Error: Could not read file {file_path} in commit {commit}.")
            pass    # File not found in commit — skip
         
    return found_classes, not_found_classes, found_methods, not_found_methods, found_variables, not_found_variables

def getKeywords(table_name, bug_id, keyword_path_root):
    # Assuming file path is something like: keywords/<table_name>_<bug_id>.json
    keywords_file = os.path.join(keyword_path_root, table_name, f"{bug_id}.json")
    
    if not os.path.exists(keywords_file):
        # print(f"Keyword file not found: {keywords_file}")
        return [], [], []

    try:
        with open(keywords_file, "r", encoding="utf-8") as f:
            data = json.load(f)

    except json.JSONDecodeError as e:
        print(f"Error parsing JSON for {keywords_file}: {e}")
        return [], [], []

    classes = data.get("classes", [])
    methods = [m["name"] for m in data.get("methods", []) if "name" in m]
    variables = [v["name"] for v in data.get("variables", []) if "name" in v]

    return classes, methods, variables    
    #return ["IntrospectionError", "Optional", "PropertyOrFieldSupport", "getSimpleValue", "ByNameSingleExtractor"] 

def save_results_to_csv(csv_path, project_name, bug_id,
                        kw_classes, kw_methods, kw_variables,
                        found_classes, not_found_classes,
                        found_methods, not_found_methods,
                        found_variables, not_found_variables):

    row = {
        "project_name": project_name,
        "bug_id": bug_id,
        "kw_classes": len(kw_classes),
        "kw_class_hits": len(found_classes),
        "kw_methods": len(kw_methods),
        "kw_method_hits": len(found_methods),
        "kw_variables": len(kw_variables),
        "kw_variable_hits": len(found_variables),
        "list_class_found": json.dumps(sorted(found_classes), ensure_ascii=False),
        "list_class_not_found": json.dumps(sorted(not_found_classes), ensure_ascii=False),
        "list_method_found": json.dumps(sorted(found_methods), ensure_ascii=False),
        "list_method_not_found": json.dumps(sorted(not_found_methods), ensure_ascii=False),
        "list_var_found": json.dumps(sorted(found_variables), ensure_ascii=False),
        "list_var_not_found": json.dumps(sorted(not_found_variables), ensure_ascii=False)
    }
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    # Check if file exists and is non-empty
    write_header = not os.path.exists(csv_path) or os.path.getsize(csv_path) == 0

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        # writer = csv.DictWriter(f, fieldnames=row.keys())
        writer = csv.DictWriter(f, fieldnames=row.keys(), quoting=csv.QUOTE_ALL)

        if write_header:
            writer.writeheader()
        writer.writerow(row)


if __name__ == "__main__":
    table_bug_list = []
    xml_path_root = f"/home/ishita/BugLocalization/Data-GHRB"  # XML file
    repo_path_root = f"/home/ishita/BugLocalization/Data-GHRB/Code corpus"  # Code repository path
    report_group_file = "ReportGroup/ReportGroupLists.txt"  # File containing project, bug_id, category
    keyword_path_root = "BR-PE-Analysis/Keywords"  # Path to keywords JSON files
    result_csv_file = "BR-PE-Analysis/relevancy_results.csv"  # Output CSV file for results

    with open(report_group_file, "r") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) != 3:
                continue  # skip malformed lines
            project, bug_id, category = parts
            if category.strip() != "PE":
                continue  # only process PE category
            table_name = project.replace("GHRB/", "", 1)
            xml_path = f"{xml_path_root}/{table_name}.xml"  # Your XML file
            commit, files = find_commit_and_files(xml_path, table_name, bug_id)
            if commit is None:
                print(f"Commit entry {commit} not found for table={table_name} and bug_id={bug_id}")
            else:
                # print(f"Found commit: {commit}")
                # print("Files to check:", files)

                repo_path = os.path.join(repo_path_root,table_name)
                # print(f"Code Repository path: {repo_path}")
                kw_classes, kw_methods, kw_variables = getKeywords(table_name, bug_id, keyword_path_root)
                if not kw_classes and not kw_methods and not kw_variables:
                    print(f"No keywords found for table={table_name} and bug_id={bug_id}")
                    continue
                results = verify_keywords_in_commit(repo_path, commit, files, kw_classes, kw_methods, kw_variables)
                
                found_classes, not_found_classes, found_methods, not_found_methods, found_variables, not_found_variables = results
                save_results_to_csv(result_csv_file, table_name, bug_id,
                                    kw_classes, kw_methods, kw_variables,
                                    found_classes, not_found_classes,
                                    found_methods, not_found_methods,
                                    found_variables, not_found_variables)
                print(f"******Results saved for {table_name} bug_id={bug_id}*******")

    print(f"Relevancy check completed. Results saved to {result_csv_file}")










        