package blizzard.bug.report.classification;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;
import blizzard.config.StaticData;
import blizzard.utility.BugReportLoader;
import blizzard.utility.ContentLoader;

public class TraceLoader {

	public static ArrayList<String> loadStackTraces(String repoName, int bugID) {
		ArrayList<String> straces = new ArrayList<>();

			String traceFile = StaticData.STACK_TRACE_DIR + "/" + repoName + "/" + bugID + ".txt";
			File tFile = new File(traceFile);
			if (tFile.exists()) {
				try {
					// Load the stack traces from the file
					straces = ContentLoader.getAllLinesList(traceFile);
				} catch (Exception e) {
					System.err.println("Error reading stack trace file: " + e.getMessage());
				}
			}
			else {
				System.err.println("No stack trace file found for " + repoName + " bug ID: " + bugID);
				
				String bugReport = BugReportLoader.loadBugReport(repoName, bugID);
				TraceCollector traceCollector = new TraceCollector(null);
				straces = traceCollector.extractStackTraces(bugReport);
				// if the directory does not exist, create it
				File dir = new File(StaticData.STACK_TRACE_DIR + "/" + repoName);
				if (!dir.exists()) {
					dir.mkdirs();
				}
				// write code to Save the extracted stack traces to a file
				try (BufferedWriter writer = new BufferedWriter(new FileWriter(tFile))) {
					for (String entry : straces) {
						writer.write(entry);
						writer.newLine();
					}
				} catch (Exception e) {
					System.err.println("Error writing to file: " + e.getMessage());
				}
				System.err.println("Created stack trace file: " + StaticData.STACK_TRACE_DIR + "/" + repoName + "/" + bugID + ".txt");
			}
		return straces;
	}

}
