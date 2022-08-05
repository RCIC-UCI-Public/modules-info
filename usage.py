#!/usr/bin/env python3

from collections import defaultdict
import sys
import os
import subprocess
from re import match

class ModType:
    def __init__(self,name, path):
        self.name = name
        self.path = path
        self.modules = []
        self.count = 0
        self.loaded = []   # list of loaded modules 
        self.badnames = {} # dictionary where keys are module names per module filenames
                           # and values are module names claimed on logger line
        self.names = []    # modules names
        self.load_distribution = [] # number of prereq modules for each module in self.modules

    def addModule(self, line):
        newmodule = [line]
        self.modules.append(newmodule)
        self.count += 1


    def listModNames(self):
        listmn = []
        for i in self.modules:
            listmn.append(i[0])
        return listmn

    def checkName(self, txt, name):
        line = txt.splitlines()[0]
        line = line.replace('"','',2) # rm quotes if module name was surrounded by by them
        claimedName = line.split()[-1]
        if claimedName == name:
            self.names.append(name)
        else:
            self.badnames[name] = claimedName

    def checkLoad(self,txt):
        load = []
        lookup = "prereq	"
        lines = txt.splitlines()
        for l in lines:
            if l.find(lookup) == 0:
                load.append (l.split(lookup)[1])  # remove 'prereq '
        self.loaded += load
        return (load)

    def verifyModule(self):
        for i in self.modules:
           txt = self.readModFile(i)
           i.append(self.checkLoad(txt))
        self.loaded = list(set(self.loaded))

    def listLoaded(self):
        return self.loaded 

    def modTypeName(self):
        return self.name
 
    def findStats(self):
        for mod in self.modules:
            self.load_distribution.append(len(mod[1]))

    def getStats(self):
        return self.load_distribution

    def printInfo(self):
        print (self.name, self.path[:-1], self.count)
        for mod in self.modules:
            print (mod)

    def printStats(self):
        print ("Modules in %s: %d" % (self.path[:-1], self.count))
        if len(self.badnames):
            print ("    Modules with inconsistent names: %d" % len(self.badnames))
            for mod in self.badnames.items():
                print ("        in file %s:  the name is %s" % mod)

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
                + "\nSYNOPSIS\n        %s FILE1 [FILE2] \n" % self.prog \
                + "\nDESCRIPTION\n" \
                + "        Process one or two files with info about modules usage and print a line by line comparison.\n" \
                + "        Files are the output of parseMod (only lines with module name and module count). Mark modules\n" \
                + "        used < 50 times for removal. When executing on a command line, outputs collected info on stdout.\n\n" \
                + "        -h, --h, -help, --help, help\n              Print usage info.\n\n" 

        print (helpstr)
        sys.exit(0)

    def verifyFiles(self):
        self.content = {}
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
        lrange = []
        lookup0 = "Processed files"
        lookup1 = "  "
        lookup2 = "Total unique"
        lines = txt.splitlines()
        for l in lines:
            if l.find(lookup0) == 0:
                continue
            if l.find(lookup1) == 0:
                continue
            if l.find(lookup2) > 0:
                continue
                lrange.append(i)
            result = l.split()
            mod = result[0]
            if len(result) == 2:
                count = result[1]
            else:
                count = 0
            if mod in self.content.keys():
                old = self.content[mod]
                old.append(count)
                self.content[mod] = old
            else:
                if forder : # processing second file)
                    self.content[mod] = [0, count]
                else:       # processing first file
                    self.content[mod] = [count]
        return

    def printResult(self):
        for k in self.content.keys():
             # make sure there are two values for ecah module
             val = self.content[k]
             if len(val) == 1:
                 val.append(0)
             self.content[k] = val

             # marked for removal modules that are used less then 50 times.
             message = ""
             num1 = int(val[0])
             num2 = int(val[1])
             if num1 < 100 and num2 < 50:
                 message = "rm"
             if num1 < 50 and num2 < 50:
                 message = "rm"
             print ("%-65s %10s %10s %s" % (k,val[0],val[1], message))

    def run(self):
        self.verifyFiles()
        self.printResult()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModInfo(sys.argv)
    app.run()
