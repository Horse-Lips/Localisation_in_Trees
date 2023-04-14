from seager            import Seager
from heuristicMovement import *
from heuristicClass    import *
import networkx as nx
import os, re, time


#tree = nx.read_adjlist("treeFiles/randomTree500.txt")
tree = nx.read_adjlist("treeFiles/randomTree10.txt")
resFile = open("seagerProbeProbTarget.txt", 'w')

tWinCount = 0
pWinCount = 0

pWinAvgCaptTime = 0
avgCaptTime     = 0

for i in range(len(tree)):
    resFile.write(" ====== Run " + str(i) + " ====== \n")
    
    #pPlayer = Probe("tRight")                #Create probe player with move function
    #tPlayer = Target(None, tUpDown)  #Create target player with move function
    
    tInitialMove = str(i)    #Use every n/10th node rounded down as start position
    #tPlayer.moveList.append(tRandom)
    
    #game = Localisation(tree, tPlayer, pPlayer, tInitial = tInitialMove)   #Using heuristic setup
    game = Seager(tree, tProbabilistic)     #Using Seager setup
    game["t"] = [tInitialMove]
    
    startTime = time.time()
    
    finished = None
    while finished is None:
        try:    finished = game.play()
        except: pass
       
    endTime  = time.time() - startTime

    captTime = game.captTime
    winner   = game.win

    try:    resFile.write("Start location: " + str(tInitialMove) + "\n")
    except: resFile.write("Start location: " + str(tInitialMove) + "\n")
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