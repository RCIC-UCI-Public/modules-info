#!/usr/bin/env python

# Make a graph of module dependencies , one per module type
# which corresponseds to entries in MODULEPATH

import os
import sys

# reset path so can  import the module
sys.path.insert(0, os.path.dirname(sys.argv[0]))
from getModInfo import ModInfo, ModType

if sys.version_info.major < 3:
    print ("Please use Python 3 to run this program")
    print ("Your default python is %s" % sys.version.split()[0])
    sys.exit()

import itertools
from graphviz import Digraph

class  ModGraph:
    def __init__(self, args):
        self.prog = os.path.basename(args[0])
        self.args = args[1:]     # command line arguments
        self.modinfo = None      # avail modules info
        self.unused = []         # list of unused modules, get from the input file
        self.gdir = "dot-graphs" # directory for saving  graphviz source and figure files
        self.render = 'png'      # rendering output format
        self.nologger = []       # list of modules that do not call logger
        self.deps = {}           # dependency dictionary, where key is a module and a value
                                 # is a dictionary of modules that depend on it, i.e.1
                                 # python/2.7.17 : {'biotools': ['bowtie2/2.4.1'], 'genomics': ['rMATS/4.0.2']}

        self.colorNode = 'white'             # regular node 
        self.colorUnused = 'lightsteelblue1' # unused  node 
        self.fontLegend = 'royalblue3'       # legend font
        self.colorLegend = 'royalblue3'      # legend color
        self.colorBackground = 'ghostwhite'  # legend background

        self.parseArgs()

    def exitError(self):
        print (self.errmsg)
        sys.exit(1)

    def exitHelp(self):
        helpstr = "NAME\n        %s - create module dependencies graphs\n" % self.prog \
                + "\nSYNOPSIS\n        %s [OPTION] [FILE]\n" % self.prog \
                + "\nDESCRIPTION\n        Parse FILE provided on a command line to get unused modules, if none\n" \
                + "        provided assumes none were unused. Checks available modules, parse their modulefiles\n" \
                + "        using info about logging and loaded modules and build a dependecy graph for each\n" \
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

        # mod is an array ['name/version', 'logging as True|False', [dependend modules if any]]
        for mod in mtype.modules:
            self.nodes.append(mod[0])
            if len(mod[2]):
                self.nodes += mod[2]
                for i in mod[2]:
                    self.edges.append([mod[0],i])

        # found no dependendcies, don't build graph
        if not self.nodes: 
            print ("No dependencies found for '%s' modules. Skip making graph" % mtype.name)
            return havenodes
        havenodes = True

        # remove duplicate nodes and sort 
        self.nodes = list(set(self.nodes))
        self.nodes.sort()

        # remove duplicates and sort edges by its key value
        self.edges = list(self.edges for self.edges,_ in itertools.groupby(self.edges))

        return havenodes

    def addNodes(self ):
        """ add graph nodes per module names """

        # modules that load another module or are loaded by another module
        endpoints = set(list(itertools.chain(*self.edges)))
        solitary = []

        for n in self.nodes:
            if n in endpoints:
                if n in self.unused:
                    self.g.node(n, fillcolor=self.colorUnused, color=self.colorUnused, style='filled')
                else:
                    self.g.node(n)
            else:
                solitary.append(n)
        self.addSolitaryNodes(solitary) 

    def addSolitaryNodes(self, names):
        """ This adds standalone modules (not loading others and not loaded by others)
            Make an artifical grouping and edges  so that  the resulting graph
            has 3 such modules per row, sinmply to make the graph a bit more dense
        """
        n = 3
        args = [iter(names)] * n
        nargs = itertools.zip_longest(*args, fillvalue=None)
        for i in nargs:
            if i[1]:
                self.g.edge(i[0],i[1], style="invis")
            if i[2]:
                self.g.edge(i[1],i[2], style="invis")
            for j in i:
                if j in self.unused:
                    self.g.node(j, fillcolor=self.colorUnused, color=self.colorUnused, style='filled')


    def addEdges(self):
        # add graph edges per loaded modules dependencies 
        for e in self.edges:
            self.g.edge(e[0], e[1])

    def addLoadLegend(self, name):
        # legend subgraph
        self.c = Digraph('clusterLegend')
        self.c.attr(label="Legend for %s modules" % name.upper())
        self.c.attr(fontsize='18', fontname="Numbus-Roman", fontcolor=self.fontLegend)
        self.c.attr(color=self.colorBackground)
        self.c.attr(style='filled')

        # use colored box for the node
        self.c.node_attr['style'] = 'filled'

        # legend nodes and edges
        self.c.node("A", fillcolor=self.colorNode)
        self.c.node("B", fillcolor=self.colorNode)
        self.c.edge("A","B", label="A loads  B")

        self.c.node("C", fillcolor=self.colorUnused, color=self.colorUnused)
        self.c.node("D", label="", style="", shape="none")
        self.c.edge("C","D",style="", label="unused module")

        # self.c.edge_attr['style'] = 'invis' # dont draw lines between nodes

        # add legend as a subgraph
        self.g.subgraph(self.c)

    def writeLoadGraph(self, mtype):
        if not self.findNodesEdges(mtype):
            return
        print ("Processing %s modules" % mtype.modTypeName())
        # create a graph object for saving in files per modules type
        self.g = Digraph(filename=mtype.name, directory=self.gdir, format=self.render)
        self.g.graph_attr['rankdir'] = 'LR'
        self.g.graph_attr['center'] = 'true'
        
        self.g.edge_attr['arrowsize'] = '0.5'
        self.g.edge_attr['arrowhead'] = 'vee'
        self.g.node_attr['shape'] = 'record'
        self.g.node_attr['color'] = self.colorUnused

        # add nodes and edges
        self.addNodes()
        self.addEdges()

        # create legend subgraph 
        self.addLoadLegend(mtype.modTypeName())

        # output graph source  and figure  files
        self.g.render(view=False) 

    def makeLoadGraph(self):
        if not self.modinfo:
            return  # no info about modules

        for item in self.modinfo.modtypes:
            self.writeLoadGraph(item)
            #item.printInfo() # for debugging

    def makeDependGraph(self):
        if not self.deps:
            return  # no info about modules

        # ordered dict:
        # key - module X name, value - number of categories where modules depend on module X
        temp={}
        for key,val in self.deps.items():
            temp[key] = len(val)
        orderDict = {k: v for k, v in sorted(temp.items(), key=lambda item: item[1], reverse=True)}

        # reverse of ordered dict:
        # key - number of categories where modules depend on a module X, value - module X name
        reverseDict = {}
        for key, value in orderDict.items():
            if value not in reverseDict:
                reverseDict[value] = [key]
            else:
                reverseDict[value].append(key)
        # create graphs
        for num, modnames in reverseDict.items():
            self.writeDependGraph(num, modnames)

    def writeDependGraph(self, num, modnames):
        print ("Processing modules with dependencies in %d categories" % num)
        # create a graph object 
        self.g = Digraph(filename="dependency-%s" % num, directory=self.gdir, format=self.render)
        self.g.graph_attr['rankdir'] = 'LR'
        self.g.graph_attr['center'] = 'true'
        self.g.node_attr['shape'] = 'none'

        self.g.edge_attr['arrowsize'] = '0.5'
        self.g.edge_attr['arrowhead'] = 'vee'

        # add subgraphs by category
        self.addDependSubGraph(modnames)

        # create legend subgraph 
        self.addDependLegend(num)

        # output graph source and image files
        self.g.render(view=False) 

    def addDependSubGraph(self, modnames):
        cats = {} # dict of modules by categories for all modules in modnames
        # add nodes and edges
        for mod in modnames:
            # find nodes
            dictdeps = self.deps[mod]
            nodes = []
            for key, val in dictdeps.items():
                nodes += val
                # update category with modules
                if key in cats:
                    cats[key] += val
                else:
                    cats[key] = val
            # find edges
            for n in nodes:
                self.g.edge(mod, n)

        # add categories as subgraphs
        i = 0  # counter, need for naming subgraphs
        for key, val in cats.items():
            subG = Digraph("cluster%s" % i)
            subG.attr(label= key.upper())
            subG.attr(fontsize='16', fontname="Numbus-Roman", fontcolor=self.fontLegend)
            subG.attr(color=self.colorBackground)
            subG.attr(style='filled')
            for n in val: 
                if n in self.unused:
                    subG.node(n, fillcolor=self.colorUnused, color=self.colorUnused, style='filled')
                else:
                    subG.node(n)
            i += 1
            self.g.subgraph(subG)

    def addDependLegend(self, num):
        self.c = Digraph('clusterLegend')
        # legend title
        self.c.attr(label="Modules dependency")
        self.c.attr(fontsize='18', fontname="Numbus-Roman", fontcolor=self.fontLegend)
        self.c.attr(color=self.fontLegend)

        # legend nodes and edges
        self.c.node("A")
        self.c.node("B")
        self.c.node("C")
        self.c.node("D", fillcolor=self.colorUnused, color=self.colorUnused, style="filled")
        self.c.edge("A","B", label="A is required for B")
        self.c.edge("C","D",style="", label="C is requred by an unused module D")

        # add legend as a subgraph
        self.g.subgraph(self.c)

    def getGraphDependency(self):
        if not self.modinfo:
            return  # no info about modules

        isdep = {}
        for item in self.modinfo.modtypes:
            category = item.modTypeName()
            for mod in item.modules:
                if mod[2]: 
                    for modName in mod[2]:
                        if isdep.get(modName):
                            if isdep[modName].get(category):
                                isdep[modName][category].append(mod[0])
                            else:
                                isdep[modName][category] = [mod[0]]
                        else:
                            newCatDict = {category : [mod[0]]}
                            isdep[modName] = newCatDict
        self.deps = isdep

    def run(self):
        self.getInfo()
        self.makeLoadGraph()
        self.getGraphDependency()
        self.makeDependGraph()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModGraph(sys.argv)
    app.run()
