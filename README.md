# A Practical View of the Localisation Game
The localisation game is a graph-based pursuit-evasion game where a hidden target moves between the nodes of a graph and a probing player attempts to detemrine its location using distance queries. The primary focus of this project is to assess Suzanne Seager's strategy for rooted trees (https://www.sciencedirect.com/science/article/pii/S0304397512006469). All code is implemented in Python and graphs use the NetworkX library (https://networkx.org/) with a custom representation of trees.

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
### Definitions
#### Custom Tree Representation
Within each localisation class there exist functions that represent the levels and orderings of a tree as dictionaries, referred to as the tDict (treeDict) and lDict (levelsDict). These are necessary as NetworkX does not provide explicit tree representations and views them as general graphs and because the probing strategies require the tree to be ordered in a certain way with access to the individual levels of the tree. A nodeInfo object is initialised as follows:

```
node = nodeInfo(
  level,    #Level of the tree the node is located on
  parent,   #The node's parent
  children  #An ordered list of the node's children
)
```

The tDict and lDict objects are Python dictionaries as described below:
- tDict
  - A key for each node label, e.g. key 1 for node 1
  - An entry of the nodeInfo object for that node
- lDict
  - A key for each level in the tree, e.g. level 0 containing just the root of the tree
  - An entry of an ordered list of nodes on that level of the tree

#### Target Set
The target set is the set of possible target locations known to the probing player. This is determined by probing the root initially and obtaining the distance d, and therefore knowing that the target could occupy any node on level d of the tree. This allows the target to be tracked while moving throughout the tree as after moving the target could occupy any node on this level, or the parents or children of nodes on this level. This allows the target set to be split into three distinct sets, one for each level of the tree that the target may occupy.

### Graph Generation - graphGenerator.py
Usage: ```python graphGenerator.py n``` Where n is the number of nodes in the tree. A number of randomly generated trees can be found in the treeFiles folder with node counts ranging from 3 to 150 nodes. This script generates hideout-free trees. A hideout is a subgraph that enables the target to theoretically evade capture indefinitely, Seager's example hideout is shown here:

<img src="images/hideout.png">

Graphs are limited to 150 nodes as it is a difficult task to generate large hideout-free trees. Graphs are generated using NetworkX's random_tree function (https://networkx.org/documentation/stable/reference/generated/networkx.generators.trees.random_tree.html).

### Target Strategies - heuristicMovement.py
As the game is usually analysed theoretically an optimal target with perfect knowledge is assumed. As this is not practical from an implementation perspective, several suboptimal target strategies have been implemented in the heuristicMovement.py file. Each target strategy is given as arguments:

```
tree      #NetworkX tree object
tDict     #tDict representation of the tree
lDict     #lDict representation of the tree
node      #The node currently occupied by the target
```

```
tRandom(tree, tDict, lDict, node)         #Move to a completely random node in the neighbourhood of the current node
tUpTree(tree, tDict, lDict, node)         #Move up or down the levels of the tree with some pre-defined probability, higher probability of moving up the tree
tDownTree(tree, tDict, lDict, node)       #Move up or down the levels of the tree with some pre-defined probability, higher probability of moving down the tree
tUpDown(tree, tDict, lDict, node)         #Combination of the above two strategies with a chance of remaining at the current node
tProbabilistic(tree, tDict, lDict, node)  #Target moves to neighbours based on a defined neighbourhood probability based on node degrees (See below)
```

In the probabilistic strategy the target moves to a node in the neighbourhood N where each node m in the neighbourhood is assigned the probability $\frac{deg(m)}{\sum_{n \in N}deg(n)}$.

Each of these can be given to either a Target object (See Localisation, Probe, and Target Classes) or a Seager object (See Seager's Probing Strategy).

### Probing Strategies - heuristicMovement.py
The heuristicMovement.py file also contains some simple functions for probe placement. Each probing strategy initially probes the root of the tree. Each probing strategy is given as arguments:

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
```

Each of these can be given to a Probe object (See Localisation, Probe, and Target Classes)

### Probing Strategies - heuristicClass.py
The Simplified Seager strategy is implemented as a part of the Probe class found in heuristicClass.py (See Localisation, Probe, and Target Classes). Each probing strategy initially probes the root of the tree. Instead of providing a probe movement function as above, the Probe class can be initialised with one of the four following strings:
- ```"tLeft"``` - Probe the "top left" node of the target set
- ```"tRight"``` - Probe the "top right" node of the target set
- ```"bLeft"``` - Probe the "bottom left" node of the target set
- ```"bRight"``` - Probe the "bottom right" node of the target set
Top and bottom refer to the lowest and highest levels in the target set and left and right refer to nodes on the left or right of the tree as per the ordering of the tree.

### Localisation, Probe, and Target Classes (Simplified Seager) - heuristicClass.py
The heuristicClass.py file contains several classes that manage the game for heuristic strategies such as the Simplified Seager strategy (See Probe).

#### Target
The Target class manages gameplay for the target player. The class can be initialised as follows:

```
target = Target(
  initialFunc,  #Redundant, give None
  moveFunc      #Function governing move generation for the target player (See Target Strategies)
)
```

A target move can be generated using the move function:

```
target.move(
  tree,   #NetworkX representation of the tree
  tDict,  #tDict representation of the tree
  lDict,  #lDict representation of the tree
)
```

#### Probe
The Probe class manages gameplay for the probing player. The class can be initialised as follows:

```
probe = Probe(
  moveFunc  #Function or string governing move generation for the probing player (See Probing Strategies)
)
```

A probe move can be generated using the move function:

```
probe.move(
  tree,   #NetworkX representation of the tree
  tDict,  #tDict representation of the tree
  lDict,  #lDict representation of the tree
  d       #Distance returned by the previous probe
)
```

If the probe movement function is given as a string, the move function will call the simpleSeager function:

```
probe.simpleSeager(
  tree,   #NetworkX representation of the tree
  tDict,  #tDict representation of the tree
  lDict,  #lDict representation of the tree
  d       #Distance returned by the previous probe
)
```

The  initial function is given but simply probes the root of the tree:

```
probe.initial()
```

#### Localisation
The Localisation class manages gameplay for both target and probing players as well as maintaining information throughout the game, such as the tree object, round number, winner, and capture time. The class can be initialised as follows:

```
game = Localisation(
  tree,     #NetworkX representation of the tree
  target,   #Target object (See Target)
  probe,    #Probe object (See Probe)
  tInitial  #Initial location for the target (**Optional**)
)
```

The game can be started by calling the play function:

```
game.play() #Returns the capture time (number of rounds) the game took
```

### Seager's Probing Strategy - seager.py
The Seager class functions similarly to the Localisation class but for a pre-defined strategy, that being Seager's strategy for rooted trees. As it is a large and complex class only the necessary components are detailed. The class can be initialised as follows:

```
game = Seager(
  tree,     #NetworkX representation of the tree
  moveFunc  #Function governing move generation for the target player (See Target Strategies)
)
```

The game can be started by calling the play function:

```
game.play() #Returns the node that the target was located at
```

The class also acts as a dictionary. This is useful for maintaining information during execution as well as retriving this information after the game is over. Commonly accessed information includes:

```
game["trace"]     #Verbose information about the execution of the game, which functions were called and which nodes or target sets were passed to these functions
game["probeList"] #A list of nodes probed by the probing player
game["t"]         #A list of nodes occupied by the target throughout the game
```

Before the play function has been called, a list of pre-defined target moves can be supplied using this dictionary functionality, e.g.

```
game[t] = [1, 2, 7]
game.play()
```

The class will generate any future moves using the provided target move generation function.

### Experiment - experiment.py
This script is responsible for running the experiment. Usage: ```python experiment.py probeStrategy``` where probe strategy can be one of the four strings given in Probe Strategies section or ```"Seager"``` for Seager's strategy. The script will iterate over each graph in the treeFiles folder and begin a game with each node of the graph as a starting point for the target, each node will be used as a starting point 25 times a total of 3 times, 25 times per target strategy. The average capture and run times of these 25 executions being reported as the capture time when starting at that node. The script will output a results file containing these averaged times for each node as ```"experimentResults.txt"``` prefixed with the given probe strategy string.

### Plotting Results - plotResults.py
This script will iterate over a given results file and average the capture times of each graph before producing a matplotlib (https://matplotlib.org/) graph of average capture time compared with number of nodes in the graph. Usage: ```python plotResults resultsFile``` where ```resultsFile``` is an output of running the experiment script.
