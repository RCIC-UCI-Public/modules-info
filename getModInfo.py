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

    def checkLogging(self,txt):
        if txt.find("/bin/logger") > -1 :
            return "True"
        else:
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
                load.append(str2.strip())     # remove any white spaces around
            
        return (load)

    def verifyModule(self):
        for i in self.modules:
           txt = self.readModFile(i)
           i.append(self.checkLogging(txt))
           i.append(self.checkLoad(txt))

    def printInfo(self):
        print (self.name, self.path, self.count)
        for mod in self.modules:
            print (mod)

class ModInfo:
    def __init__(self):
        self.cmd = ['/data/apps/modules/Modules/%s/bin/modulecmd' % os.environ['MODULE_VERSION'],'python', 'avail', '-lv']
        self.modtypes = []   # lsit of ModType objects, one per module type (software, bio, mpi, compielrs, etc)

        self.readInfo()

    def readInfo(self):
        p = subprocess.Popen( self.cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = p.communicate()
        # split string into lines and remove first header line
        self.lines = error.decode('utf-8').splitlines()[1:]
        for l in self.lines:
            if match(r'^\s*$', l): 
                continue # line is empty
            if "modulefiles" in l:
                name = l.split("/")[-1][:-1].lower()
                path = l[:-1] + "/"
                newModType = ModType(name, path)
                self.modtypes.append(newModType)
            else: 
                newModType.addModule(l)

    def runCheck(self):
        for item in self.modtypes:
            item.verifyModule()

    def printTypes(self):
        for item in self.modtypes:
            item.printInfo()

    def getModNameList(self):
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

