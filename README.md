# modules-info
Scripts for parsing modules information on a cluster. 

## Requirements

Python scripts were tested with python from anaconda/3.6-4.3.1
Any version of python 3 will work provided that there are
modules installed:
- graphviz
- itertools

For the examples below assume messages-DATE\*.gz fles are in backup/

## Using scripts

1. **parseMod**     

   Requirements: 
   - imports  classes from getModinfo.py
   
   Parse files provided on a command line and find how many times environment modules were loaded.
   If none provided, will parse /var/log/messages\* files. The output contains 
   - for each used module: a module name and a count of times  it was loaded 
   - a list of modules that were not loaded.
   Output is an ascii file, naming schema  out-parsemod-YYYYMMDD

   Example: run script on all modules-DATE files and redirect output in a file
   ```bash
   ./parseMod -h
   ./parseMod backups/modules* 
   ```
   
   The output file format (cut) :
   ```txt
   ===== Total unique used modules: 965
   gcc/6.4.0                                         6437348
   blcr/0.8.6-3.10.107-1.el6                         3114992
   zlib/1.2.8                                        1647296
   gcc/5.3.0                                          991558
   gcc/4.8.2                                          711689
   ...
   ruby/2.2.2                                              1
   aaa/28                                                  1
   flywheel/8.5.0                                          1
   stata/11                                                1
   
   ===== Total unique unused modules: 620
   Bertini/1.4
   CGAL/4.9.0
   Cluster_Defaults
   EF5/2017.10.18
   ```

1. **getModInfo.py**
   
   Collect information about modules installed on the host using `modules avail`. Checks available
   modules, parses their module files, extracts info about logging, name and loaded modules for each
   category of modules (per MODULEPATH entries). Called as a python module from `parseMod` or `modGraph`.
   When run on a command line, just prints number of modules by category and total number on stdout.
   
   Example: 
   ```bash
   ./getModInfo.py -h
   ./getModInfo.py
   ```
   
   The output file format (cut):
   ```txt
   Modules by catgory
   /opt/rcic/Modules/modulefiles/AI-LEARNING:   3
   /opt/rcic/Modules/modulefiles/BIOTOOLS   :  66
   /opt/rcic/Modules/modulefiles/CHEMISTRY  :  29
   /opt/rcic/Modules/modulefiles/COMPILERS  :  20
   ...
   /opt/rcic/Modules/modulefiles/ENGINEERING:   8
                                       Total: 295
   ```

1. **modGraph.py**
   
   Requirements: 
   - imports classes from getModInfo.py
   - needs `dot` from graphviz  package to create graphics
   - needs graphviz python module
   
   Parse file provided on a command line to get unused modules, if none are
   provided assumes none were unused. List of unused modules is an ascii file, one module name per line,
   comes from running `parseMod` and extracting unused modules. 

   The script checks available modules, parses their modulefiles and  uses info about (1) logging and 
   (2) loading prerequisite to builds a dependecy graph for each category of modules (per MODULEPATH entries).
   
   Example: run script and provide a file with a list of unused modules:
   ```bash
   ./modGraph.py -h
   ./modGraph.py unused
   ```
   The output files are ascii dot files (graphviz description of the graph) and the resulting PNG image, 
   one per each module category which are created in dot-graphs/ in the current directory

   See graph files examples in examples/ in this repo

1. **usage.py**
   
   Process one or two files with info about modules usage and print a line by
   line comparison of what modules are used and how many times. In case of one
   file  values for just that files are listed.  Files are the output of parseMod 
   (abridged). Mark modules used <50 times for removal.  Print result on stdout.

   Example:
   ```bash
   ./usage.py -h
   ./usage.py file1 file2

   Input files format:

   ```txt
   gcc/8.4.0          1269648
   python/3.8.0        835296
   java/1.8.0          527397
   ...
   ```
1. **plotRequests**

   A plotting routine that creates two plots for the requests in RT system.
   Data are hand-collected from RT as number of requests per month
   the first plot shows the distribution of RT tickets vs. sw-related tickets
   the second plot shows side by side monthly sw requests as a bar graph
   Output plots are allRequests.png swRequests.png

   Example:
   ```bash
   ./plotRequests
   ```

## No longer used  scripts  and files

1. **examples/**

   Contains a few dot files and graphs produced by modGraph.py for HPC modules.

1. **xmodl** 
   
   Was used on HPC. Extract lines with `module-hpc` lines from the /var/log/messages-DATE files.
   For each processed messages-DATE file generate an output file modules-DATE.
   If no  arguments are given on the command line assume messages-DATE files
   in the  current directory. 
   
   Example: run script on a specific file. Output is a file `backups/modules-20190721` with extracted lines 
   ```bash
   ./xmodl backups/messages-20190721.gz 
   Wrote backups/modules-20190721
   ```

1. **fixDuplicates**

   Parse module load log files and remove every second (duplicate) line
   Duplicates were due to an error in syslog was recording modules load  twice.
   Affected dates in module-hpc.log-\* files are through 2020 through 2021-05-23.
   No need to use for files created after that.

1. **next-admix**

   Initial old  record of what next software to install.
   Obsoleted by next-lab-software in admixbuilder repo


