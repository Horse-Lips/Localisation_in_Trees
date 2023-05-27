from networkx import shortest_path_length, single_source_dijkstra_path_length
from random   import choice
import os


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
        
        self.createTDict("0")


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
                if len(sibList) == 2: return self.lemma4(sibList[1 - r], sibList[1 - r], self.tDict[w].level + 1)
                else:                 return self.lemma4(sibList[1 - r], sibList[-1 - r], self.tDict[w].level + 1)

            if len(sibList) == 2: return self.located(sibList[1 - r])
            else:                 return self.lemma2(v, sibList[1 - r], sibList[-1 - r])

        elif d1 == 4:
            if len(sibList) == 2: return self.lemma4(sibList[1 - r], sibList[1 - r], self.tDict[w].level + 1)
            else:                 return self.lemma4(sibList[1 - r], sibList[-1 - r], self.tDict[w].level + 1)
        

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
            if d: return self.lemma4(w, z, self.tDict[w].level + 1)
            else: return self.lemma2(v, w, z)

        elif d1 == 4: return self.lemma4(w, z, self.tDict[w].level + 1)

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
            else: return self.case1(p, w, d1)   #elif  w == z and len(self.tDict[vk].children) == 1: return self.located(w)

        elif d1 == 3:   #If probed vk and d1 == 3 then case 4 (dk-1 and dk+1 non-empty)
            if d: return self.case4(p, w, d1)
            else: return self.case2(p, w, d1)

        elif d1 == 4:   #If probed vk and d1 == 4 then target in subset of Children(w, z)
            if d: return self.lemma4(self.tDict[self["dk"][0]].parent, self.tDict[self["dk"][-1]].parent)
            else: return self.case4(p, w, d1)

        elif d1 % 2 == 1 and d1 > 3:
            if d: return self.case5(p, w, d1, self["dkMinus"][-1])
            else: return self.case3(p, w, d1)
        
        elif d1 % 2 == 0 and d1 > 5:
            if d: return self.case3(p, w, d1)
            else: return self.case5(p, w, d1, self["dkMinus"][-1])
            
        """elif d1 % 2 == 1 and d1 > 3:
            if d: return self.case5(self, p, w, d1, self["dkMinus"][-1])
                if self["dkMinus"] == [] and self["dkPlus"] != []:
                    return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent, self["k"] + 1)

                elif self["dkPlus"] == [] and self["dkMinus"] != []:
                    return self.lemma4(self.tDict[self["dkMinus"][0]].parent, self.tDict[self["dkMinus"][-1]].parent, self["k"] - 1)

                elif self["dkMinus"] == [] and self["dkPlus"] == []:
                    #print("====== Lemma 4 line 138 - dkPlus and dkMinus both empty ======")
                    #print(self["dkMinus"])
                    #print(self["dk"])
                    #print(self["dkPlus"])
                    None

                else:
                    return 

            else:
                return self.case3(self, p, w, d1, k)

        elif d1 % 2 == 0 and d1 > 5:
            if d:
                return self.lemma4(self.tDict[self["dkMinus"][0]].parent, self.tDict[self["dk"][-1]].parent, k)

            #NOTE THESE OCCUR OFTEN
            elif self["dkMinus"] == []:
                try: return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent, k + 1)
                except: raise Exception("Sets empty")
            elif self["dkPlus"] == []:
                try: return self.lemma4(self.tDict[self["dkMinus"][0]].parent, self.tDict[self["dkMinus"][-1]].parent, k - 1)
                except: raise Exception("Sets empty")
            else:
                try: self.case5(self, p, w, d1, self["dkMinus"][-1])
                except: raise Exception("Sets empty")
                
        raise Exception("Reached end of return lemma4 function")"""


    def case1(self, p, w, d1):
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
            return self.lemma3(w, self.tDict[p].parent, self["dkPlus"][0], self["dkPlus"][-1])

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
            elif d2 == 4: return self.lemma4(self["dkPlus"][0], self["dkPlus"][-1], self.tDict[self["dkPlus"][0]].level + 1) #If d2 is 4 then the target is in children(wk+1, xk+1)

        #Now if zk has at most one child, then we probe w's parent
        elif len(self.tDict[zk].children) <= 1:
            d2 = self.probe(vkMinus2)

            if d2 == 0:   return self.located(vkMinus2)
            if d2 == 1:   return self.located(w)  #If d2 is 1 then the target is at w
            elif d2 == 2: return self.lemma2(w, vk, zk) #If d2 == 2 then the target is in siblings(vk, zk) so lemma 2
            elif d2 == 3: return self.lemma2(vk, self["dkPlus"][0], self["dkPlus"][-1]) #If d2 is 3 then target is in children(vk) excluding vk + 1, so lemma 2
            elif d2 == 4: return self.lemma4(self["dkPlus"][0], self["dkPlus"][-1], self.tDict[self["dkPlus"][0]].level + 1) #If d2 is 4 then the target is in children(wk+1, xk+1)

        raise Exception("Reached end of play function")
    

    def case2(self, p, w, d):
        """
         - Case 2: d is 2 or 3, so the target set is the children of w minus vk.
         - Args:
            - w  - The leftmost sibling in siblings(w, z) in lemma 4.
            - vk - The leftmost child of w.
        """
        if len(self["dk"]) == 1: return self.located(self["dk"][0])
        else:                    return self.lemma2(w, self["dk"][0], self["dk"][-1])
    

    def case3(self, p, w, d):
        """
         - Case 3: d is odd and greater than 3, so the target set contains all nodes
         - on level k that are d away. i.e children(yk-1, zk-1), so call Lemma 4 on.
        """
        if len(self["dk"]) == 1: return self.located(self["dk"][0])
        else:                    return self.lemma4(self["dkMinus"][0], self["dkMinus"][0], self["k"])
    

    def case4(self, p, w, d1):
        """
         - Case 4: d = 4, so dk-1 and dk+1 will contain nodes
        """
        if   self["dkPlus"]    == []:    #dk+1 empty, target in dkMinus, these are siblings so lemma 2
            return self.lemma2(self.tDict[self["dkMinus"][0]].parent, self.["dkMinus"][0], self.["dkMinus"][0][-1])

        elif self["dkMinus"] == []:     #dk-1 empty, so target set in dkPlus (children(wk, zk)) so lemma 4
            return self.lemma4(self.tDict[self["dkPlus"][0]].parent, self.tDict[self["dkPlus"][-1]].parent)

        zkMinus   = self["dkMinus"][-1]     #Get zk, wk-2's rightmost child
        p2, minus = (zkMinus, 1) if self.tDict[zkMinus].children == [] else (self.tDict[zkMinus].children[0], 0)
        d2        = self.probe(p2)          #Probe zk's first child or zk if there are no children

        if d2 == 0: return self.located(p2)
        if d2 == 1: return self.located(self.tDict[p2].parent)
            
        elif d2 == 2:
            if minus:                                  return self.lemma2(self.tDict[zkMinus].parent, self["dkMinus"][0], self["dkMinus"][-2])
            if len(self.tDict[zkMinus].children) == 1: return self.located(self.tDict[zkMinus].parent) #zk is zk-1's only child, target at zk's parent
            
            d3 = self.probe(w)

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
    
    
    def probe(self, v):
        """
         - Returns the distance from v to the target
        """
        if self.captTime == 0: self["probeList"] = []                       #Initialise probe list
        if self["t"] is None:  self["t"] = [choice(list(self.tree.nodes))]  #Random target start if none given

        self["probeList"].append(v) #Add probed node to probe list
        self.captTime += 1          #Increase capture time by one
                    
        d  = shortest_path_length(self.tree, v, self["t"][-1])               #Get dist from node to target
        self["t"].append(self.tMoveFunc(self.tree, self.tDict, self.lDict, self["t"][-1]))  #Move target according to given movement function

        return d


    def updateDSets(self, v, d):
        """
         - Updates the sets Dk-1, Dk, Dk+1
        """
        distances = single_source_dijkstra_path_length(self.tree, v)
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
        if level not in self.lDict:        self.lDict[level] = []
        if node  not in self.lDict[level]: self.lDict[level].append(node)

        nodeChildren     = [i for i in self.tree.neighbors(node) if i not in self.tDict]
        self.tDict[node] = nodeInfo(level, parent, nodeChildren)

        for child in nodeChildren: self.createTDict(child, parent = node, level = level + 1)


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
