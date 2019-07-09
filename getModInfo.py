#!/usr/bin/env python

# For all the modules check (1) which ones use logger and 
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
        self.nologger = [] # list of modules that have no logging
        self.loaded = []   # list of loaded modules 

    def addModule(self, line):
        items = line.split()
        if len(items) == 3:
            newmodule = [items[0], items[1] + " " + items[2]]
        else:
            newmodule = [items[0], items[2] + " " + items[3]]

        self.modules.append(newmodule)
        self.count += 1

    def readModFile(self, mod):
        fname = self.path + mod[0]
        if not os.path.isfile(fname):
            print("ERROR")
            return []
        f = open(fname)
        txt = f.read()
        f.close()
        return txt

    def checkLogging(self,txt, name):
        if txt.find("/bin/logger") > -1 :
            return "True"
        else:
            self.nologger.append(name)
            return "False"

    def listModNames(self):
        listmn = []
        for i in self.modules:
            listmn.append(i[0])
        return listmn

    def checkLoad(self,txt):
        load = []
        lookup = "module load "
        lines = txt.splitlines()
        for l in lines:
            if l.find(lookup) == 0:
                str1 = l.split('#')[0]        # remove comments if any
                str2 = str1.split(lookup)[1]  # remove 'module load '
                load += str2.split()          # account for possible multiple modules on a single line
        self.loaded += load
        return (load)

    def verifyModule(self):
        for i in self.modules:
           txt = self.readModFile(i)
           i.append(self.checkLogging(txt, i[0]))
           i.append(self.checkLoad(txt))
        self.loaded = list(set(self.loaded))
        self.nologger = list(set(self.nologger))

    def listLoaded(self):
        return self.loaded 

    def listNologger(self):
        return self.nologger

    def modTypeName(self):
        return self.name
 
    def printInfo(self):
        print (self.name, self.path, self.count)
        for mod in self.modules:
            print (mod)

class ModInfo:
    def __init__(self):
        self.cmd = ['/data/apps/modules/Modules/%s/bin/modulecmd' % os.environ['MODULE_VERSION'],'python', 'avail', '-lv']
        self.modtypes = [] # list of ModType instances, one per module type: software, bio, mpi, compielrs, etc
        self.nologger = [] # list of modules that have no logging across all module types
        self.loaded = []   # list of loaded modules across all module types

        self.readInfo()

    def readInfo(self):
        '''Parse the output of the 'module avail' command and create a list of ModType instances'''
        p = subprocess.Popen( self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = p.communicate()

        # split string into lines and remove first header line
        self.lines = error.decode('utf-8').splitlines()[1:]

        for l in self.lines:
            if match(r'^\s*$', l): 
                continue # skip empty lines
            if "modulefiles" in l: # add module type
                name = l.split("/")[-1][:-1].lower()
                path = l[:-1] + "/"
                newModType = ModType(name, path)
                self.modtypes.append(newModType)
            else: 
                newModType.addModule(l)  # add module name for the type

    def runCheck(self):
        '''For each ModType instance, parse all modules files and check for logging and loaded modules info'''
        for item in self.modtypes:
            item.verifyModule()
            self.loaded += item.listLoaded()
            self.nologger += item.listNologger()

    def allModLoaded(self):
        '''Return a list of modules that are loaded by any other module'''
        return self.loaded 

    def allModNologger(self):
        '''Return a list of modules that have no logger enabled'''
        return self.nologger

    def printTypes(self):
        '''print info for each ModType'''
        for item in self.modtypes:
            item.printInfo()

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
        self.printTypes()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModInfo()
    app.run()

