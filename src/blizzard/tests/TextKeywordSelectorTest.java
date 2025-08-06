package blizzard.tests;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileReader;

import org.junit.Test;

import blizzard.config.StaticData;
import blizzard.query.TextKeywordSelector;

public class TextKeywordSelectorTest {
    @Test
    public void testGetSearchTermsWithCR() {
        int bugID = 77585; // Example bug ID, replace with actual ID as needed
        String repoName = "jdt";
        String fileName = "BR-Raw/" + repoName + "/"+ bugID + ".txt";
        String[] fileData = readFile(fileName);
        String bugReportTitle = fileData[0];
        String reportContent = fileData[1];
        
        System.out.println("debug ongoing for " + bugID);

        TextKeywordSelector kwSelector = new TextKeywordSelector(repoName, bugReportTitle, reportContent,
                StaticData.MAX_NL_SUGGESTED_QUERY_LEN);
        String extended = kwSelector.getSearchTermsWithCR(StaticData.MAX_NL_SUGGESTED_QUERY_LEN);
        System.out.println("Extended Query: " + extended);
    }

    protected String[] readFile(String fileName) {
        StringBuilder content = new StringBuilder();
        	try {
			File f = new File(fileName);
			if (!f.exists()) {
				System.out.println("File does not exist: " + fileName);
			}
			BufferedReader bufferedReader = new BufferedReader(
					new FileReader(f));
			while (bufferedReader.ready()) {
				String line = bufferedReader.readLine().trim();
                content.append(line).append("\n");
			}
			bufferedReader.close();
		} catch (Exception ex) {
			System.out.println("Error opening or reading file: " + fileName);
			//ex.printStackTrace();
		}
        String bugReportTitle = content.toString().split("\n")[0].trim();
        String reportContent = content.toString();

        return new String[] { bugReportTitle, reportContent };
        
    }
}
