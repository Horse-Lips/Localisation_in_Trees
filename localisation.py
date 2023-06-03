import networkx as nx
from random import choice

#===Global Variables===#
U = []
L = []


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

        Utils.createTDict("0", self.tDict, self.lDict, self.tree)   #Create tDict rooted at node 0

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
        
        return self.captTime


class Probe:
    """
     - Probe player class, given a move function this can
     - be called by the controller class to play the game
    """
    def __init__(self, moveFunc):
        self.moveFunc = moveFunc
        self.moveList = []


    def move(self, tree, tDict, lDict, d):
        return self.moveFunc(tree, tDict, lDict, self.moveList, d)


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


class Seager:
    """
     - Class for the Seager 2014 localisation strategy for trees.
     - The solve() method is the main function after initialisation.
     - Variables:
        - tree     - NetworkX tree object rooted at node 0
        - captTime - Number of rounds before target evaded or was captured
        - win      - Winner of the game, set to target until probe locates target
        - tDict    - Dict representation of the tree (See createTreeDict function)
        - lDict    - Dict of lists of nodes at each tree level
        - iDict    - Dict of relevant information during execution containing:
            - trace                 - Verbose information about the execution
            - k                     - The level marked as k at current stage of execution
            - dkMinus, dk, dkPlus   - Target locations on levels k - 1, k, k + 1
            - probeList             - List of all previously probed vertices
            - t, tLocation          - List of target locations, final target location. t can be preset as node list
            - l, vl, yl, zl         - Level l in the tree and associated nodes (case 5)
    """
    def __init__(self, tree, tMoveFunc):
        self.tree     = tree   #NetworkX tree object (Rooted at node 0)
        self.captTime = 0
        self.win      = "Target"
        self.tDict    = dict() #Dict representation of tree object (See createTreeDict)  
        self.lDict    = dict() #Dict of level information of the tree object
        self.iDict    = dict() #Dict containing relevant information during execution
        
        self.tMoveFunc = tMoveFunc  #Function controlling target movement
        
        Utils.createTDict("0", self.tDict, self.lDict, self.tree)


    def __setitem__(self, key, value):
        self.iDict[key] = value


    def __getitem__(self, key):
        try:    return self.iDict[key]
        except: return None


    def play(self):
        """
         - Carries out the strategy of theorem 8.
        """
        d = self.probe("0")

        if   d == 0:                  return self.located("0")
        elif len(self.lDict[d]) == 1: return self.located(self.lDict[d][0])
        else:                         return self.lemma4(self.tDict[self.lDict[d][0]].parent, self.tDict[self.lDict[d][-1]].parent)


    def lemma2(self, v, w, z):
        """
         - Lemma 2: Given v with w and z among its children where target set is
         - is contained in Siblings(w, z), either the target is located or the
         - target set can be contained within Children(w', z) if w has at most 
         - one child or Children(w, z') if z has at most one child.
         - Args:
            - v - The root of the subtree.
            - w - The leftmost sibling in the subset of v's children.
            - z - The rightmost sibling in the subset of v's children.
        """
        sibList = self.siblings(w, z)

        if len(sibList) == 1:
            return self.located(sibList[0])

        if len(self.tDict[w].children) == 1: #w has 1 child, narrow tree from left to right
            p, d, r = self.tDict[w].children[0], 0, 0

        elif len(self.tDict[w].children) == 0:
            p, d, r = w, 1, 0

        elif len(self.tDict[z].children) == 1:   #z has 1 child, narrow tree from right to left
            p, d, r = self.tDict[z].children[0], 0, 1

        elif len(self.tDict[z].children) == 0:
            p, d, r = z, 1, 1

        else:   #Neither w nor z have unique children, wrong lemma used so exit
            raise Exception("Lemma 2 used incorrectly. Exiting.")
        
        d1 = self.probe(p)

        if d1 == 0: return self.located(p)
        if d1 == 1: return self.located(self.tDict[p].parent)
            
        elif d1 == 2:
            if   not d:             return self.located(v)
            elif len(sibList) == 2: return self.located(sibList[1])
            else:                   return self.lemma2(v, sibList[1 - r], sibList[-1 - r])

        elif d1 == 3:
            if d:
                if len(sibList) == 2: return self.lemma4(sibList[1 - r], sibList[1 - r])
                else:                 return self.lemma4(sibList[1 - r], sibList[-1 - r])

            if len(sibList) == 2: return self.located(sibList[1 - r])
            else:                 return self.lemma2(v, sibList[1 - r], sibList[-1 - r])

        elif d1 == 4:
            if len(sibList) == 2: return self.lemma4(sibList[1 - r], sibList[1 - r])
            else:                 return self.lemma4(sibList[1 - r], sibList[-1 - r])
        

    def lemma3(self, u, v, w, z):
        """
         - Lemma 3: Given u with unique child v with w and z in its children,
         - either locates the robber at u or v, or applies Lemma 2 to v, w, z.
         - Args:
            - u - The parent of v.
            - v - The root of the subtree in lemma 2.
            - w - The leftmost sibling in the children of v.
            - z - The rightmost sibling in the children of v.
        """
        if self.tDict[u].parent is not None: p, d = self.tDict[u].parent, 0
        else:                                p, d = u,                    1

        d1 = self.probe(p)

        if d1 == 0: return self.located(p)
        if d1 == 1: return self.located(self.tDict[p].children[0])

        elif d1 == 2:
            if d: return self.lemma2(v, w, z)
            else: return self.located(v)

        elif d1 == 3:
            if d: return self.lemma4(w, z)
            else: return self.lemma2(v, w, z)

        elif d1 == 4: return self.lemma4(w, z)

        raise Exception("Reached end of play function")
    
    
    def lemma4(self, w, z):
        """
         - Applies return lemma 4 which, when the target set is contained
         - in Children(w, z) with w and z on the same level with
         - w <= z, finds w' and z' on the same level with w' <= z'
         - such that the target set is contained in Children(w', z').
         - F(Children(w', z')) is a strict subset of F(Children(w, z)).
         - Args:
            - w - The leftmost node of {w, ..., z}.
            - z - The rightmost node of {w, ..., z}.
            - k - The level in the tree of Children(w, z) (NOT w and z).
        """
        if w == z and self.tDict[w].children == []: return self.located(w)

        w, z      = self.reduceSet(w, z)    #Replace w with w', z with z' if no children
        self["k"] = self.tDict[w].level + 1 #Set global value of level k
        self.setDSets(w, z)                 #Set dk to Children(w, z) and expand

        if len(self["dk"]) == 1: return self.located(self["dk"][0])
        
        vk   = self.tDict[w].children[0]  #Let vk be the first child of w
        p, d = (vk, True) if len(self.tDict[vk].children) == 0 else (self.tDict[vk].children[0], False)
        
        d1   = self.probe(p)
        ds   = self.updateDSets(p, d1)

        if ds != -1: return self.located(ds)    #Dist set update resulted in 1 possible target location
        
        if d1 == 0:
            return self.located(p)
            
        if d1 == 1:
            return self.located(self.tDict[p].parent)

        elif d1 == 2:
            if d: return self.lemma2(w, self["dk"][1], self["dk"][-1])  #If probed vk and d1 == 2 then return lemma 2 w's other children
            else: return self.case1(w)   #elif  w == z and len(self.tDict[vk].children) == 1: return self.located(w)

        elif d1 == 3:   #If probed vk and d1 == 3 then case 4 (dk-1 and dk+1 non-empty)
            if d: return self.case4(w)
            else: return self.case2(w)

        elif d1 == 4:   #If probed vk and d1 == 4 then target in subset of Children(w, z)
            if d: return self.lemma4(self.tDict[self["dk"][0]].parent, self.tDict[self["dk"][-1]].parent)
            else: return self.case4(w)

        elif d1 % 2 == 1 and d1 > 3:
            if d: return self.case5(p, w, d1, self["dkMinus"][-1])
            else: return self.case3(w)
        
        elif d1 % 2 == 0 and d1 > 5:
            if d: return self.case3(w)
            else: return self.case5(p, w, d1, self["dkMinus"][-1])


    def case1(self, w):
        """
         - Case 1: d = 2 and therefore the target set 
         - contains w (vk-1) and  children(vk) excluding vk+1.
         - Args:
            - vk - The leftmost child of w.
            - d  - The distance between the previous probe and the target.
        """
        if self["dkPlus"] == []: #If vk has no children, target located at its parent
            return self.located(self["dkMinus"][0])

        elif len(self.tDict[w].children) == 1: #If vk is the unique child of w then lemma 3
            return self.lemma3(w, self.tDict[w].children[0], self["dkPlus"][0], self["dkPlus"][-1])

        #Otherwise w has more than one child, zk is its rightmost child
        vkMinus2 = self.tDict[w].parent  #vk-2 is w's parent
        vk = self.tDict[w].children[0]   #vk is w's leftmost child
        yk = self.tDict[w].children[1]   #yk is the child to the right of vk
        zk = self.tDict[w].children[-1]  #zk is w's rightmost child
        s  = self.tDict[w].children[-2]  #s is the child to the left of zk

        if len(self.tDict[zk].children) > 1: #zk has > 1 child, then w.parent has <= 1 child, probe zk
            d2 = self.probe(zk)

            if d2 == 0: return self.located(zk)
            if d2 == 1: return self.located(w)

            elif d2 == 2: #Target set is w's parent and w's children (minus zk)
                if vkMinus2 is None: return self.lemma2(w, vk, s) #If w is the root it has no parent, lemma 2 on w's children
                else:                return self.lemma3(vkMinus2, w,  vk,  s)

            elif d2 == 3: return self.lemma2(vk, self["dkPlus"][0], self["dkPlus"][-1]) #If d2 is 3 then target is in children(vk) excluding vk + 1, so lemma 2
            elif d2 == 4: return self.lemma4(self["dkPlus"][0], self["dkPlus"][-1]) #If d2 is 4 then the target is in children(wk+1, xk+1)

        #Now if zk has at most one child, then we probe w's parent
        elif len(self.tDict[zk].children) <= 1:
            d2 = self.probe(vkMinus2)

            if d2 == 0:   return self.located(vkMinus2)
            if d2 == 1:   return self.located(w)  #If d2 is 1 then the target is at w
            elif d2 == 2: return self.lemma2(w, vk, zk) #If d2 == 2 then the target is in siblings(vk, zk) so lemma 2
            elif d2 == 3: return self.lemma2(vk, self["dkPlus"][0], self["dkPlus"][-1]) #If d2 is 3 then target is in children(vk) excluding vk + 1, so lemma 2
            elif d2 == 4: return self.lemma4(self["dkPlus"][0], self["dkPlus"][-1]) #If d2 is 4 then the target is in children(wk+1, xk+1)

        raise Exception("Reached end of play function")
    

    def case2(self, w):
        """
         - Case 2: d is 2 or 3, so the target set is the children of w minus vk.
         - Args:
            - w  - The leftmost sibling in siblings(w, z) in lemma 4.
            - vk - The leftmost child of w.
        """
        if len(self["dk"]) == 1: return self.located(self["dk"][0])
        else:                    return self.lemma2(w, self["dk"][0], self["dk"][-1])
    

    def case3(self, w):
        """
         - Case 3: d is odd and greater than 3, so the target set contains all nodes
         - on level k that are d away. i.e children(yk-1, zk-1), so call Lemma 4 on.
        """
        if len(self["dk"]) == 1: return self.located(self["dk"][0])
        else:                    return self.lemma4(self["dkMinus"][0], self["dkMinus"][0])
    

    def case4(self, w):
        """
         - Case 4: d = 4, so dk-1 and dk+1 will contain nodes
        """
        if   self["dkPlus"]    == []:    #dk+1 empty, target in dkMinus, these are siblings so lemma 2
            return self.lemma2(self.tDict[self["dkMinus"][0]].parent, self["dkMinus"][0], self["dkMinus"][-1])

        elif self["dkMinus"] == []:     #dk-1 empty, so target set in dkPlus (children(wk, zk)) so lemma 4
            return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent)

        zkMinus   = self["dkMinus"][-1]     #Get zk, wk-2's rightmost child
        p2, minus = (zkMinus, 1) if self.tDict[zkMinus].children == [] else (self.tDict[zkMinus].children[0], 0)
        d2        = self.probe(p2)          #Probe zk's first child or zk if there are no children

        if d2 == 0:
            return self.located(p2)

        if d2 == 1:
            return self.located(self.tDict[p2].parent)
            
        elif d2 == 2:
            if minus:                                  return self.lemma2(self.tDict[zkMinus].parent, self["dkMinus"][0], self["dkMinus"][-2])
            if len(self.tDict[zkMinus].children) == 1: return self.located(self.tDict[zkMinus].parent) #zk is zk-1's only child, target at zk's parent
            
            d3 = self.probe(w)

            if d3 == 0:
                return self.located(w)
            
            elif d3 == 1:
                return self.located(self.tDict[w].parent)
                
            elif d3 == 2:
                vkMinus2 = self.tDict[w].parent
                vkMinus3 = self.tDict[self.tDict[w].parent].parent

                if vkMinus3 is None: return self.lemma2(vkMinus2, self["dkMinus"][0], self["dkMinus"][-1])
                else:                return self.lemma3(vkMinus3, vkMinus2, self["dkMinus"][0], self["dkMinus"][-1])

            elif d3 == 3:
                return self.lemma2(zkMinus, self.tDict[zkMinus].children[1], self.tDict[zkMinus].children[-1])

            elif d3 == 4:
                return self.lemma4(self.tDict[zkMinus].children[1], self.tDict[zkMinus].children[-1])

        elif d2 == 3:
            if minus:                       return self.lemma4(w, self["dkMinus"][-2]) #Same as d2 == 4 and no minus
            elif len(self["dkMinus"]) == 2: return self.located(self["dkMinus"][0]) #there's one other vertex on zk.level, it's 3 away so target found
            else:                           return self.lemma2(self.tDict[zkMinus].parent, self["dkMinus"][0], self["dkMinus"][-2]) #Otherwise the target is in the siblings of wk-2's children, so lemma 2

        elif d2 == 4:
            if minus: return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent) #Same as d2 == 5 and no minus
            else:     return self.lemma4(w, self["dkMinus"][-2])

        elif d2 == 5:
            if minus: return self.lemma4(self["dkPlus"][0], self["dkPlus"][-1])
            else:     return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent) #If d = 5 then the target is in the children of the children of w (apart from vk)

        elif d2 == 6:
            return self.lemma4(self["dkPlus"][0], self["dkPlus"][-1])

        raise Exception("Reached end of play function")
    

    def lVariables(self, d, p):
        self["l"] = self["k"] - (d // 2)    #Get level l in the tree (highest level path to target can reach)

        self["vl"] = p              #Get vl
        while self.tDict[self["vl"]].level != self["l"]:
            self["vl"] = self.tDict[self["vl"]].parent

        self["yl"] = p              #Get yl
        while self.tDict[self["yl"]].level != self["l"]:
            self["yl"] = self.tDict[self["yl"]].parent

        self["zl"] = p              #Get zl
        while self.tDict[self["zl"]].level != self["l"]:
            self["zl"] = self.tDict[self["zl"]].parent


    def case5(self, p, w, d1, zkMinus):
        if   self["dkMinus"] == [] and self["dkPlus"] != []:
            return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent)
        
        elif self["dkMinus"] != [] and self["dkPlus"] == []:
            return self.lemma4(self.tDict[self["dkMinus"][0]].parent, self.tDict[self["dkMinus"][-1]].parent)
            
        self.lVariables(d1, p)
        zkMinus2 = self.tDict[zkMinus].parent

        if zkMinus == self.tDict[zkMinus2].children[-1]:
            d2 = self.probe(self["vl"])
            return self.case5a(p, w, d1, d2, zkMinus)

        elif zkMinus == self.tDict[zkMinus2].children[0] and len(self.tDict[zkMinus2].children) > 1 and len(self.tDict[zkMinus].children) > 1:
            d2 = self.probe(self.tDict[zkMinus].parent)
            if d2 == 0: return self.located(self.tDict[zkMinus].parent)
            else:       return self.case5b(p, w, d1, d2, zkMinus)

        elif zkMinus != self.tDict[zkMinus2].children[-1] and len(self.tDict[zkMinus].children) < 2:
            return self.case5c(p, w, d1, zkMinus)
            

    def case5a(self, p, w, d1, d2, zkMinus):
        wkPlus,  xkPlus  = self["dkPlus"][0],  self["dkPlus"][-1]
        ykMinus = self["dkMinus"][0]

        if   d2 == (d1 // 2) + 2: return self.lemma4(wkPlus, xkPlus)
        elif d2 == (d1 // 2) + 1: return self.lemma4(self.tDict[wkPlus].parent, self.tDict[xkPlus].parent)
        elif d2 == (d1 // 2) - 1: return self.lemma4(self.tDict[ykMinus].parent, self.tDict[zkMinus].parent)
        elif d2 == (d1 // 2) - 2:
            ykMinus2, zkMinus2 = self.tDict[ykMinus].parent,  self.tDict[zkMinus].parent

            if d1 != 6: return self.lemma4(self.tDict[ykMinus2].parent, self.tDict[zkMinus2].parent)
            else:       return self.lemma2(self.tDict[ykMinus2].parent, ykMinus2, zkMinus2)
        elif d2 == d1 // 2:       return self.lemma4(self.tDict[self.tDict[wkPlus].parent].parent, zkMinus)
        

    def case5b(self, p, w, d1, d2, zkMinus):
        wk = self.tDict[self["dkPlus"][0]].parent
        xk = self.tDict[self["dkPlus"][-1]].parent

        zkMinus2 = self.tDict[zkMinus].parent

        zlPlus = self["dkMinus"][-1]

        while self.tDict[zlPlus].level != self["l"]+ 1:
            zlPlus = self.tDict[zlPlus].parent

        if   d2 == 0:      return self.located(zkMinus2)
        elif d2 == 1:      return self.located(zkMinus)
        elif d2 == 2:      return self.lemma2(zkMinus, zkMinus)
        elif d2 == d1:     return self.lemma4(self["dkMinus"][0], self["dkMinus"][-1])
        elif d2 == d1 - 1: return self.lemma4(wk, xk)

        elif d2 == d1 - 2:
            return self.lemma4(self.tDict[wk].parent, self.tDict[zk].parent)
            """kMinus   = self.lDict[self["k"] - 1]

            for i in range(len(kMinus) - 1, 0, -1):
                r = kMinus[i]

                while r != zlPlus and r != self["zl"]:
                    r = self.tDict[r].parent

                if r == self["zl"]:
                    t = kMinus[i]
                    break

            return self.lemma4(self.tDict[wk].parent, t, self.tDict[wk].level + 1)

        return self.case5bExtraCase(zkMinus2, w, d1, d2)"""


    def case5bExtraCase(self, p, w, d1, d2):
        #d2 is odd with 3 <= d2 <= d1 - 3 or similarly for case 5c
        if d2 % 2 != 0 and (3 <= d2 <= d1 - 3 or 5 <= d2 <= d1 + 2):
            m = (d2 - 1) / 2
            levelPlus = self["k"] - m - 1

            stPlus = self["dkMinus"][-1]
            while self.tDict[stPlus].level != levelPlus:
                stPlus = self.tDict[stPlus].parent

            stRoot = self.tDict[stPlus].parent

            kMinus   = self.lDict[self["k"] - 1]

            for i in range(len(kMinus) - 1, 0, -1):
                r = kMinus[i]

                while r != stPlus and r != stRoot:
                    r = self.tDict[r].parent

                if r == stRoot:
                    t = kMinus[i]
                    break

            for i in range(0, len(kMinus)):
                r = kMinus[i]

                while r != stPlus and r != stRoot:
                    r = self.tDict[r].parent

                if r == stRoot:
                    s = kMinus[i]
                    break

            return self.lemma4(s, t)

        elif d2 % 2 == 0 and (4 <= d2 <= d1 - 4 or 6 <= d2 <= d1 + 2):
            m = d2 / 2

            q, R, s, t = None, None, None, None

            qrPlus = self["dkMinus"][-1]
            while qrPlus is not None and self.tDict[qrPlus].level != self["k"] - m:
                qrPlus = self.tDict[qrPlus].parent

            if qrPlus is not None:
                qrRoot = self.tDict[qrPlus].parent

                levelK   = self.lDict[self["k"]]

                for i in range(len(levelK) - 1, 0, -1):
                    r = levelK[i]

                    while r != qrPlus and r != qrRoot and r != None:
                        r = self.tDict[r].parent

                    if r == qrRoot:
                        R = levelK[i]
                        break

                for i in range(0, len(levelK)):
                    r = levelK[i]

                    while r != qrPlus and r != qrRoot and r != None:
                        r = self.tDict[r].parent

                    if r == qrRoot:
                        q = levelK[i]
                        break


            stPlus = self["dkMinus"][-1]
            while stPlus is not None and self.tDict[stPlus].level != self["k"] - m - 1:
                stPlus = self.tDict[stPlus].parent

            if stPlus is not None:
                stRoot = self.tDict[stPlus].parent

                kMinusMinus   = self.lDict[self["k"] - 2]

                for i in range(len(kMinusMinus) - 1, 0, -1):
                    r = kMinusMinus[i]

                    while r != stPlus and r != stRoot and r != None:
                        r = self.tDict[r].parent

                    if r == stRoot:
                        t = kMinusMinus[i]
                        break

                for i in range(0, len(kMinusMinus)):
                    r = kMinusMinus[i]

                    while r != stPlus and r != stRoot and r != None:
                        r = self.tDict[r].parent

                    if r == stRoot:
                        s = kMinusMinus[i]
                        break

            if q == None and R == None and s == None and t == None:
                raise Exception("====== ALL OF S, T, Q, R, ARE NONE ======")

            elif q == None or R == None or self.children(q, R) == []:
                return self.lemma4(s, t)

            elif s == None or t == None or self.children(s, t) == []:
                return self.lemma4(q, R)

            self.lVariables(d2, p)
            d3 = self.probe(self["vl"])
            if d3 == 0: return self.located(self["vl"])

            self["dkMinus"] = self.children(self.tDict[s].parent, self.tDict[t].parent)
            self["dk"]      = []
            self["dkPlus"]  = self.children(self.tDict[q].parent, self.tDict[R].parent)

            self["k"] = self.tDict[s].level + 1

            return self.case5a(p, w, d1, d3)


    def case5c(self, p, w, d1, zkMinus):    
        zkMinus2 = self.tDict[zkMinus].parent
        zk       = self.tDict[zkMinus].children[0]
        zkMinusPred   = self["dkMinus"][self["dkMinus"].index(zkMinus) - 1]

        d2 = self.probe(zk)

        if d2 == 0:   return self.located(zk)
        if d2 == 1:   return self.located(zkMinus)
        elif d2 == 2: return self.located(zkMinus2)
        elif d2 == 3: return self.lemma2(zkMinus2, self.tDict[zkMinus2].children[0], zkMinusPred)

        elif d2 == 4:
            zkMinus3 = self.tDict[zkMinus2].parent
            d3 = self.probe(zkMinus3)
            
            if d3 == 0:
                return self.located(zkMinus3)

            if d3 == 1:
                zkMinus3Children = self.tDict[zkMinus3].children
                zkMinus2Pred = zkMinus3Children[zkMinus3Children.index(zkMinus2) - 1]

                return self.lemma2(zkMinus3, self.tDict[zkMinus3].children[0], zkMinus2Pred)

            elif d3 == 2:
                self["dkMinus"] = self["dkMinus"][:-1]
                return self.case5(p, w, d1, zkMinusPred)

            elif d3 == 3:
                return self.lemma4(t, zkMinusPred)

            elif d3 == 4:
                return self.lemma4(self.tDict[t].children[0], self.tDict[zkMinusPred].children[-1])

        else:
            return self.case5b(p, w, d1, d2, zkMinus)
        

    def probe(self, v):
        """
         - Returns the distance from v to the target
        """
        if self.captTime == 0: self["probeList"] = []                       #Initialise probe list
        if self["t"] is None:  self["t"] = [choice(list(self.tree.nodes))]  #Random target start if none given

        self["probeList"].append(v) #Add probed node to probe list
        self.captTime += 1          #Increase capture time by one
                    
        d  = nx.shortest_path_length(self.tree, v, self["t"][-1])               #Get dist from node to target
        self["t"].append(self.tMoveFunc(self.tree, self.tDict, self.lDict, self["t"][-1]))  #Move target according to given movement function

        return d


    def updateDSets(self, v, d):
        """
         - Updates the sets Dk-1, Dk, Dk+1
        """
        distances = nx.single_source_dijkstra_path_length(self.tree, v)
        dkMinus, dk, dkPlus = [], [], []

        tSet = self["dkMinus"] + self["dk"] + self["dkPlus"]

        for i in distances:
            if distances[i] == d and i in tSet:
                if   self.tDict[i].level == self["k"] - 1: dkMinus.append(i)
                elif self.tDict[i].level == self["k"]:     dk.append(i)
                elif self.tDict[i].level == self["k"] + 1: dkPlus.append(i)

        tSetNew = dkMinus + dk + dkPlus
        self["dkMinus"], self["dk"], self["dkPlus"] = dkMinus, dk, dkPlus
        
        if len(tSetNew) == 1: return tSetNew[0]
        else:                 return -1


    def setDSets(self, w, z):
        """
         - Expands Dk-1, Dk, and Dk+1 simulating target movement
        """
        self["dkMinus"] = []
        self["dk"]      = self.children(w, z)  #Set dk sets
        self["dkPlus"]  = []

        for n in self["dk"]:
            if self.tDict[n].parent not in self["dkMinus"]:
                self["dkMinus"].append(self.tDict[n].parent)

            for c in self.tDict[n].children:
                if c not in self["dkPlus"]:
                    self["dkPlus"].append(c)
            

    def located(self, v):
        """
         - Sets the target as located at node v.
         - Args:
            - v - The vertex that the target was located at.
        """
        self.win = "Probe"
        self["tLocation"] = v
        return v


    def siblings(self, w, z):
        """
         - Returns list of siblings(w, z) defined as all vertices
         - on the same level between w and z with the same parent.
         - Args:
            - w - The leftmost sibling in the set.
            - z - The rightmost sibling in the set.

         - Returns:
            -   - The set of Siblings(w, z) as defined above.
        """
        allChildren = self.tDict[self.tDict[w].parent].children
        return allChildren[allChildren.index(w):allChildren.index(z) + 1]


    def children(self, w, z):
        """
         - Returns the list of children of vertices between
         - and including w and z on the same level.
         - Args:
            - w - The leftmost vertex of the subset of the level.
            - z - The rightmost vertex of the subset of the level.

         - Returns:
            -   - The set of Children(w, z) as defined above.
        """
        levelK    = self.lDict[self.tDict[w].level]
        childList = []

        for node in levelK[levelK.index(w):levelK.index(z) + 1]:
            for child in self.tDict[node].children:
                childList.append(child)

        return childList


    def reduceSet(self, w, z):
        """
         - Replaces w with w' and z with z' if they have
         - no children. Used at the start of Lemma 4.
        """
        levelK = self.lDict[self.tDict[w].level]
        wIndex = levelK.index(w)
        zIndex = levelK.index(z)

        while self.tDict[levelK[wIndex]].children == []: wIndex += 1
        while self.tDict[levelK[zIndex]].children == []: zIndex -= 1

        return levelK[wIndex], levelK[zIndex]


"""Utility functions for use with various classes."""
class Utils:
    def createTDict(node, tDict, lDict, tree, parent = None, level = 0):
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
        if level not in lDict:        lDict[level] = []
        if node  not in lDict[level]: lDict[level].append(node)

        nodeChildren = [i for i in tree.neighbors(node) if i not in tDict]
        tDict[node]  = nodeInfo(level, parent, nodeChildren)

        for child in nodeChildren: Utils.createTDict(child, tDict, lDict, tree, parent = node, level = level + 1)


class TargetMovement:
    def tRandom(tree, tDict, lDict, node):
        """
         - Given the node that the target currently
         - occupies, move to a random neighbour node.
        """
        return choice([i for i in tree.neighbors(node)])


    def tUpTree(tree, tDict, lDict, node):
        """
         - Given the tDict and node the target
         - occupies, move up the tree with a 70% 
         - chance, move down the tree with a 20%
         - chance, stay still with a 10% chance
        """
        n = uniform(0, 1)

        if   n <= 0.7 and tDict[node].parent is not None: return tDict[node].parent
        elif n <= 0.9 and tDict[node].children != []:     return choice(tDict[node].children)
        else:                                             return node


    def tDownTree(tree, tDict, lDict, node):
        """
         - The same as upTree but with higher
         - probability of moving down the tree
        """
        n = uniform(0, 1)

        if   n <= 0.7 and tDict[node].children != []:     return choice(tDict[node].children)
        elif n <= 0.9 and tDict[node].parent is not None: return tDict[node].parent
        else:                                             return node


    def tUpDown(tree, tDict, lDict, node):
        """
         - Given the currently occupied node, 35%
         - chance of selecting the parent 50% chance
         - of selecting a random child, and 15%
         - chance of remaining at the node itself.
        """
        n = uniform(0, 1)
        
        if   n <= 0.35  and tDict[node].parent is not None: return tDict[node].parent
        elif n <= .85 and tDict[node].children != []:       return choice(tDict[node].children)
        else:                                               return node


    def tProbabilistic(tree, tDict, lDict, node):
        """
         - Probabilistic movement where the prob-
         - ability of moving to a neighbour is
         - equal to its degree divided by the sum
         - of the degree of all neighbours of the
         - node currently occupied by the target.
        """
        neighbours = [i for i in tree.neighbors(node)]
        nDegrees   = [len([i for i in tree.neighbors(neighb)]) for neighb in neighbours]
        nSum       = sum(nDegrees)
        nDegrees   = cumsum([i / nSum for i in nDegrees])

        n = uniform(0, 1)

        for i in range(len(neighbours)):
            if n <= nDegrees[i]:
                return neighbours[i]
                
                
class ProbeMovement:
    def pRandom(tree, tDict, lDict, probeList, d):
        """
         - Probe a random node in the tree
        """
        return choice(list(tree.nodes))


    def pRandomLeaf(tree, tDict, lDict, probeList, d):
        """
         - Probe a random leaf node of the tree
        """
        return choice(tDict["leaves"])


    def pTLeft(tree, tDict, lDict, probeList, d):
        if len(probeList) % 3 == 1:
            try:    U = lDict[d - 1]
            except: U = lDict[d]

            probeList.append(U[0])

        elif len(probeList) % 3 == 2:
            try:    probeList.append(tDict[U[0]].parent)
            except: probeList.append(U[0])
            
        else:
            probeList.append("0")
        
        return probeList[-1]


    def pTRight(tree, tDict, lDict, probeList, d):
        if len(probeList) % 3 == 1:
            try:    U = lDict[d - 1]
            except: U = lDict[d]

            probeList.append(U[-1])

        elif len(probeList) % 3 == 2:
            try:    probeList.append(tDict[U[-1]].parent)
            except: probeList.append(U[-1])
            
        else:
            probeList.append("0")
        
        return probeList[-1]


    def pBLeft(tree, tDict, lDict, probeList, d):
        if len(probeList) % 3 == 1:
            try:    U = lDict[d + 1]
            except: U = lDict[d]

            probeList.append(U[0])

        elif len(probeList) % 3 == 2:
            try:    probeList.append(tDict[U[0]].children[0])
            except: probeList.append(U[0])
            
        else:
            probeList.append("0")
        
        return probeList[-1]


    def pBRight(tree, tDict, lDict, probeList, d):
        if len(probeList) % 3 == 1:
            try:    U = lDict[d + 1]
            except: U = lDict[d]

            probeList.append(U[-1])

        elif len(probeList) % 3 == 2:
            try:    probeList.append(tDict[U[-1]].children[-1])
            except: probeList.append(U[-1])
            
        else:
            probeList.append("0")
        
        return probeList[-1]
