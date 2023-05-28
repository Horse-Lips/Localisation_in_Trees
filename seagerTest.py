from   seagerNew         import Seager
from   heuristicMovement import tProbabilistic
import networkx          as     nx


tree = nx.read_adjlist("treeFiles\\randomTree103.txt")
game = Seager(tree, tProbabilistic)
game.play()

print(game["t"])
print(game["probeList"])
