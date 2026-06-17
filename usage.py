#!/usr/bin/env python3

from collections import defaultdict
import sys
import os
import subprocess
from re import match

class ModInfo:
    def __init__(self, args=None):
        self.args = args

        self.parseArgs()

    def parseArgs(self):
        if not self.args:
            self.exitHelp()
        if len(self.args) == 1:
            self.exitHelp()
        if self.args[1] in ["-h","--h","help","-help","--help"]:
            self.exitHelp()
        self.files = self.args[1:]
        return

    def exitHelp(self):
        self.prog = self.args[0]
        helpstr = "NAME\n        %s - collect module info\n" % self.prog \
                + "\nSYNOPSIS\n        %s [OPTION]\n" % self.prog \
                + "        %s FILE1 [FILE2] \n" % self.prog \
                + "\nDESCRIPTION\n" \
                + "        Process two files with info about modules usage and print a line by line comparison.\n" \
                + "        Files are the output of parseMod (only lines with module name and module count).\n" \
                + "        Mark modules  used less than once per week for removal. Print comparison on stdout.\n\n" \
                + "        -h, --h, -help, --help, help\n              Print usage info.\n\n" 

        print (helpstr)
        sys.exit(0)

    def verifyFiles(self):
        self.content = {}
        self.weeks = []  # number of files that was processed for modules info
        forder = 0
        for i in self.files:
           txt = self.readModFile(i)
           self.checkLoad(txt, forder)
           forder += 1

    def readModFile(self, fname):
        if not os.path.isfile(fname):
            print("ERROR: %s  is not a  file: " % fname)
            sys.exit(1)
        f = open(fname)
        txt = f.read()
        f.close()
        return txt

    def checkLoad(self,txt,forder):
        lookup0 = "Processed files"
        lookup1 = "module-hpc"
        lookup2 = "Total unique"
        lines = txt.splitlines()
        countLines = 0
        for l in lines:
            if l.find(lookup0) == 0:
                continue
            if l.find(lookup1) > 0:
                countLines += 1
                continue
            if l.find(lookup2) > 0:
                continue
            result = l.split()
            mod = result[0]
            if len(result) == 2:
                count = result[1]
            else:
                count = 0
            if mod in self.content.keys():
                tmpval = self.content[mod]
                tmpval.append(count)
                self.content[mod] = tmpval
            else:
				# processing second file, module was not present in the first
                if forder : 
                    self.content[mod] = [0, count]
				# processing first file,  first time encounter module
                else:
                    self.content[mod] = [count]

        self.weeks.append(countLines)
        return

    def printResult(self):
        for k in self.content.keys():
             # make sure there are two values for each module
             val = self.content[k]
             if len(val) == 1:
                 val.append(0)
             self.content[k] = val

             # marked for removal modules that are used less then once a week
			 # in both processed files
             message = ""
             num1 = int(val[0])
             num2 = int(val[1])
             if num1 < self.weeks[0] and num2 < self.weeks[1]:
                 message = "rm"
             print ("%-65s %10s %10s %s" % (k,val[0],val[1], message))

    def run(self):
        self.verifyFiles()
        self.printResult()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModInfo(sys.argv)
    app.run()
