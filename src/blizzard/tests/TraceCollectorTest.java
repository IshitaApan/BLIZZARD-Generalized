package blizzard.tests;

import static org.junit.Assert.assertNotNull;

import java.io.BufferedWriter;
import java.io.File;
import java.io.FileWriter;
import java.util.ArrayList;
import java.util.regex.Matcher;
import java.util.regex.Pattern;

import org.junit.Test;
import blizzard.bug.report.classification.TraceCollector;
import blizzard.bug.report.classification.TraceLoader;
import blizzard.config.StaticData;
import blizzard.utility.BugReportLoader;

public class TraceCollectorTest {

	@Test
	public void testCollectTraces() {
		String repoName = "eclipse.jdt.core";
		int bugID = 380048;
		String bugReport = BugReportLoader.loadBugReport(repoName, bugID);
		TraceCollector traceCollector = new TraceCollector(null);
		ArrayList<String> entries = traceCollector.extractStackTraces(bugReport);
		System.out.println(entries);
		assertNotNull(entries);
	}

	@Test
	public void testCollectTracesFromAspectj() {
		String repoName = "birt";
		int bugID = 103106; // birt: 103106 // aspectj: 220172
		String bugReport = BugReportLoader.loadBugReport(repoName, bugID);

		ArrayList<String> traces = new ArrayList<>();
		String stackRegexBlizzard = "(.*)?(.+)\\.(.+)(\\((.+)\\.java:\\d+\\)|\\(Unknown Source\\)|\\(Native Method\\))";
		//String stackRegexAltered = "([A-Za-z0-9_\\.$<>]+)\\((?:[A-Za-z0-9_]+\\.java:\\d+|Unknown Source|Native Method)\\)";
		
		Pattern p = Pattern.compile(stackRegexBlizzard);
		Matcher m = p.matcher(bugReport);
		while (m.find()) {
			String entry = bugReport.substring(m.start(), m.end());
			entry = cleanTheEntry(entry);
			traces.add(entry);
		}

		String traceFile = "src/blizzard/tests/" + repoName + "/" + bugID + "_Blizzard.txt";
		File file = new File(traceFile);
		try (BufferedWriter writer = new BufferedWriter(new FileWriter(file))) {
			for (String entry : traces) {
				writer.write(entry);
				writer.newLine();
			}
		} catch (Exception e) {
			System.err.println("Error writing to file: " + e.getMessage());
		}

		System.out.println(traces);
		assertNotNull(traces);
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

	@Test
	public void testCollectTraceEntries() {
		String repoName = "eclipse.jdt.core";
		int bugID = 88845;
		String traceFile = StaticData.STACK_TRACE_DIR + "/" + repoName + "/" + bugID;
		TraceCollector traceCollector = new TraceCollector(traceFile);
		assertNotNull(traceCollector.collectTraceEntries());
	}
	
	@Test
	public void testTraceLoader() {
		String repoName = "eclipse.jdt.core";
		int bugID = 384317;
		assertNotNull(TraceLoader.loadStackTraces(repoName, bugID)); 
	}

}
