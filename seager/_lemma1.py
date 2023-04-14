from networkx import relabel_nodes


def lemma1(self):
    """
     - Organise the children such that the first vertex has highest degree and the
     - last has second highest. Also enforce Lemma 1: Any vertex with more than two
     - children that have higher degree than 3 means there is a hideout in the tree.
     - Returns:
        - 1  if no hideouts are detected in the tree
        - -1 if a hideout is detected in the tree
    """
    labelMap = dict()

    for node in self.tDict:
        if node == "leaves":
            continue
            
        oldChildren = self.tDict[node].children

        if len(oldChildren) < 3:
            continue

        childDegs = [len(self.tDict[child].children) for child in oldChildren]
        deg3Count    = sum(deg >= 2 for deg in childDegs)

        if deg3Count > 2:
            return -1
        
        maxDeg = childDegs.index(max(childDegs))    #Slow but gets max value
        secDeg = 0

        for i in range(len(childDegs)):
            if childDegs[maxDeg] > childDegs[i] > childDegs[secDeg]:
                secDeg = i

        if sum(childDegs) != len(childDegs):    #Don't adjust children if all have degree 1
            continue

        if maxDeg != 0: #Dont adjust max if its already at index 0
            labelMap[oldChildren[maxDeg]]        = oldChildren[0]
            labelMap[oldChildren[0]]             = oldChildren[maxDeg]
            oldChildren[0],  oldChildren[maxDeg] = oldChildren[maxDeg], oldChildren[0]
            
        if secDeg != len(childDegs) - 1 and secDeg != 0:
            labelMap[oldChildren[secDeg]]        = oldChildren[-1]
            labelMap[oldChildren[-1]]            = oldChildren[secDeg]
            oldChildren[-1], oldChildren[secDeg] = oldChildren[secDeg], oldChildren[-1]

    self.tree = relabel_nodes(self.tree, labelMap, copy = True)  #Update altered node labels

    self.tDict = dict()
    self.lDict = dict()

    self.createTDict("0")

    return 1

