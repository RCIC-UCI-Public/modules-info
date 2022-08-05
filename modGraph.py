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
import numpy as np
import matplotlib.pyplot as plt

class  ModGraph:
    def __init__(self, args):
        self.prog = os.path.basename(args[0])
        self.args = args[1:]     # command line arguments
        self.modinfo = None      # avail modules info
        self.unused = []         # list of unused modules, get from the input file
        self.gdir = "dot-graphs" # directory for saving  graphviz source and figure files
        self.render = 'png'      # rendering output format
        self.deps = {}           # dependency dictionary, where key is a module and a value
                                 # is a dictionary of modules that depend on it, i.e.1
                                 # python/2.7.17 : {'biotools': ['bowtie2/2.4.1'], 'genomics': ['rMATS/4.0.2']}
        self.categories = []     # list of modules categories
        self.modules = {}        # key is module name, value is its category index from self.categories
        self.statsPrereqs = []    # number of prereq modules for each avail module

        # graph attributes
        self.graphDir = 'LR'     # edge direction from L to R

        # legend attributes
        self.legendFontName = "Numbus-Roman" # font name
        self.legendFontColor = 'royalblue3'  # font color
        self.legendFontSize = '16'           # font size
        self.legendColorNode = 'aliceblue'       # regular node 

        # subgraph attributes 
        self.subgraphColorBg = 'ghostwhite'    # background color
        self.subgraphFontName = "Numbus-Roman" # font name
        self.subgraphFontColor = 'royalblue3'  # font color
        self.subgraphFontSize = '14'           # font size

        # node attributes
        self.colorUnused = 'orangered' # unused node 
        self.colorInvis = 'invis'      # for invisible color, balnd into background
        self.penWidth = '2'            # node border width
        self.nodeShape = 'record'      # node shape
        self.nodeStyle = 'filled'      # fill node with color

        # edge attributes 
        self.edgeArrowSize = '0.5'
        self.edgeArrowHead = 'vee'
        self.edgeColor = 'royalblue3'

        # CATEGOTIRES ['ai-learning', 'biotools', 'chemistry', 
        #              'compilers', 'engineering', 'genomics',
        #              'imaging', 'languages', 'libraries',
        #              'physics', 'statistics', 'tools']

        # colors for dot graphs
        self.colors = ['snow2', 'lavenderblush2', 'linen',
                       'slategray1', 'cornsilk', 'gainsboro',
                       'azure2', 'honeydew2', 'lavender',
                       'powderblue','oldlace', 'wheat'
                      ]
        self.pltColors = ['SteelBlue', 'LightSteelBlue', 'RoyalBlue',
                          'LIghtSkyblue', 'SlateGray','Gainsboro',
                          'MediumBlue', 'LightCyan', 'Blue',
                          'Lavender', 'Crimson', 'Gold'
                         ]

        self.parseArgs()

    def exitError(self):
        print (self.errmsg)
        sys.exit(1)

    def exitHelp(self):
        helpstr = "NAME\n        %s - create module dependencies graphs\n" % self.prog \
                + "\nSYNOPSIS\n        %s [OPTION] [FILE]\n" % self.prog \
                + "\nDESCRIPTION\n        Parse FILE provided on a command line to get unused modules, if none\n" \
                + "        provided assumes none were unused. Checks available modules, parse their modulefiles\n" \
                + "        using info about logging and loaded modules and build a dependency graph for each\n" \
                + "        category of modules (per MODULEPATH entries).\n\n" \
                + "        -h, --h, --help, help\n              Print usage info.\n\n" \
                + "        NOTE: this program requires python module graphviz and RPM graphviz (for dot) to be installed.\n "
        print (helpstr)
        sys.exit(0)

    def parseArgs(self):
        if self.args == []:
            return
        if self.args[0] in ["-h","--h","help","-help","--help"]:
            self.exitHelp()
        if os.path.isfile(self.args[0]):
            self.getUnusedModules(self.args[0])

    def getUnusedModules(self, fname):
        f = open(fname)
        txt = f.read()
        f.close()
        self.unused = txt.split()
        self.unused.sort()

    def getInfo(self):
        self.modinfo = ModInfo()
        self.modinfo.runCheck()

    def findNodesEdges(self, mtype):
        havenodes = False
        self.nodes = [] # graph node names list
        self.edges = [] # graph edges from->to

        # mod is an array ['name/version',  [prereq modules if any]]
        for mod in mtype.modules:
            self.nodes.append(mod[0])
            if len(mod[1]):
                self.nodes += mod[1]
                for i in mod[1]:
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
                ncolor = self.colors[self.modules[n]]  # node color from its category
                if n in self.unused:
                    self.addNode(self.g, n, fillcolor=ncolor, color=self.colorUnused)
                else:
                    self.addNode(self.g, n, fillcolor=ncolor, color=ncolor)
            else:
                solitary.append(n)
        self.addSolitaryNodes(self.g, solitary) 

    def addSolitaryNodes(self, g, names):
        """ use invisible edges to make graph more readable,
            resulting graph has 4 modules per row to keep nodes aligned.
        """
        n = 4
        args = [iter(names)] * n
        # an array of tuples size 4, non-node values are None
        nargs = itertools.zip_longest(*args, fillvalue=None)
        for i in nargs:
            if i[1]:
                self.addEdge(g, i[0], i[1], style=self.colorInvis)
            if i[2]:
                self.addEdge(g, i[1], i[2], style=self.colorInvis)
            if i[3]:
                self.addEdge(g, i[2], i[3], style=self.colorInvis)
            for j in i:
                if not j: continue # empty value
                ncolor = self.colors[self.modules[j]]
                if j in self.unused:
                    self.addNode(g, j, fillcolor=ncolor, color=self.colorUnused)
                else:
                    self.addNode(g, j, fillcolor=ncolor, color=ncolor )

    def addEdges(self):
        # add graph edges per loaded modules dependencies 
        for e in self.edges:
            self.addEdge(self.g, e[0], e[1])

    def addNode(self, G, nlabel, **kwargs):
        """add node to the graph
           G - graph object
           nlabel - node label
           **kwargs - additional attributes
        """
        G.node(nlabel, **kwargs)

    def addEdge(self, G, start, end, **kwargs):
        """add edge to the graph
           G - graph object
           start - edge start
           end   - edge end
           **kwargs - additional attributes
        """
        G.edge(start, end, **kwargs)

    def initLegend(self, name, reqstr):
        """ create and return legend subgraph object
            name - legend label
            reqstr - string for the requirements edge
        """
        c = Digraph('clusterLegend')
        c.attr(label=name)
        c.attr(fontsize=self.legendFontSize, fontname=self.legendFontName, fontcolor=self.legendFontColor)
        c.attr(color=self.legendFontColor)
        
        # module dependency info 
        # left hand nodes
        s0 = Digraph('struct0', node_attr={'shape': 'plaintext', 'color':'white'})
        s0.node('struct0', '''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
          <TR><TD PORT="p0" bgcolor="%s">A</TD></TR>
          <TR><TD bgcolor="%s">%s</TD></TR>
          <TR><TD PORT="p1" border="2" color="red" bgcolor="%s">C</TD></TR>
          <TR><TD bgcolor="%s">Users don't use C</TD></TR>
        </TABLE>>''' % (self.legendColorNode, self.colorInvis, reqstr, self.legendColorNode, self.colorInvis ))
        c.subgraph(s0)

        # right hand nodes
        s1 = Digraph('struct1', node_attr={'shape': 'plaintext', 'color':'white'})
        s1.node('struct1', '''<
        <TABLE BORDER="0" CELLBORDER="0" CELLSPACING="5">
          <TR><TD PORT="p0" bgcolor="%s">&emsp; B &emsp;</TD></TR>
          <TR><TD bgcolor="%s">   </TD></TR>
          <TR><TD PORT="p1" bgcolor="%s">   </TD></TR>
          <TR><TD bgcolor="%s">   </TD></TR>
        </TABLE>>''' % (self.legendColorNode, self.colorInvis, self.colorInvis, self.colorInvis, ))
        c.subgraph(s1)

        # add edge 
        self.addEdge(c, 'struct0:p0', 'struct1:p0')

        # module categories info as 2 tables
        s2 = Digraph('struct2', node_attr={'shape': 'plaintext', 'color':'white'})
        table = self.makeTableStr(0)
        s2.node('struct2', table)
        c.subgraph(s2)

        s3 = Digraph('struct3', node_attr={'shape': 'plaintext', 'color':'white'})
        table = self.makeTableStr(1)
        s3.node('struct3', table)
        c.subgraph(s3)

        # edge beteen two tables, just to line up things
        self.addEdge(c, 'struct2:p0', 'struct3:p0', style="", color=self.colorInvis)

        return c

    def makeTableStr(self, n):
        """ create HTML style table for categories 
            n=0 - first half of categoreis
            n=1 - second half of available categories
        """
        x = int(len(self.categories)/2) 
        head = "<<TABLE BORDER=\"0\" CELLBORDER=\"0\" CELLSPACING=\"5\">\n"
        tail = "        </TABLE>>"
        middle = ""

        if n:
           names = self.categories[x:]
           colors = self.colors[x:]
        else:
           names = self.categories[0:x]
           colors = self.colors[0:x]
           # add title to table start
           middle += "          <TR><TD colspan='2'><FONT COLOR=\"%s\">Modules Categories:</FONT></TD></TR>\n" % self.legendFontColor

        for i in range(0, int(x/2)):
           vals = (i, colors[i], names[i].upper(), colors[i+3], names[i+3].upper())
           middle  += "          <TR><TD PORT=\"p%d\" bgcolor=\"%s\">%s</TD><TD bgcolor=\"%s\">%s</TD></TR>\n" % vals
        table = head + middle + tail

        return table

    def initGraph(self, name):
        """ start graph and initialize its basic attribures"""
        self.g = Digraph(filename=name, directory=self.gdir, format=self.render)
        self.addGraphAttr('rankdir', self.graphDir)
        self.addGraphAttr('center', 'true')
        
        # arrows attributes
        self.addEdgeAttr('arrowsize', self.edgeArrowSize)
        self.addEdgeAttr('arrowhead', self.edgeArrowHead)
        self.addEdgeAttr('color', self.edgeColor)

        # nodes attributes
        self.addNodeAttr(self.g, 'shape', self.nodeShape)
        self.addNodeAttr(self.g, 'style', self.nodeStyle)
        self.addNodeAttr(self.g, 'penwidth', self.penWidth)

    def addGraphAttr(self, key, val):
        if self.g:
            self.g.graph_attr[key] = val

    def addEdgeAttr(self, key, val):
        if self.g:
            self.g.edge_attr[key] = val

    def addNodeAttr(self, g, key, val):
        if g:
            g.node_attr[key] = val

    def writeLoadGraph(self, mtype):
        if not self.findNodesEdges(mtype):
            return
        #print ("Processing %s modules" % mtype.modTypeName())
        # create a graph object for saving in files per modules type
        self.initGraph("modules-" + mtype.name)

        # add nodes and edges
        self.addNodes()
        self.addEdges()

        # create legend subgraph 
        l = self.initLegend("%s modules" % mtype.modTypeName().upper(), "A requires B")
        self.g.subgraph(l)

        # output graph source  and figure  files
        self.g.render(view=False) 

    def makeLoadGraph(self):
        if not self.modinfo:
            return  # no info about modules

        for item in self.modinfo.modtypes:
            #item.printInfo() # DEBUG 
            self.writeLoadGraph(item)

    def makeDependGraph(self):
        if not self.deps:
            return  # no info about modules

        # dict1: key - module name N, 
        #        val - number of categories where modules depend on module N 
        temp={}
        for key,val in self.deps.items():
            temp[key] = len(val)
        dict1 = {k: v for k, v in sorted(temp.items(), key=lambda item: item[1], reverse=True)}

        # dict2: key - number of categories where modules depend on a specific module X, 
        #        val - list of specific modules 
        dict2 = {}
        for key, value in dict1.items():
            if value not in dict2:
                dict2[value] = [key]
            else:
                dict2[value].append(key)

        # get stats for categories 
        self.findCategoryStats(dict2)

        # create graphs by number of categories for module dependencies
        for num, modnames in dict2.items():
            self.writeDependGraph(num, modnames)

    def findCategoryStats(self, d):
        # self.stats1: [0] - number of categories where modules depend on a specific module X, 
        #              [1] - number of X modules 
        self.statsByCategory = []
        for num, modnames in d.items():
            self.statsByCategory.append([len(modnames), num])

    def writeDependGraph(self, num, modnames):
        # create a graph object and set properties
        #print ("Processing modules with dependencies in %d categories" % num)
        self.initGraph("dependency-%s" % num)
        self.addGraphAttr('compound', 'true')
        self.addGraphAttr('concentrate', 'true')
        self.addEdgeAttr('dir', 'back')

        # add subgraphs by category
        self.addDependSubGraph(modnames)

        # create legend subgraph 
        l = self.initLegend("Modules dependency","A is required by B")
        self.g.subgraph(l)

        # output graph source and image files
        self.g.render(view=False) 

    def addDependSubGraph(self, modnames):
        cats = {} # dict of modules by categories for all modules in modnames
        # add nodes and edges
        num = len(modnames)
        for mod in modnames:
            # add modules that a loaded by other modules
            ncolor = self.colors[self.modules[mod]]
            self.addNode(self.g, mod, fillcolor=ncolor, color=ncolor)
            # find loading modules
            dictdeps = self.deps[mod]
            nodes = []
            for key, val in dictdeps.items():
                nodes += val
                # update category with modules
                if key in cats:
                    cats[key] += val
                else:
                    cats[key] = val
            for n in nodes:
                self.addEdge(self.g, mod, n)

        # create subgraph  cluster names
        subGraphs = cats.keys()
        subGraphsNames = {}
        i = 0  # counter for naming subgraphs
        for s in subGraphs:
            subGraphsNames[s] = ("cluster%s" % i)
            i += 1

        # add categories subgraphs
        for key in subGraphs:
            val = cats[key]
            subG = Digraph(subGraphsNames[key])
            subG.attr(label= key.upper())
            subG.attr(fontsize=self.subgraphFontSize, fontname=self.subgraphFontName, fontcolor=self.subgraphFontColor)
            subG.attr(color=self.subgraphFontColor)

            # remove duplicate node reference
            val_flat = list(set(val))
            if num < 3:
                self.addSolitaryNodes(subG, val_flat)
            else:
                for n in val_flat: 
                    ncolor = self.colors[self.modules[n]]
                    if n in self.unused:
                        self.addNode(subG, n, fillcolor=ncolor, color=self.colorUnused)
                    else:
                        self.addNode(subG, n, fillcolor=ncolor, color=ncolor)
            self.g.subgraph(subG)

    def getGraphDependency(self):
        if not self.modinfo:
            return  # no info about modules

        isdep = {}
        i = 0 # category position index
        for item in self.modinfo.modtypes:
            category = item.modTypeName()
            self.categories.append(category)
            for mod in item.modules:
                self.modules[mod[0]] = i # module category index
                if mod[1]:
                    for modName in mod[1]:
                        if isdep.get(modName):
                            if isdep[modName].get(category):
                                isdep[modName][category].append(mod[0])
                            else:
                                isdep[modName][category] = [mod[0]]
                        else:
                            newCatDict = {category : [mod[0]]}
                            isdep[modName] = newCatDict
            i += 1  # increase category position index

        self.deps = isdep
        # DEBUG
        #for k,v in self.deps.items():
        #    print ("DEBUG", k,v)

    def makeLoadedStatsGraph(self):
        print ("Building load stats graph")
        name = "%s/loadStats" % self.gdir
        plt.figure(2)

        d = {}
        for key in self.modules.keys():
            d[key] = 0

        for item in self.modinfo.modtypes:
            for mod in item.modules:
                if mod[1]:
                    for modName in mod[1]:
                        d[modName] += 1

        # create data and labels for pie plot
        vals = list(d.values())
        array = np.asarray(vals)
        bins = list(set(vals))
        bins.sort()
        bins.append(bins[-1]+1)
        ans = np.histogram(array,bins)

        y = ans[0]
        x = ans[1][:-1]
        let = []
        for i in y:
            if i > 1: 
                let.append("s")
            else:
                let.append("")
 
        # create wedge explode for data value "1"
        z = x * 0.0
        index = np.where(x == 1)
        z[index] = 0.05
        p = plt.pie(y, pctdistance=1.1, startangle=45, colors=self.pltColors, explode=z)

        # creatl legend labels
        labels = ['%4d (%2.1f%% or %d module%s)' % (l1, l2, l3, l4) for l1, l2, l3, l4 in zip(x, y*1.0/len(vals)*100,y,let)]
        plt.legend(p[0], labels, loc="best")

        # plor properties
        plt.title("Loading distribution for %s modules" % len(vals))
        plt.axis('equal')         # set equal ratio for the axes
        plt.tight_layout()        # paddingf between subplots if any

        # make white background nontransparent, legend 5% transparent
        plt.rcParams.update({ "figure.facecolor": (1.0, 1.0, 1.0, 1.0), "axes.facecolor":(1.0, 1.0, 1.0, 0.95)})

        # add annotation
        plt.text(0.2,-0.4,"%d modules (%2.1f%%)\nare loaded by\n%d other module" % (y[index], y[index]*1.0/len(vals)*100,x[index] ))

        plt.show()
        plt.savefig("%s.png" % name)

    def makePrereqStatsGraph(self):
        print ("Building prereq stats graph")
        name = "%s/prereqStats" % self.gdir
        plt.figure(1)

        for item in self.modinfo.modtypes:
            item.findStats()
            self.statsPrereqs += item.getStats()
        array = np.asarray(self.statsPrereqs)
        bins = range(min(array), max(array)+2)
        ans = plt.hist(array, bins=bins, rwidth=0.8, align='left' )
        plt.xticks(range(max(array)+1))
        yticks = range(int(max(ans[0])/10+2))
        yticks = np.asarray(yticks)
        yticks  = yticks * 10
        plt.yticks(yticks)
        plt.xlim(bins[0]-1, bins[-1])
        
        plt.grid(axis='y', alpha=1.0)
        plt.xlabel('Number of prerequisite modules loaded')
        plt.ylabel('Modules Counts')
        plt.show()
        plt.savefig("%s.png" % name)

    def run(self):
        self.getInfo()
        self.getGraphDependency()
        print ("Building graphs for modules by categories...")
        self.makeLoadGraph()
        print ("Building graphs for modules dependencies...")
        self.makeDependGraph()
        #for i in self.statsByCategory:
        #    print ("%d modules are required by others in %d categories" % (i[0], i[1]))
        self.makePrereqStatsGraph()
        self.makeLoadedStatsGraph()

##### Run from a command line #####
if __name__ == "__main__":
    app = ModGraph(sys.argv)
    app.run()
