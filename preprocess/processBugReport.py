import xml.etree.ElementTree as ET
import os

# This script reads an XML file containing bug reports and writes each report to a separate text file.
# Each file is named after the bug ID and contains the summary and description of the bug.
def dump_bug_reports(xml_path, output_dir, bugIds_file):
    """
    Reads the given XML file and for each <table> entry writes a file
    named <bug_id>.txt in output_dir with the summary and description.
    """

    bug_ids = []
    os.makedirs(output_dir, exist_ok=True)
    
    # Stream‐parse the XML
    context = ET.iterparse(xml_path, events=("end",))    
    for event, elem in context:
        if elem.tag == "table":
            # find the column elements by attribute
            bug_id_el   = elem.find("column[@name='bug_id']")
            summary_el  = elem.find("column[@name='summary']")
            desc_el     = elem.find("column[@name='description']")
            
            if bug_id_el is not None:
                bug_id = bug_id_el.text.strip()
                summary = (summary_el.text or "").strip()
                description = (desc_el.text or "").strip()
                bug_ids.append(bug_id)

                # write to file
                out_path = os.path.join(output_dir, f"{bug_id}.txt")
                if not os.path.exists(out_path):
                    print(f"Writing {out_path}...")
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(summary + "\n\n" + description)
            # clear from memory
            elem.clear()

    # write the bug_ids file (one ID per line)
    with open(bugIds_file, "w", encoding="utf-8") as f:
        for bid in bug_ids:
            f.write(f"{bid}\n")

if __name__ == "__main__":
    project_name = "swt"  # replace with your project name, [aspectj, birt, eclipse, jdt, swt]
    xml_file = f"/home/ishita/BugLocalization/Data-22k/{project_name}-updated-data.xml"         # replace with your XML path
    output_folder = f"/home/ishita/BugLocalization/Data-22k/BR-RAW-Query/{project_name}"    # directory to hold the .txt files
    bugIds_file = f"/home/ishita/BugLocalization/Data-22k/{project_name}_bug_ids.txt"  # file to hold the bug IDs
    dump_bug_reports(xml_file, output_folder, bugIds_file)
    print(f"Processed {len(os.listdir(output_folder))} reports; bug_ids written.") 
    print(f"Written all bug files to ./{output_folder}/")
