#!/usr/bin/env python

# Make a graph of module dependencies , one per module type
# which corresponseds to entries in MODULEPATH

import os
import sys
import itertools
from graphviz import Digraph
from getModInfo import ModInfo, ModType

class  ModGraph:
    def __init__(self, args):
        self.args = args[1:]     # command line arguments
        self.modinfo = None      # avail modules info
        self.unused = []         # list of unused modules, get from the input file
        self.gdir = "dot-graphs" # directory for saving  graphviz source and figure files
        self.render = 'png'      # rendering output format
        self.nologger = []      # list of modules that do not call logger

        self.parseArgs()

    def exitError(self):
        print (self.errmsg)
        sys.exit(1)

    def parseArgs(self):
        # TODO arguments 
        if self.args == []:
            self.file = None
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
            if n in self.unused:
                if n in self.nologger: 
                    self.g.node(n, fillcolor=color1, style='filled')
                else:
                    self.g.node(n, fillcolor=color2, style='filled')
            else:
                self.g.node(n)

    def addEdges(self):
        # add graph edges per loaded modules dependencies 
        for e in self.edges:
            self.g.edge(e[0], e[1])

    def addLegend(self, name, color1, color2, color3):
        # create legend  and set its attributes
        c = Digraph('clusterLegend')
        c.attr(label="Color legend for '%s' modules" % name, fontsize='18', fontname="Numbus-Roman")
        c.attr(color='snow2')
        c.attr(style='filled')

        # define legend nodes
        label1 = "module without logging"
        label2 = "module unused"
        label3 = "module name"
        c.node(label1, fillcolor=color1)
        c.node(label2, fillcolor=color2)
        c.node(label3, fillcolor=color3)

        # line all nodes on one level
        c.edge(label3, label2)
        c.edge(label2, label1)

        # dont draw lines between nodes
        c.edge_attr['style'] = 'invis'

        # use colored box for the node
        c.node_attr['shape'] = 'none'
        c.node_attr['style'] = 'filled'

        # add legend as a subgraph
        self.g.subgraph(c)

    def makeGraph(self, mtype):
        color1 = 'lightsalmon1'
        color2 = 'lightblue1'
        color3 = 'white'
        # create a graph object for saving in files names per  modules type
        self.g = Digraph(filename=mtype.name, directory=self.gdir, format=self.render)
        self.g.graph_attr['rankdir'] = 'LR'
 
        if not self.findNodesEdges(mtype):
            return
        self.addNodes(color1, color2)
        self.addEdges()
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
