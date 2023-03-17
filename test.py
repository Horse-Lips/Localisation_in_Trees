from heuristicMovement   import targetMovement
from localisation        import Localisation
from localisation.probe  import Probe
from localisation.target import Target
import networkx as nx
import os, re, time


#tree = nx.read_adjlist("randomTrees/randomTree500.txt")
tree = nx.read_adjlist("randomTrees/seagTree101.txt")
print(tree)
resFile = open("tLeftProbeProbTarget.txt", 'w')

tWinCount = 0
pWinCount = 0

pWinAvgCaptTime = 0
avgCaptTime     = 0

for i in range(1, 11):
    resFile.write(" ====== Run " + str(i) + " ====== \n")
    pPlayer = Probe("tLeft")
    tPlayer = Target(None, targetMovement.prob)
    game = Localisation(tree, tPlayer, pPlayer)

    startTime = time.time()
    game.play()
    endTime  = time.time() - startTime

    captTime = game.captTime
    winner   = game.win

    resFile.write("Start location: " + str(game.target.moveList[0]) + "\n")
    resFile.write("Time taken: " + str(endTime) + "\n")
    resFile.write("Capture time: " + str(captTime) + "\n")
    resFile.write("Winner: " + winner + "\n\n")

    if winner == "Probe":
        pWinCount += 1
        pWinAvgCaptTime += captTime

    else:
        tWinCount += 1

    avgCaptTime += captTime

resFile.write(" ====== Averages and Win Rates ====== \n")
resFile.write("Overall avg capt time: " + str(avgCaptTime / 10) + "\n")
resFile.write("Probe win avg capt time: " + str(pWinAvgCaptTime / pWinCount) + "\n")
resFile.write("Wins: T = " + str(tWinCount) + " | P = " + str(pWinCount))

resFile.close()