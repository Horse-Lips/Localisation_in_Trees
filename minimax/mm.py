from math import inf
import networkx as nx


class Minimax():
    """
     - MiniMax solver class for the Localisation game.
     - The solve() function acts as the main method.
     - Target plays as MAX player and probe plays as MIN
     - as target wants to maximise its time on the graph
     - and probe wants to minimise number of rounds.
     - Variables:
        - tree    - NetworkX tree object
        - tDict   - Dict representation of the tree
        - lDict   - Dict representation of levels in the tree
        - iDict   - Dictionary of useful information during execution, containing:
            - numRounds - Number of rounds that have taken place
            - pMoves    - Every node probed by the probe
            - tMoves    - Every node occupied by the target
            - tWin      - Number of rounds before target wins
        - dkMinus - Possible robber locations for each turn on level k - 1
        - dk      - Possible robber locations for each turn on level k
        - dkPlus  - Possible robber locations for each turn on level k + 1
        - tSet    - Lists of possible target locations on each turn
    """
    def __init__(self, tree, tDict, lDict):
        self.tree  = tree
        
        self.tDict = tDict
        self.lDict = lDict
        self.iDict = dict()

        self.iDict["numRounds"] = 0
        self.iDict["pMoves"]    = []
        self.iDict["tMoves"]    = []
        self.iDict["tWin"]      = len(tree)

        self.dkMinus = dict()
        self.dk      = dict()
        self.dkPlus  = dict()
        
        self.tSet    = dict()


    def __setitem__(self, key, value):
        self.iDict[key] = value


    def __getitem__(self, key):
        try:    return self.iDict[key]
        except: return None


    def getMoves(self, player):
        """
         - Given a player, returns the available moves for that player.
         - For the target, return the neighbourhood of the node the
         - target occupies and the node itself as options. For the probe
         - either probe the root or calculate the D sets as in Seager
         - and offer top left/right and bottom left/right as options.
        """
        if player == -1:    #Get target moves
            if self["tMoves"] == []:
                return [i for i in range(len(self.tree))]   #Target can pick any initial node

            else:
                return [i for i in self.tree.neighbors(self["tMoves"][-1])] + [self["tMoves"][-1]]

        else:               #Get probe moves
            if self["pMoves"] == [] or self["numRounds"] % 3 == 0:  #Initial and every third probe are the root
                return [0]

            elif self["numRounds"] % 2 != 0:                        #Probe top/bottom left/right after root
                return [self["dkMinus"][0], self["dkMinus"][-1], self["dkPlus"][0], self["dkPlus"][-1]]

            else:                                                   #Probe last remaining top/bottom left/right
                return [self["dkMinus"][0], self["dkMinus"][-1], self["dkPlus"][0], self["dkPlus"][-1]]


    def makeMove(self, player, node):
        """
         - Play the given node for the given player.
        """
        if player == 1:
            self["numRounds"] += 1
            self["pMoves"].append(node)
            
            d = nx.shortest_path_length(self.tree, self["pMoves"][-1], self["tMoves"][-1])
            
            if self["pMoves"] == [] or self["numRounds"] % 3 == 0:
                self.dkMinus[self["numRounds"]] = self.lDict[d - 1]
                self.dk[self["numRounds"]]      = self.lDict[d]
                self.dkPlus[self["numRounds"]]  = self.lDict[d + 1]
            
        else:
            self["tMoves"].append(node)


    def undoMove(self, player):
        if player == 1:
            self["numRounds"] -= 1
            self["pMoves"] = self["pMoves"][0:-1]

        else:
            self["tMoves"] = self["tMoves"][0:-1]


    def minimax(self, player):
        bestMove = [0, -1 * player * inf]

        for move in self.getMoves(player):
            self.makeMove(player, move)
            score = self.minimax(-1 * player)
            self.undoMove(player)

            score[0] = i

            if (player == 1 and score[1] > bestMove[1]) or (player == -1 and score[1] < bestMove[1]):
                bestMove = score

        return bestMove