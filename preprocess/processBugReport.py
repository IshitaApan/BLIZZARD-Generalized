import xml.etree.ElementTree as ET
import os

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
    # xml_file = "/home/ishita/BugLocalization/Data-22k/aspectj-updated-data.xml"         # replace with your XML path
    # output_folder = "//home/ishita/BugLocalization/Data-22k/BR-RAW-Query/aspectj"    # directory to hold the .txt files
    # bugIds_file = "/home/ishita/BugLocalization/Data-22k/aspectj_bug_ids.txt"  # file to hold the bug IDs

    xml_file = "/home/ishita/BugLocalization/Data-22k/birt-updated-data.xml"         # replace with your XML path
    output_folder = "/home/ishita/BugLocalization/Data-22k/BR-RAW-Query/birt"    # directory to hold the .txt files
    bugIds_file = "/home/ishita/BugLocalization/Data-22k/birt_bug_ids.txt"  # file to hold the bug IDs
    dump_bug_reports(xml_file, output_folder, bugIds_file)
    print(f"Written all bug files to ./{output_folder}/")
    print(f"Processed {len(os.listdir(output_folder))} reports; bug_ids written.") 

# This script reads an XML file containing bug reports and writes each report to a separate text file.
# Each file is named after the bug ID and contains the summary and description of the bug.
# Ensure the XML file path and output directory are correctly set before running the script.
# The script uses the ElementTree library to parse the XML and extract relevant data.
# It creates the output directory if it does not exist and handles cases where elements may be missing.
# The output files are encoded in UTF-8 to handle any special characters in the bug reports