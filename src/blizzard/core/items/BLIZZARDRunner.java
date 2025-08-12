package blizzard.core.items;

import java.io.File;
import java.util.ArrayList;
import java.util.HashMap;
import blizzard.utility.ContentWriter;
import blizzard.query.BLIZZARDQueryManager;
import blizzard.query.evaluation.BLIZZARDResultProvider;
import blizzard.query.evaluation.ReportedPerformanceProvider;
import blizzard.config.StaticData;

public class BLIZZARDRunner {

	public static void saveItems(String outputFile,
			HashMap<Integer, String> suggestedQueries) {
		ArrayList<String> results = new ArrayList<>();
		for (int bugID : suggestedQueries.keySet()) {
			String line = bugID + "\t" + suggestedQueries.get(bugID);
			results.add(line);
		}
		ContentWriter.writeContent(outputFile, results);
	}
	public static void appendItems(String outputFile,
			ArrayList<String> content) {
		
		ContentWriter.appendContent(outputFile, content);
	}

	public static void saveItemList(String outputFile,
			HashMap<Integer, ArrayList<String>> resultMap) {
		ArrayList<String> results = new ArrayList<>();
		for (int bugID : resultMap.keySet()) {
			ArrayList<String> ranked = resultMap.get(bugID);
			int index = 0;
			for (String file : ranked) {
				String line = bugID + "\t" + file + "\t" + index;
				results.add(line);
				index++;
			}
		}
		ContentWriter.writeContent(outputFile, results);
	}

	public static void main(String[] args) {
		
		long start = System.currentTimeMillis();
		if (args.length == 0) {
			System.out
					.println("Please check README, and enter your arguments.");
			return;
		}

		HashMap<String, String> keymap = new HashMap<>();
		for (int i = 0; i < args.length; i += 2) {
			String key = args[i];
			String value = args[i + 1];
			keymap.put(key, value);
		}

		String task = null;
		if (keymap.containsKey("-task")) {
			task = keymap.get("-task");

			String repoName = null;
			String queryFile = null;
			String resultFile = null;
			String bugIDFile = null;
			String reportKey = null;
			int topk = 10;

			switch (task) {

			case "classifyReport":
				String repo_dir = "BR-Raw/GHRB";
				// Create a File object from the provided directory path.
				File directory = new File(repo_dir);
				// Check if the file exists and is a directory.
				if (!directory.exists()) {
					System.out.println("Error: The directory '" + repo_dir + "' does not exist.");
					return;
				}
				// Get a list of all files and sub-folders in the directory.
        		File[] allItems = directory.listFiles();
				for (File item : allItems) {
					// Check if the current item is a directory.
					if (item.isDirectory()) {
						repoName = "GHRB/" + item.getName();
						bugIDFile = "inputs/" + repoName + "_bug_ids.txt";
						System.out.println(repoName);
						if (!repoName.isEmpty() && !bugIDFile.isEmpty()) {
							BLIZZARDQueryManager queryManager = new BLIZZARDQueryManager(
									repoName, bugIDFile);
							ArrayList<String> suggestedReportClassList = queryManager.getSuggestedReportGroup();
							appendItems(StaticData.ReportGroup_File, suggestedReportClassList);
						}
					}
				}
				break;
			case "reformulateQuery":
				if (keymap.containsKey("-repo")) {
					repoName = keymap.get("-repo");
				} else {
					System.out
							.println("Please enter a project name (e.g., ecf)");
					return;
				}
				if (keymap.containsKey("-bugIDFile")) {
					bugIDFile = keymap.get("-bugIDFile");
				} else {
					System.out.println("Please enter your bug IDs in a file.");
				}

				if (keymap.containsKey("-queryFile")) {
					queryFile = keymap.get("-queryFile");
				} else {
					System.out.println("Please enter your query file.");
				}

				if (!repoName.isEmpty() && !bugIDFile.isEmpty()
						&& !queryFile.isEmpty()) {
					BLIZZARDQueryManager queryManager = new BLIZZARDQueryManager(
							repoName, bugIDFile);
					HashMap<Integer, String> suggestedQueries = queryManager
							.getSuggestedQueries();
					saveItems(queryFile, suggestedQueries);
				}
				break;
			case "getResult":
				if (keymap.containsKey("-repo")) {
					repoName = keymap.get("-repo");
				} else {
					System.out
							.println("Please enter a project name (e.g., ecf)");
					return;
				}
				if (keymap.containsKey("-queryFile")) {
					queryFile = keymap.get("-queryFile");
				} else {
					System.out.println("Please enter the query file.");
				}
				if (keymap.containsKey("-topk")) {
					topk = Integer.parseInt(keymap.get("-topk"));
				} else {
					System.out
							.println("Please enter a Top-K value. Default Top-K = 10");
				}
				if (keymap.containsKey("-resultFile")) {
					resultFile = keymap.get("-resultFile");
				} else {
					System.out.println("Please enter your result file.");
				}

				if (topk <= 10) {
					if (!repoName.isEmpty() && !queryFile.isEmpty()
							&& !resultFile.isEmpty()) {
						BLIZZARDResultProvider bprovider = new BLIZZARDResultProvider(
								repoName, topk, queryFile);
						HashMap<Integer, ArrayList<String>> results = bprovider
								.collectBLIZZARDResults();
						bprovider.calculateBLIZZARDPerformance(results);
						saveItemList(resultFile, results);
					}
				} else if (topk == 100000) {
					if (!repoName.isEmpty() && !queryFile.isEmpty()
							&& !resultFile.isEmpty()) {
						BLIZZARDResultProvider bprovider = new BLIZZARDResultProvider(
								repoName, topk, queryFile);
						HashMap<Integer, ArrayList<String>> results = bprovider
								.collectBLIZZARDResultsAll();
						saveItemList(resultFile, results);
					}
				} else {
					System.out.println("Please enter K<=10 or K=100000");
				}
				break;

			case "getReportedBLPerformance":
				if (keymap.containsKey("-reportKey")) {
					reportKey = keymap.get("-reportKey");
				}
				if (keymap.containsKey("-topk")) {
					topk = Integer.parseInt(keymap.get("-topk"));
				} else {
					System.out
							.println("Please enter a Top-K value. Default Top-K = 10");
				}
				ReportedPerformanceProvider rpProvider = new ReportedPerformanceProvider(
						reportKey);
				rpProvider.determineRetrievalPerformance(topk);
				break;

			case "getReportedQEPerformance":
				if (keymap.containsKey("-reportKey")) {
					reportKey = keymap.get("-reportKey");
				}
				ReportedPerformanceProvider rpProvider2 = new ReportedPerformanceProvider(
						reportKey);
				rpProvider2.determineQE();
				break;

			default:
				break;
			}

		}
		long end = System.currentTimeMillis();
		System.out.println("Time elapsed:" + (end - start) / 1000 + " seconds");
	}
}
