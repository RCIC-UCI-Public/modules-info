# modules-info
Scripts for parsing modules information on a cluster. 

## Requirements

Python scripts were tested with python from anaconda/3.6-4.3.1
Any version of python 2.7.* or 3.* will work provided that thee are
modules installed :
- graphviz
- itertools

For the examples below assume messages-DATE*.gz fles are in backup/

## Using scripts

1. **xmodl** 
   
   Extract lines with `module-hpc` lines from the /var/log/messages-DATE files.
   For each processed messages-DATE file generate an output file modules-DATE.
   If no  arguments are given on the command line assume messages-DATE files
   in the  current directory. 
   
   Example: run script on a specific file. Output is a file `backups/modules-20190721` with extracted lines 
   ```bash
   ./xmodl backups/messages-20190721.gz 
   Wrote backups/modules-20190721
   ```

1. **parseMod**     

   Requirements: 
   - imports  classes from getModinfo.py
   
   Parse files provided on a command line and find how many times environment modules were loaded.
   If none provided, will parse /var/log/messages* files. The output contains 
   - for each used module: a module name and a count of times  it was loaded 
   - a list of modules that were not loaded.

   NOTE: using unprocessed /var/log/messages files can be slow. Process them first
   with `xmodl` and then run this program on processsed files.
   
   Example: run script on all modules-DATE files and redirect output in a file
   ```bash
   ./parseMod backups/modules* > out-parsemod
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
   ...
   ```

1. **getModInfo.py**
   
   Collect informtion about modules installed on the host using `modules avail`. Checks available
   modules, parses their modulefiles, extracts info about logging, name and loaded modules for each
   category of modules (per MODULEPATH entries). Called as a python module from `parseMod` or `modGraph`.
   When executing on a command line, outputs collected info on stdout.
   
   Example: run script  and redirect output in a file
   ```bash
   ./getModInfo.py > out-getmodinfo
   ```
   
   The output file format (cut):
   ```txt
   ### Modules in /data/modulefiles/SOFTWARE/: 1083
       ### Modules without logging: 1
           Cluster_Defaults
       ### Modules with inconsistent names: 71
                                abaqus/6.20:  abaqus/6.14
                              amber/12-cuda:  amber/amber12-cuda
                               amber/12-mpi:  amber/amber12-mpi
   ...
   
   ### Modules in /data/modulefiles/COMPILERS/: 130
       ### Modules without logging: 51
           acml/gfortran/5.1.0
           acml/gfortran/mp/5.1.0
           acml/ifort/5.1.0
           ...
           acml/open64/5.1.0
                                      
       ### Modules with inconsistent names: 0
   ```

1. **modGraph.py**
   
   Requirements: 
   - imports classes from getModInfo
   - needs `dot` from graphviz  package to create graphics
   - need graphviz python module
   
   Parse file provided on a command line to get unused modules, if none are
   provided assumes none were unused. List of unused modules is an ascii file, one module name per line,
   comes from running `parseMod`. 
   The script checks available modules, parses their modulefiles
   using info about logging and loaded modules and builds a dependecy graph for each
   category of modules (per MODULEPATH entries). The output files (png and graphviz source) are created in
   the dot-graphs/ subdirectory.
   
   Example: run script and provide a file with a list of unused modules (portion of the parseMod output)
   ```bash
   ./modGraph.py unused
   dot: graph is too large for cairo-renderer bitmaps. Scaling by 0.868621 to fit
   No dependencies found for 'bio' modules. Skip making graph
   No dependencies found for 'private_commercial_software' modules. Skip making graph
   ```
   The last 3 ines are the messages from makingpng files with dot.
   
   The output files are raw graphviz descirptino of the graph and the resulting PNG image, one per each module `type`
   are created in dot-graphs/ in the current directory
   ```bash
   ls dot-graphs/
   compilers      linuxbrew      mpi-message_passing_interface      software      user_contributed_software
   compilers.png  linuxbrew.png  mpi-message_passing_interface.png  software.png  user_contributed_software.png
   ```
   
   See graph files examples in examples/ in this repo
