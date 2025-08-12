package blizzard.bug.report.classification;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;
import blizzard.config.StaticData;

public class BugReportClassifier {

	String reportContent;
	ArrayList<String> traces;
	ArrayList<String> invocations;
	String repoName;
	int bugID;

	public BugReportClassifier(String reportContent, String repoName, int bugID) {
		this.reportContent = reportContent;
		this.repoName = repoName;
		this.bugID = bugID;
		this.traces = new ArrayList<>();
		this.invocations = new ArrayList<>();
	}

	public String determineReportClass() {
		ArrayList<String> traces = extractTraces(this.reportContent);
		if (!traces.isEmpty()) {
			this.traces = traces;
			return "ST";
		} else {
			this.invocations = extractMethodInvocations(this.reportContent);
			if (!invocations.isEmpty()) {
				this.saveInvocations();
				return "PE";
			} else {
				return "NL";
			}
		}
	}

	public ArrayList<String> getTraces() {
		return this.traces;
	}

	protected ArrayList<String> extractMethodInvocations(String bugReport) {
		ArrayList<String> invocations = new ArrayList<>();
		String regex = "((\\w+)?\\.[\\s\\n\\r]*[\\w]+)[\\s\\n\\r]*(?=\\(.*\\))|([A-Z][a-z0-9]+){2,}";
		Pattern p = Pattern.compile(regex);
		Matcher m = p.matcher(bugReport);
		while (m.find()) {
			invocations.add(bugReport.substring(m.start(), m.end()));
		}
		return invocations;
	}

	protected ArrayList<String> extractTraces(String bugReport) {
		ArrayList<String> traces = new ArrayList<>();
		// original regex used in BLIZZARD
		String stackRegex = "(.*)?(.+)\\.(.+)(\\((.+)\\.java:\\d+\\)|\\(Unknown Source\\)|\\(Native Method\\))";
		// modified regex to match stack traces more accurately
		String stackRegexAltered = "([A-Za-z0-9_\\.$<>]+)\\((?:[A-Za-z0-9_]+\\.java:\\d+|Unknown Source|Native Method)\\)";
		
		Pattern p = Pattern.compile(stackRegexAltered);
		Matcher m = p.matcher(bugReport);
		while (m.find()) {
			String entry = bugReport.substring(m.start(), m.end());
			entry = cleanTheEntry(entry);
			traces.add(entry);
		}
		return traces;
	}

	protected String cleanTheEntry(String entry) {
		if (entry.indexOf("at ") >= 0) {
			int atIndex = entry.indexOf("at");
			entry = entry.substring(atIndex + 2).trim();
		}
		if (entry.contains("(")) {
			int leftBraceIndex = entry.indexOf("(");
			entry = entry.substring(0, leftBraceIndex);
		}
		return entry;
	}

	// Save Program Element invocations for each bug report to a file
	protected void saveInvocations() {
		File dir = new File(StaticData.PROGRAM_ELEMENT_DIR + "/" + repoName);
		if (!dir.exists()) {
			dir.mkdirs();
		}
		String invocationFile = dir + "/" + bugID + ".txt";
		try (BufferedWriter writer = new BufferedWriter(new FileWriter(invocationFile))) {
			for (String entry : invocations) {
				writer.write(entry);
				writer.newLine();
			}
		} catch (Exception e) {
			System.err.println("Error writing to file: " + e.getMessage());
		}
	}

}
