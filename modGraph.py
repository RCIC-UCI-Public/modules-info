#!/usr/bin/env python

# Make a graph of module dependencies , one per module type
# which corresponseds to entries in MODULEPATH

import os
import sys
import itertools
from graphviz import Digraph
from getModInfo import ModType, ModInfo

class  ModGraph:
    def __init__(self, args):
        self.args = args[1:]          # command line arguments
        self.parseArgs()
        self.name = "compilers"
        self.modinfo = None

        self.parseArgs()

    def exitError(self):
        print (self.errmsg)
        sys.exit(1)

    def parseArgs(self):
        return

    def getModInfo(self):
        self.modinfo = ModInfo()
        self.modinfo.runCheck()

    def makeGraph(self, mtype):
        nodes = []
        edges = []
        for mod in mtype.modules :
            if len(mod[3]) :
                nodes.append(mod[0])
                nodes += mod[3]
                for i in mod[3]:
                    edges.append([mod[0],i])

        #remove duplicates
        nodes = list(set(nodes))
        edges.sort()
        edges = list(edges for edges,_ in itertools.groupby(edges))

        gname = mtype.name + ".gv"
        g = Digraph(format='png')
        g.graph_attr['rankdir'] = 'LR'

        for n in nodes:
            g.node(n)

        for e in edges:
            g.edge(e[0], e[1])
        g.render(gname, view=False) 


    def findType(self, name):
        for item in self.modinfo.modtypes:
            if item.name == self.name:
                self.makeGraph(item)

    def run(self):
        self.getModInfo()
        self.findType(self.name)

##### Run from a command line #####
if __name__ == "__main__":
    app = ModGraph(sys.argv)
    app.run()

