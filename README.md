# BLIZZARD-Generalized

1. created a launch.json file as it needs arguements to pass
2. need to run from "run & debug"
3. created settings.json file to include referenced libraries. ("java.project.referencedLibraries": ["blizzard.lib/**/*.jar"])
4. change HOME_DIR to project root in blizzard/config/StaticData
5. added necessary data and files (BR-RAW folder, tbdata(suffixes, prefixes), corpus(original code), BR-ST-Stack-Trace (needed for report group ST), goldset(Change set for reported bugs, required for evaluation))
6. create lucene index for repos (running IndexLucene.java)
7. copied Lucene-Index2File-Mapping from the original repo



### Query Reformulation for other projects (except the 6 projects used in BLIZZARD)
#### Projects (aspectj, eclipse, birt, jdt)
#### Preprocessing bug reports
1. clone related projects, download bug reports(xml files)
2. run the python file (preprocess/processBugReport.py) modifying file names and folders related to the project (eg. aspectj). It will create a [project] folder containing bug report raw query files named per bug_id. also it will create [project]_bug_ids.txt containing the list of bug ids. keep the raw query folder to (BR-Raw/[project]) and bug ids to (inputs) folder.

3. Creating lucene index of the code files is necessary for the NL-group bug reports as while query reformulation they use lucene index. To create lucene index of the cloned code repository,
    a. Run (preprocess/CodeCorpusGeneration.py) file for processing the codes of [project] and creating corpus for running BLIZZARD.
    b. Modify the source directory, destination directory(eg. Corpus/aspectj) and mapping directory(Lucene-Index2File-Mapping).
    c. This will take the java files only from the repository and copy to destination directory renaming them sequentially, like 1.java, 2.java. (necessary for running lucene as there are some .class files used from ACER that cannot be modified in BLIZZARD)
    d. It will also create a mapping of numbered indices and the original path of coding files, so that the original names can be retrieved later.
    e. Now create Lucene index for [project] code repository running IndexLucene.java. Modify necessary file names. 
4. Create stack-traces files for the bug reports that belongs to the report group ST. 
    a. Modified the loadStackTraces() in TraceLoader.java file to create ST files if not exists. So now no need to run anything else, it will be created automatically while running query reformulation.
    b. Make sure there is folder created (BR-ST-StackTraces/[project]), otherwise it won't make stack traces
    c. However their original BLIZZARD regex failed to detect stack traces for aspectj. so needed to modify the regex in TraceCollector.java file at extractStackTraces method. 
    d. Wrote testCollectTracesFromAspectj() for testing the regex.
    TODO: need to check whether BLIZZARD regex fails for other projects too by running unit test

7. Now create launch settings for [project] run reformulated query for [project]. Inside inputs folder, keep the list of bug ids and inside BR-RAW, there are raw bug report queries

8. Finally run query reformulation. 

Problems:

1. Encountered javaparser.TokenMgrError exceptions for some of java files from corpus. Found reasons
    a. While query reformulation, to created extended query for NL-group bug reports, they scan the java files and find relevant terms for query extension.
    b. Blizzard used blizzard.lib/javaparser-core-2.3.0.jar for parsing java codes. But the old version of Java parser doesn't support text block syntax """...""" .
    b. upgrading javaparser created compatibility issues.
    c. couldn't modify code before parsing as it has used acer.coderank for getting extended query, they used jar files so code cannot be edited.
    d. as a result needed to clean code while generating corpus (preprocess/CodeCorpusGeneration.py). Converted Java text blocks ("""...""") into safe concatenated string literals.
    e. example of exception: for 6776.java file in jdt project creates the following exception: 
        "
        Exception in thread "main" com.github.javaparser.TokenMgrError: Lexical error at line 148, column 46.  Encountered: "\n" (10), after : "\""
        "
        again for bug report 7712 id, 7718.java file got exception.

        Jdt project, bug report id: 77585(NL Group), Java file: 3488.java, 
        Exception: javaparser.TokenMgrError: Lexical error at line 314, column 49.  Encountered: "\n" (10), after "\"\t\t\t 
        case 10: /* "

    f. Some file needed manual intervention. 
        i. TODO: need to check whether manually changed jdt->3373.java(CodeFormatterUtilTest.java)
        

1. Project specific Stack traces
2. Project specific Lucene Index, if lucene index is created manually, it doesn't reproduce the original result for the original projects BLIZZARD used

Problems solved:
1. couldn't git push, as large file detected, solved by git rebase
2. after indexing, query reformulation creating issue, probably because i need to index only java files but i index all type of files like .xml,.pom,.git etc. another problem may be, in original code they named the files like 1.java, 2.java etc, but in my case, the file names are kept as it is. need to figure out this

Not in Github repo because of size issue (code to reproduce is described above)
1. Corpus
2. Lucene-Index 
