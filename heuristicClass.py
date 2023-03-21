import networkx as nx
from random import choice

class nodeInfo:
    """
     - Stores information about nodes in a tree.
     - Variables:
        - Level    - Level of node in the tree.
        - Parent   - Parent of node, None if root.
        - Children - List of the node's children.
    """
    def __init__(self, level, parent, children):
        self.level    = level
        self.parent   = parent
        self.children = children


class Localisation:
    """
     - Class for the localisation game. The play() function handles the game.
     - Variables:
        - tree     - NetworkX tree object
        - target   - Target object
        - probe    - Probe object
        - win      - "p" if probe wins, "t" if target wins, otherwise None
        - captTime - Rounds taken to locate target
        - tInitial - Target start location (optional)
    """
    def __init__(self, tree, target, probe, tInitial = None):
        self.tree     = tree
        self.target   = target
        self.probe    = probe
        self.win      = None
        self.captTime = 1       #Start at 1 for initial moves

        self.tInitial = tInitial
        
        self.tDict = dict()
        self.lDict = dict()

        self.createTDict("0")   #Create tDict rooted at node 0

        self.tDict["leaves"] = []
        for i in self.tDict:
            if i == "leaves":
                continue

            if self.tDict[i].children == []:
                self.tDict["leaves"].append(i)


    def play(self):
        """
         - Calls the target's initial() function for initial placement, then alternates
         - the play() function for probe and target until there is a winner.
        """
        if self.tInitial is None: tMove = self.target.initial(self.tree)      #Initial target placement
        else:                     tMove = self.tInitial
        pMove = self.probe.initial()                #Initial probe move (Usually root)
        
        while True:
            dists     = nx.single_source_dijkstra_path_length(self.tree, pMove) #Dist from p to all nodes
            tDist     = nx.shortest_path_length(self.tree, pMove, tMove)        #Dist from p to t
            tPossible = [i for i in dists if dists[i] == tDist]                 #Possible t locations
            
            if tMove == pMove:
                self.win = "Probe"
                break

            elif len(tPossible) == 1:
                self.win = "Probe"
                break

            elif self.captTime > len(list(self.tree.nodes)):
                self.win = "Target"
                break
            
            tMove = self.target.move(self.tree, self.tDict, self.lDict)
            pMove = self.probe.move(self.tree, self.tDict, self.lDict, tDist)
            self.captTime += 1


    def createTDict(self, node, parent = None, level = 0):
        """
         - Converts a tree to a dictionary, where keys are the
         - the node's ID and values are nodeInfo entries as above.
         - Args:
            - d      - A dictionary.
            - tree   - A networkx tree.
            - node   - Node to add to the dictionary.
            - parent - The node's parent if it exists.
            - level  - The level in the tree that the node is on.
        """
        if level not in self.lDict:
            self.lDict[level] = []

        if node not in self.lDict[level]:
            self.lDict[level].append(node)

        nodeChildren = [i for i in self.tree.neighbors(node) if i not in self.tDict]
        self.tDict[node] = nodeInfo(level, parent, nodeChildren)

        for child in nodeChildren:
            self.createTDict(child, parent = node, level = level + 1)


class Probe:
    """
     - Probe player class, given a move function this can
     - be called by the controller class to play the game
    """
    def __init__(self, moveFunc):
        self.moveFunc = moveFunc
        self.moveList = []
        
        self.dkMinus = []
        self.dk      = []
        self.dkPlus  = []


    def move(self, tree, tDict, lDict, d):
        if type(self.moveFunc) == str: return self.simpleSeager(tree, tDict, lDict, d)
        else:                          return self.moveFunc(tree, tDict, lDict, self.moveList, d)


    def simpleSeager(self, tree, tDict, lDict, d):
        if len(self.moveList) % 2 == 0:
            self.updateDSets(tree, d)
            parentSet = []
            
            if   self.dkPlus  != []: parentSet = self.dkPlus
            elif self.dk      != []: parentSet = self.dk
            elif self.dkMinus != []: parentSet = self.dkMinus
            
            if parentSet == []:             self.moveList.append("0")
            elif self.moveFunc == "tLeft":  self.moveList.append(tDict[parentSet[0]].parent)
            elif self.moveFunc == "tRight": self.moveList.append(tDict[parentSet[-1]].parent)
            elif self.moveFunc == "bLeft":  self.moveList.append(tDict[parentSet[0]].children[0])
            elif self.moveFunc == "bRight": self.moveList.append(tDict[parentSet[0]].children[-1])
            
        elif len(self.moveList) % 1 == 0:
            try:    self.dkMinus = lDict[d - 1]
            except: self.dkMinus = lDict[d]
            
            self.dk      = lDict[d]   #Dk is level d after probing the root
            
            try:    self.dkPlus = lDict[d + 1]
            except: self.dkPlus = lDict[d]

            if self.moveFunc == "tLeft":    self.moveList.append(self.dkMinus[0])
            elif self.moveFunc == "tRight": self.moveList.append(self.dkMinus[-1])
            elif self.moveFunc == "bLeft":  self.moveList.append(self.dkPlus[0])
            elif self.moveFunc == "bRight": self.moveList.append(self.dkPlus[-1])
        
        else:
            self.moveList.append("0")
    
        return self.moveList[-1]

    def initial(self):
        self.moveList.append("0")
        return "0"  #Just probe the root at the start of the game


    def updateDSets(self, tree, d):
        """
         - Updates the sets Dk-1, Dk, Dk+1
        """
        distances = nx.single_source_dijkstra_path_length(tree, self.moveList[-1])
        dkMinus, dk, dkPlus = [], [], []

        tSet = self.dkMinus + self.dk + self.dkPlus

        for i in distances:
            if distances[i] == d:
                if   i in dkMinus: dkMinus.append(i)
                elif i in dk:      dk.append(i)
                elif i in dkPlus:  dkPlus.append(i)

        self.dkMinus, self.dk, self.dkPlus = dkMinus, dk, dkPlus


class Target:
    """
     - Target player class, given an initial placement
     - function and a move function, these can be called
     - by the controller class to play the game
     - Variables:
        - initialFunc - Function that chooses an initial node for the target
        - moveFunc    - Function that chooses a move for the target
        - moveList    - List of all moves made by the target
    """
    def __init__(self, initialFunc, moveFunc):
        self.initialFunc = initialFunc
        self.moveFunc    = moveFunc
        self.moveList    = []


    def initial(self, tree):
        move = choice(list(tree.nodes))
        self.moveList.append(move)

        return move


    def move(self, tree, tDict, lDict):
        move = self.moveFunc(tree, tDict, lDict, self.moveList[-1])
        self.moveList.append(move)

        return move