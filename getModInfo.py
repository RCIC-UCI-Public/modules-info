#!/usr/bin/env python3

# For all the modules check
# (1) which ones use logger and 
# (2) which ones load other modules 

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

    def readModFile(self, mod):
        fname = self.path + mod[0]
        if not os.path.isfile(fname):
            print("ERROR in file: ", fname)
            return ""
        f = open(fname)
        txt = f.read()
        f.close()
        return txt

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
        print ("%-41s: %3d" % (self.path[:-1], self.count))
        if len(self.badnames):
            print ("    Modules with inconsistent names: %d" % len(self.badnames))
            for mod in self.badnames.items():
                print ("        in file %s:  the name is %s" % mod)

class ModInfo:
    def __init__(self, args=None):
        self.args = args
        self.cmd = ['/usr/bin/modulecmd', 'python', 'avail', '-t', '-v']
        self.modtypes = [] # list of ModType instances, one per module type: biotools, compielrs, etc
        self.loaded = []   # list of loaded modules across all module types
        self.defaultDir = "/opt/rcic/Modules/modulefiles"
        self.total = 0     # number of total modules installed, without user's $HOME 

        self.parseArgs()
        self.readInfo()

    def parseArgs(self):
        if not self.args:
            return
        if len(self.args) == 1:
            return 

        self.prog = self.args[0]
        if self.args[1] in ["-h","--h","help","-help","--help"]:
            self.exitHelp()
        return

    def exitHelp(self):
        helpstr = "NAME\n        %s - collect module info\n" % self.prog \
                + "\nSYNOPSIS\n        %s [OPTION]\n" % self.prog \
                + "\nDESCRIPTION\n" \
                + "        Collect information about modules installed on the host using 'modules avail'. Checks available\n" \
                + "        modules, parses their module files, extracts info about logging, name and loaded modules for each\n" \
                + "        category of modules (per MODULEPATH entries). Called as a python module from parseMod and modGraph.\n" \
                + "        When run on a command line, just prints number of modules by category and total number on stdout.\n\n" \
                + "        -h, --h, --help, help\n              Print usage info.\n\n" 

        print (helpstr)
        sys.exit(0)

    def readInfo(self):
        '''Parse the output of the 'module avail' command and create a list of ModType instances'''
        p = subprocess.Popen( self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = p.communicate()
        
        # split string into lines 
        self.lines = error.decode('utf-8').splitlines()

        for l in self.lines:
            if match(r'^\s*$', l):              # skip empty lines
                continue 
            if l[-1] == ":" :                   # add module type
                name = l.split("/")[-1][:-1].lower()
                path = l[:-1] + "/"
                newModType = ModType(name, path)
                self.modtypes.append(newModType)
            else: 
                newModType.addModule(l)        # add module name for the type

    def runCheck(self):
        '''For each ModType instance, parse all modules files and check for logging and loaded modules info'''
        savemod = []
        for item in self.modtypes:
            if self.defaultDir in item.path:
                savemod.append(item)

        self.modtypes = savemod

        for item in self.modtypes:
            item.verifyModule()
            self.loaded += item.listLoaded()
            self.total += item.count

    def allModLoaded(self):
        '''Return a list of modules that are loaded by any other module'''
        return self.loaded 

    def printModInfo(self):
        '''print info for each ModType'''
        print ("Modules by catgory")
        for item in self.modtypes:
            item.printStats()
        print ("%41s: %3d" % ("Total", self.total))

    def getModNameList(self):
        '''return a list of all modules names'''
        nlist = []
        for item in self.modtypes:
            nlist += item.listModNames()

        return nlist

    def exitError(self):
        print (self.errmsg)
        sys.exit(1)

    def run(self):
        self.runCheck()
        self.printModInfo()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModInfo(sys.argv)
    app.run()
