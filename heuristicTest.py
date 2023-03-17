from heuristicMovement   import probeMovement, targetMovement
from localisation        import Localisation
from localisation.probe  import Probe
from localisation.target import Target
import networkx as nx
import os, re, time

treeDir = "randomTrees/"


resultsName = "randomTreesResults.csv"
resultsFile = open(resultsName, 'w')
resultsFile.write("Player Types, Num Nodes, Avg Capture Time (Num Rounds), Avg Run Time (s), P Win / T Win\n")


def runTest(tPlayer, pPlayer):
    for fName in os.listdir(treeDir):   #Iterate over test dir
        numNodes = str(re.findall(r'\d+', fName)[0])    #Get num nodes
        tree     = nx.read_adjlist(treeDir + fName)     #Read tree

        totalTime = 0   #Total time over 10 runs
        captTime  = 0   #Capture time when P wins
        pWin = 0        #Num times P won
        tWin = 0        #Num times T won

        for i in range(10):
            game = Localisation(tree, tPlayer, pPlayer)

            startTime = time.time()
            game.play()
            totalTime += time.time() - startTime

            if game.win == "Probe":
                print("Num Nodes:", numNodes)
                print("Probe moves:", pPlayer.moveList)
                print("Target moves:", tPlayer.moveList)
                captTime += game.captTime
                pWin += 1

            else:
                tWin += 1

        if pWin > 0:
            resultsFile.write(pTypes + "," + numNodes + "," + str(captTime / float(pWin)) + "," + str(totalTime / 10.0) + "," + str(pWin) + "/" + str(tWin) + "\n")

        else:
            resultsFile.write(pTypes + "," + numNodes + ",-1," + str(totalTime / 10.0) + "," + str(pWin) + "/" + str(tWin) + "\n")


#====================================#
pTypes = "Random Probe Random Target"   #Probe and player types

pPlayer = Probe(probeMovement.random)
tPlayer = Target(None, targetMovement.random)

runTest(tPlayer, pPlayer)


#====================================#
pTypes = "Random Probe UpTree Target"   #Probe and player types

pPlayer = Probe(probeMovement.random)
tPlayer = Target(None, targetMovement.upTree)

runTest(tPlayer, pPlayer)

#====================================#
pTypes = "Random Probe downTree Target"   #Probe and player types

pPlayer = Probe(probeMovement.random)
tPlayer = Target(None, targetMovement.downTree)

runTest(tPlayer, pPlayer)

#====================================#
pTypes = "Random Leaf Probe Random Target"   #Probe and player types

pPlayer = Probe(probeMovement.randomLeaf)
tPlayer = Target(None, targetMovement.random)

runTest(tPlayer, pPlayer)

#====================================#
pTypes = "Random Leaf Probe UpTree Target"   #Probe and player types

pPlayer = Probe(probeMovement.randomLeaf)
tPlayer = Target(None, targetMovement.upTree)

runTest(tPlayer, pPlayer)

#====================================#
pTypes = "Random Leaf Probe downTree Target"   #Probe and player types

pPlayer = Probe(probeMovement.randomLeaf)
tPlayer = Target(None, targetMovement.downTree)

runTest(tPlayer, pPlayer)

#====================================#

resultsFile.close()

