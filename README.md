# A Practical View of the Localisation Game
The localisation game is a graph-based pursuit-evasion game where a hidden target moves between the nodes of a graph and a probing player attempts to detemrine its location using distance queries. The primary focus of this project is to assess Suzanne Seager's strategy for rooted trees ([https://www.sciencedirect.com/science/article/pii/S0304397512006469](https://www.sciencedirect.com/science/article/pii/S0304397514003119)). All code is implemented in Python and graphs use the NetworkX library (https://networkx.org/) with a custom representation of trees.

## Game Rules
- The game is played in rounds
- The target's initial move is to select some vertex of the graph
- In subsequent rounds the target may move anywhere in the neighbourhood of its currently occupied vertex
- The probing player selects **1** vertex and receives the distance between that vertex and the invisible target
- The target wins in theory if it is never caught
  - In practice this is determined using an upper limit, for example 5 * n rounds where n is the number of nodes in the graph
- The probing player wins if it is able to locate the target in a finite number of rounds
  - In practice this is similarly determined by the same threshold
- This variant of the localisation game was created by Carraher et al. (https://www.sciencedirect.com/science/article/pii/S0304397512006469).
- For the purposes of this implementation **All probing strategies initially probe the root of the tree** (See Target Set)

## Usage
### Installing Requirements
All required libraries can be found in ```requirements.txt```. These can be installed using ```python -m pip install -r requirements.txt```.

### Definitions
#### Custom Tree Representation
The ```createTDict(node, tDict, lDict, tree, parents = None, level = 0)``` function found in the ```Utils``` class of ```localisation.py``` creates a representation of the levels and orderings of a NetworkX tree object as two dictionaries. These are referred to as the ```tDict``` (treeDict) and ```lDict``` (levelsDict). These are necessary as NetworkX does not provide explicit tree representations and views them as general graphs and also as probing strategies require the tree to be ordered in a certain way with access to the individual levels of the tree. A ```NodeInfo``` object, found in ```localisation.py``` is initialised as follows:

```
node = NodeInfo(
  level,    #Level of the tree the node is located on
  parent,   #The node's parent
  children  #An ordered list of the node's children
)
```

```tDict``` and ```lDict``` objects are Python dictionaries as described below:
- ```tDict```
  - A key for each node label, e.g. key 1 for node 1
  - An entry of the ```NodeInfo``` object for that node
- ```lDict```
  - A key for each level in the tree, e.g. level 0 containing just the root of the tree
  - An entry of an ordered list of nodes on that level of the tree

#### Target Set
The target set is the set of possible target locations known to the probing player. This is determined by probing the root initially and obtaining the distance d, and therefore knowing that the target could occupy any node on level d of the tree. This allows the target to be tracked while moving throughout the tree as after moving the target could occupy any node on this level, or the parents or children of nodes on this level. This allows the target set to be split into three distinct sets, one for each level of the tree that the target may occupy.

### Graph Generation - ```localisation.py``` ```Utils``` Class
Usage: ```Utils.generateRandomGraph(numNodes)``` Where ```numNodes``` is the number of nodes in the tree. A number of randomly generated trees can be found in the ```treeFiles``` folder with node counts ranging from 3 to 150 nodes. This script generates hideout-free trees. A hideout is a subgraph that enables the target to theoretically evade capture indefinitely, Seager's example hideout is shown here:

<img src="images/hideout.png">

Graphs are limited to 150 nodes as it is a difficult task to generate large hideout-free trees. Graphs are generated using NetworkX's random_tree function (https://networkx.org/documentation/stable/reference/generated/networkx.generators.trees.random_tree.html).

### Target Strategies - ```localisation.py``` ```TargetMovement``` Class
As the game is usually analysed theoretically, an optimal target with perfect knowledge is assumed. This is not practical from an implementation perspective so several suboptimal target strategies have been implemented in the ```TargetMovement``` class. Each target strategy is given the arguments:

```
tree      #NetworkX tree object
tDict     #tDict representation of the tree
lDict     #lDict representation of the tree
node      #The node currently occupied by the target
```

```
TargetMovement.tRandom(tree, tDict, lDict, node)         #Move to a completely random node in the neighbourhood of the current node
TargetMovement.tUpTree(tree, tDict, lDict, node)         #Move up or down the levels of the tree with some pre-defined probability, higher probability of moving up the tree
TargetMovement.tDownTree(tree, tDict, lDict, node)       #Move up or down the levels of the tree with some pre-defined probability, higher probability of moving down the tree
TargetMovement.tUpDown(tree, tDict, lDict, node)         #Combination of the above two strategies with a chance of remaining at the current node
TargetMovement.tProbabilistic(tree, tDict, lDict, node)  #Target moves to neighbours based on a defined neighbourhood probability based on node degrees (See below)
```

In the probabilistic strategy the target moves to a node in the neighbourhood N where each node m in the neighbourhood is assigned the probability $\frac{deg(m)}{\sum_{n \in N}deg(n)}$. These movement generation functions are given when initialising either a ```Localisation``` or ```Seager``` object as the ```tMoveFunc``` argument.

### Probing Strategies - ```localisation.py``` ```ProbeMovement``` Class
The ```ProbeMovement``` class contains simple functions for probe placement including each version of the simplified Seager approach. Each probing strategy initially probes the root of the tree. Each probing strategy is given the arguments:

```
tree      #NetworkX tree object
tDict     #tDict representation of the tree
lDict     #lDict representation of the tree
probeList #A list of all previous nodes probed
d         #Distance between the previous probe and the target
```

```
pRandom(tree, tDict, lDict, probeList, d)     #Probes are placed completely randomly on the tree
pRandomLeaf(tree, tDict, lDict, probeList, d) #Probes are placed on completely random leaf nodes in the tree
pTLeft(tree, tDict, lDict, probeList, d)      #Simple Seager using the top left node of the target set
pTRight(tree, tDict, lDict, probeList, d)     #Simple Seager using the top right node of the target set
pBLeft(tree, tDict, lDict, probeList, d)      #Simple Seager using the bottom left node of the target set
pBRight(tree, tDict, lDict, probeList, d)     #Simple Seager using the bottom right node of the target set
```

These movement generation functions are given when initialising a ```Localisation``` object as the ```pMoveFunc``` argument.

### Localisation Object - ```localisation.py``` ```Localisation``` Class
The ```Localisation``` class manages gameplay for both target and probing players as well as maintaining information throughout the game, such as the tree object, round number, winner, and capture time. The class can be initialised as follows:

```
game = Localisation(
  tree,       #NetworkX representation of the tree
  tMoveFunc,  #See Target Strategies for a list of options
  pMoveFunc,  #See Probing Strategies for a list of options
  tMoveList,  #Initial locations the target has visited (**Optional**)
  pMoveList   #Initial locations the probing player has probed (**Optional**)
)
```

The class will generate any future moves after ```tMoveList``` has been exhausted using ```tMoveFunc```. The game can be started by calling the play function, ```game.play()```.

After the game is finished, information about the game can be access as follows:
```
game.tMoveList  #List of nodes the target occupied throughout the game
game.pMoveList  #List of nodes probed throughout the game
game.win        #Winner of the game as a string, either "Target" or "Probe"
game.captTime   #Number of rounds before a winner was determined
```

### Seager Object - ```localisation.py``` ```Seager``` Class
The Seager class functions similarly to the Localisation class but with a pre-defined probing strategy, that being Seager's strategy for rooted trees. As it is a large and complex class only the necessary components are detailed here. The class can be initialised as follows:

```
game = Seager(
  tree,       #NetworkX representation of the tree
  tMoveFunc,  #See Target Strategies for a list of options
  tMoveList   #Initial locations the target has visited (**Optional**)
)
```

The class will generate any future moves after ```tMoveList``` has been exhausted using ```tMoveFunc```. The game can be started by calling the play function, ```game.play()```.

The class also acts as a dictionary. This is useful for maintaining information during execution as well as retriving this information after the game is over. Commonly accessed information includes:
```
game["trace"]     #Verbose information about the execution of the game, which functions were called and which nodes or target sets were passed to these functions
game["probeList"] #A list of nodes probed by the probing player
game["t"]         #A list of nodes occupied by the target throughout the game
```

### Capture and Run Time Experiments - ```experiment-captureTime.py```
This script is responsible for running the main experiment. Usage: ```python experiment-captureTime.py probeStrategy``` where probe strategy can be one of ```tLeft```, ```tRight```, ```bLeft```, ```bRight```, ```seager```. The script will iterate over each graph in the ```treeFiles``` folder and begin a game with each node of the graph as a starting point for the target, each node will be used as a starting point 25 times a total of 3 times, 25 times per target strategy. The average capture and run times of these 25 executions being reported as the capture time when starting at that node. The script will output a results file containing these averaged times for each node as ```experimentResults.txt``` prefixed with the given probe strategy string. For example ```python experiment-captureTime.py tLeft``` will output the file ```tLeftexperimentResults.txt```.

### Target Wins Experiment - ```experiment-targetWins.py```
This script is responsible for counting the number of target wins when using the simplified Seager strategy. Usage: ```python experiment-targetWins.py```. This script will play a game with each combination of probe and target strategies on each graph in the ```treeFiles``` folder using each node of the graph as a starting point. This will output a file ```tWinsResults.txt``` which records each probing strategy, the number of target wins for each target strategy, and the percentage of target wins for each target strategy as a decimal. These are given as lists of three floats. The order of target strategies in each list is ```tRandom```, ```tProbabilistic```, ```tUpDown```.

### Plotting Results - ```plot-avgCaptureTime.py```
This script will iterate over a given results file and average the capture times of each graph before producing a matplotlib (https://matplotlib.org/) graph of average capture time compared with number of nodes in the graph. Usage: ```python plotResults resultsFile``` where ```resultsFile``` is an output of running the ```experiment-captureTime.py``` script.

### Calculating Average Run Times - ```calculate-avgRunTime.py```
This script simply calculates the average run time of a probing strategy against each target strategy. Usage: ```python calculate-avgRunTime.py resultsFile``` where ```resultsFile``` is an output of running the ```experiment-captureTime.py``` script. This script will output to the terminal a list of average run times calculated as the average of all run times in the results file. Each average run time represents the average run time of a particular target strategy, ordered ```tRandom```, ```tProbabilistic```, ```tUpDown```.
