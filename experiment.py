from   localisation import *
import networkx     as     nx
import time, sys


tStrats = [TargetMovement.tRandom, TargetMovement.tProbabilistic, TargetMovement.tUpDown]   #Each target strategy
pStrats = {"tLeft":  ProbeMovement.pTLeft, "tRight": ProbeMovement.pTRight, "bLeft":  ProbeMovement.pBLeft, "bRight": ProbeMovement.pBRight}
resFile = open(sys.argv[1] + "experimentResults.txt", 'w')
resFile.write(sys.argv[1] + "\n")
print("Probe strat:", sys.argv[1])

for tStrat in tStrats:  #Iterate target strats
    resFile.write(str(tStrat) + "\n")
    print("Target strat:", tStrat)
    
    for graphNum in range(3, 151):    #Iterate over tree files
        resFile.write("randomTree" + str(graphNum) + "\n")
        print("Current tree: randomTree", str(graphNum))
        
        tree = nx.read_adjlist("treeFiles\\randomTree" + str(graphNum) + ".txt")    #Load tree file as nx graph
        nodeAvgs  = []
        nodeTimes = []
        
        for startNode in range(len(tree)):      #Use each node as a starting position
            currNodeAvg  = 0
            currNodeTime = 0
            
            for i in range(25):                 #Start from each node 100 times for a mean
                result = None
                
                while result is None:
                    if sys.argv[1] == "seager":
                        game = Seager(tree, tStrat)
                        game["t"] = [str(startNode)]
                        
                    else:
                        pPlayer = Probe(pStrats[sys.argv[1]])
                        tPlayer = Target(None, tStrat)
                        tPlayer.moveList.append(str(startNode))
                        game = Localisation(tree, tPlayer, pPlayer, tInitial = str(startNode))


                    try:
                        start  = time.time()
                        result = game.play()
                        
                        currNodeAvg  += game.captTime
                        currNodeTime += time.time() - start
                        
                    except:
                        pass
                        
            nodeAvgs.append( currNodeAvg  / 25)
            nodeTimes.append(currNodeTime / 25)
        
        resFile.write("Capture Times: " + str(nodeAvgs) + "\n")
        resFile.write("Run Times: " + str(nodeTimes) + "\n")
    
resFile.close()
