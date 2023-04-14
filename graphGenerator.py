"""
 - Simple script used for generating hide-out free.
 - trees Given a number n as command line argument
 - will generate a hideout-free tree with n nodes.
"""
import sys
import networkx as nx


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


def detectHideouts(tDict):
    """
     - Detects hideouts in a tree defined as a node with at least
     - 3 neighbours each of which have at least 3 neighbours.
     - Variables:
        - tDict - tDict representation of the tree (See genTreeDicts)
    """
    for node in tDict:        
        children = tDict[node].children     #Get node's children
        parent   = tDict[node].parent       #Get node's parent
        
        if   parent is not None and len(children) < 2: continue   #Node must have degree >= 3 to be a hideout
        elif parent is     None and len(children) < 3: continue

        childDegs = [(len(tDict[child].children) + 1) for child in children]     #Degrees of node's children
        parentDeg = 0
        if parent is not None: parentDeg = len(tDict[parent].children) + 1 if tDict[parent].parent is not None else 0    #Work out degree of parent node
        
        deg3Count = sum(deg >= 3 for deg in childDegs) + 1 if parentDeg >= 3 else 0   #Number of neighbours with degree 3
        
        if deg3Count >= 3: return 0 #Return -1 if more than 2

    return 1


def genTreeDicts(tree, node, parent = None, level = 0):
    """
     - Converts a tree to a dictionary, where keys are the
     - the node's ID and values are nodeInfo entries as above.
     - Args:
        - tree   - A NetworkX tree object
        - node   - Node to add to the dictionary.
        - parent - The node's parent if it exists.
        - level  - The level in the tree that the node is on.
    """
    nodeChildren = [i for i in tree.neighbors(node) if i not in tDict]
    tDict[node]  = nodeInfo(level, parent, nodeChildren)

    for child in nodeChildren: genTreeDicts(tree, child, parent = node, level = level + 1)

tDict = dict()

tree = nx.random_tree(int(sys.argv[1]))
genTreeDicts(tree, 0)

if not detectHideouts(tDict): print("Hideout detected")
else:                         nx.write_adjlist(tree, "treeFiles/randomTree" + sys.argv[1] + ".txt")
