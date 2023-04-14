from   seager            import Seager
from   heuristicMovement import *
from   heuristicClass    import *
import networkx          as     nx
import os, re, time


pStrats = ["tLeft",  "tRight", "bLeft", "bRight", "Seager"] #Each probe  strategy
tStrats = ["Random", "Prob",   "UpDown"]                    #Each target strategy

resFile = open("experimentResults.txt", 'w')

for pStrat in pStrats:      #Iterate probe  strats
    resFile.write(pStrat + "\n")
    print("Probe strat:", pStrat)
    
    for tStrat in tStrats:  #Iterate target strats
        resFile.write(tStrat + "\n")
        print("Target strat:", tStrat)
        
        for graphNum in range(3, 201):    #Iterate over tree files
            treeFile = "randomTree" + str(graphNum) + ".txt"
            resFile.write(treeFile + " = ")
            print("Current tree:", treeFile)
            
            tree = nx.read_adjlist("treeFiles\\" + treeFile)    #Load tree file as nx graph
            nodeAvgs = []
            
            for startNode in range(len(tree)):      #Use each node as a starting position
                currNodeAvg = 0
                
                for i in range(25):                #Start from each node 100 times for a mean
                    if pStrat == "Seager":
                        if   tStrat == "Random": game = Seager(tree, tRandom)
                        elif tStrat == "Prob":   game = Seager(tree, tProbabilistic)
                        elif tStrat == "UpDown": game = Seager(tree, tUpDown)
                            
                        game["t"] = [str(startNode)]
                        
                    else:
                        pPlayer = Probe(pStrat)
                        
                        if  tStrat == "Random": tPlayer = Target(None, tRandom)
                        elif tStrat == "Prob":  tPlayer = Target(None, tProbabilistic)
                        elif tStrat == "UpDown":tPlayer = Target(None, tUpDown)
                        
                        tPlayer.moveList.append(str(startNode))
                        
                        game = Localisation(tree, tPlayer, pPlayer, tInitial = str(startNode))

                    result = None
                    while result is None:
                        try:
                            result = game.play()
                            currNodeAvg += game.captTime
                            
                        except:
                            pass
                            
                nodeAvgs.append(currNodeAvg / 25)
            
            resFile.write(str(nodeAvgs) + "\n")
    
resFile.close()
