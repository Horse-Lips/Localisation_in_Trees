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
    
    if p == self["t"][-1]: return self.located(p)
    d1 = self.probe(p)

    if d1 == 1:
        return self.located(self.tDict[p].parent)
        
    elif d1 == 2:
        if not d:
            return self.located(v)

        if len(sibList) == 2:
            return self.located(sibList[1])

        else:
            return lemma2(self, v, sibList[1 - r], sibList[-1 - r])

    elif d1 == 3:
        if d:
            if len(sibList) == 2:
                return self.lemma4(sibList[1 - r], sibList[1 - r], self.tDict[w].level + 1)

            else:
                return self.lemma4(sibList[1 - r], sibList[-1 - r], self.tDict[w].level + 1)

        if len(sibList) == 2:
            return self.located(sibList[1 - r])

        else:
            return lemma2(self, v, sibList[1 - r], sibList[-1 - r])

    elif d1 == 4:
        if len(sibList) == 2:
            return self.lemma4(sibList[1 - r], sibList[1 - r], self.tDict[w].level + 1)

        else:
            return self.lemma4(sibList[1 - r], sibList[-1 - r], self.tDict[w].level + 1)

    raise Exception("Reached end of play function")
