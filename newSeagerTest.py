from localisation import *
import networkx as nx


tree = nx.read_adjlist("treeFiles\\randomTree100.txt")

game = Localisation(tree, TargetMovement.tProbabilistic, ProbeMovement.seager)
game.play()
print(game.win)