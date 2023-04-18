def case3(self, p, w, d, k):
    """
     - Case 3: d is odd and greater than 3, so the target set contains all nodes
     - on level k that are d away. i.e children(yk-1, zk-1), so call Lemma 4 on.
    """
    if len(self["dk"]) == 1: return self.located(self["dk"][0])
    return self.lemma4(self["dkMinus"][0], self["dkMinus"][0], self["k"])
