from random import choice, uniform, randint
from numpy  import cumsum
import networkx as nx


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
