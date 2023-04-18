from ._lemma2 import lemma2


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
        if d: return lemma2(self, v, w, z)
        else: return self.located(v)

    elif d1 == 3:
        if d: return self.lemma4(w, z, self.tDict[w].level + 1)
        else: return lemma2(self, v, w, z)

    elif d1 == 4: return self.lemma4(w, z, self.tDict[w].level + 1)

    raise Exception("Reached end of play function")
