from   localisation import *
from   natsort      import natsorted
import networkx     as     nx
import os

tStrats = [TargetMovement.tRandom, TargetMovement.tProbabilistic, TargetMovement.tUpDown]               #Each target strategy
pStrats = [ProbeMovement.pTLeft, ProbeMovement.pTRight, ProbeMovement.pBLeft, ProbeMovement.pBRight]    #Each probe strategy

resFile = open("tWinsResults.txt", 'w') #Results outfile

for pStrat in pStrats:      #Iterate probe  strats
    tWins      = []
    percentage = []
    
    for tStrat in tStrats:  #Iterate target strats
        wins  = 0
        total = 0
        
        for graphName in natsorted(os.listdir("treeFiles")):    #Iterate graph files
            tree = nx.read_adjlist("treeFiles\\" + graphName)   #Read graph as nx object
            
            for startNode in range(len(tree)):  #Use each node as a starting point
                game = Localisation(            #Initialise game instance with start location
                    tree      = tree,
                    tMoveFunc = tStrat,
                    pMoveFunc = pStrat,
                    tMoveList = [str(startNode)]
                )
                
                result = game.play()
                
                if game.win == "Target": wins += 1
                total += 1
                
        tWins.append(wins)
        percentage.append(wins / total)
    
    resFile.write("Probe: "      + str(pStrat))
    resFile.write("\ntWins: "      + str(tWins))
    resFile.write("\nPercentage: " + str(percentage) + "\n")

resFile.close()