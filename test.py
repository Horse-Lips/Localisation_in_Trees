from heuristicMovement import *
from heuristicClass    import *
import networkx as nx
import os, re, time


#tree = nx.read_adjlist("treeFiles/randomTree50.txt")
tree = nx.read_adjlist("treeFiles/seagTree101.txt")
resFile = open("tRightProbeProbTarget.txt", 'w')

tWinCount = 0
pWinCount = 0

pWinAvgCaptTime = 0
avgCaptTime     = 0

for i in range(1, 11):
    resFile.write(" ====== Run " + str(i) + " ====== \n")
    
    pPlayer = Probe("tRight")                #Create probe player with move function
    tPlayer = Target(None, tProbabilistic)  #Create target player with move function
    
    tInitialMove = str(((len(tree) - 1) // 10) * i)    #Use every n/10th node rounded down as start position
    tPlayer.moveList.append(tInitialMove)
    
    game = Localisation(tree, tPlayer, pPlayer, tInitial = tInitialMove)

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