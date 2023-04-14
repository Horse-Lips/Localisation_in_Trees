from ._lemma2 import lemma2


def case2(self, p, w, d, k):
    """
     - Case 2: d is 2 or 3, so the target set is the children of w minus vk.
     - Args:
        - w  - The leftmost sibling in siblings(w, z) in lemma 4.
        - vk - The leftmost child of w.
    """
    if len(self["dk"]) == 1:
        return self.located(self["dk"][0])

    return lemma2(self, w, self["dk"][0], self["dk"][-1])
