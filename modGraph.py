#!/usr/bin/env python

# Make a graph of module dependencies , one per module type
# which corresponseds to entries in MODULEPATH

import os
import sys
import itertools
from getModInfo import ModInfo, ModType

class  ModGraph:
    def __init__(self, args):
        self.prog = os.path.basename(args[0])
        self.args = args[1:]     # command line arguments
        self.modinfo = None      # avail modules info
        self.unused = []         # list of unused modules, get from the input file
        self.gdir = "dot-graphs" # directory for saving  graphviz source and figure files
        self.render = 'png'      # rendering output format
        self.nologger = []       # list of modules that do not call logger

        self.parseArgs()

    def exitError(self):
        print (self.errmsg)
        sys.exit(1)

    def exitHelp(self):
        helpstr = "NAME\n        %s - create module dependencies graphs\n" % self.prog \
                + "\nSYNOPSIS\n        %s [OPTION] [FILE]\n" % self.prog \
                + "\nDESCRIPTION\n        Parse FILE provided on a command line to get unused modules, if none\n" \
                + "        provided assumes none were unused. Checks available modules, parse their modulefiles\n" \
                + "        using info about logging and loaded modules and and build a dependecy graph for each\n" \
                + "        category of modules (per MODULEPATH entries).\n\n" \
                + "        -h, --h, --help, help\n              Print usage info.\n\n" \
                + "        NOTE: this program requires python module graphviz and RPM graphviz (for dot) to be installed.\n "
        print (helpstr)
        sys.exit(0)

    def parseArgs(self):
        if self.args == []:
            self.file = None
        elif self.args[0] in ["-h","--h","help","-help","--help"]:
            self.exitHelp()
        else:
            if os.path.isfile(self.args[0]):
                self.file = self.args[0]
                self.checkUnused()

    def checkUnused(self):
        f = open(self.file)
        txt = f.read()
        f.close()
        self.unused = txt.split()
        self.unused.sort()

    def getInfo(self):
        self.modinfo = ModInfo()
        self.modinfo.runCheck()
        self.nologger = self.modinfo.allModNologger()

    def findNodesEdges(self, mtype):
        havenodes = False
        self.nodes = [] # graph node names list
        self.edges = [] # graph edges from->to
        # mod = ['name/version', 'time stamp', 'logging is True|False', [dependend modules if any]]
        for mod in mtype.modules:
            if len(mod[3]):
                self.nodes.append(mod[0])
                self.nodes += mod[3]
                for i in mod[3]:
                    self.edges.append([mod[0],i])

        # no dependendcies found, don't build graph
        if not self.nodes: 
            print ("No dependednices found for '%s' modules. Skip making graph" % mtype.name)
            return havenodes
        havenodes = True

        # remove duplicate nodes and sort 
        self.nodes = list(set(self.nodes))
        self.nodes.sort()

        # remove duplicates and sort edges by its key value
        self.edges = list(self.edges for self.edges,_ in itertools.groupby(self.edges))

        return havenodes

    def addNodes(self, color1, color2):
        # add graph nodes per module names
        for n in self.nodes:
            if n in self.nologger: 
                self.g.node(n, fillcolor=color1, style='filled')
            elif n in self.unused:
                self.g.node(n, fillcolor=color2, style='filled')
            else:
                self.g.node(n)

    def addEdges(self):
        # add graph edges per loaded modules dependencies 
        for e in self.edges:
            self.g.edge(e[0], e[1])

    def addLegend(self, name, color1, color2, color3):
        # create legend  and set its attributes
        self.c.attr(label="Color legend for '%s' modules" % name, fontsize='18', fontname="Numbus-Roman")
        self.c.attr(color='snow2')
        self.c.attr(style='filled')

        # define legend nodes
        label1 = "module without logging"
        label2 = "module unused"
        self.c.node(label1, fillcolor=color1)
        self.c.node(label2, fillcolor=color2)
        self.c.node("A", fillcolor=color3)
        self.c.node("B", fillcolor=color3)

        # line all nodes on one level
        self.c.edge(label2, label1)

        # dont draw lines between nodes
        self.c.edge_attr['style'] = 'invis'

        # use colored box for the node
        self.c.node_attr['style'] = 'filled'

        # add edge explanation
        self.c.edge("A","B",style="bold", label="A loads B")

        # add legend as a subgraph
        self.g.subgraph(self.c)

    def makeGraph(self, mtype):
        from graphviz import Digraph
        color1 = 'lightsalmon1'
        color2 = 'lightblue1'
        color3 = 'white'
        # create a graph object for saving in files names per  modules type
        self.g = Digraph(filename=mtype.name, directory=self.gdir, format=self.render)
        self.g.graph_attr['rankdir'] = 'LR'
 
        # add nodes and edges
        if not self.findNodesEdges(mtype):
            return
        self.addNodes(color1, color2)
        self.addEdges()

        # create legend subgraph 
        self.c = Digraph('clusterLegend')
        self.addLegend(mtype.modTypeName(), color1, color2, color3)

        # output graph source  and figure  files
        self.g.render(view=False) 

    def makeGraphType(self):
        if not self.modinfo:
            return  # no info about modules

        for item in self.modinfo.modtypes:
            self.makeGraph(item)

    def run(self):
        self.getInfo()
        self.makeGraphType()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModGraph(sys.argv)
    app.run()
