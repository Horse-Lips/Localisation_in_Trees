# Search Approaches to the Localisation Game
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
### Custom Tree Representation
Within each localisation class there exist functions that represent the levels and orderings of a tree as dictionaries, referred to as the tDict (treeDict) and lDict (levelsDict). These are necessary as NetworkX does not provide explicit tree representations and views them as general graphs and because the probing strategies require the tree to be ordered in a certain way with access to the individual levels of the tree.
- nodeInfo object
  - Each node has a nodeInfo object which maintains information about:
    - level - The level of the tree the node is located on
    - parent - The node's parent
    - children - An ordered list of the node's children
- tDict - A Python dictionary with:
  - A key for each node label, e.g. key 1 for node 1
  - An entry of the nodeInfo object for that node
- lDict - A python dictionary with:
  - A key for each level in the tree, e.g. level 0 containing just the root of the tree
  - An entry of an ordered list of nodes on that level of the tree

### Graph Generation - graphGenerator.py
Usage: python graphGenerator.py n
- n: The number of nodes in the tree

A number of randomly generated trees can be found in the treeFiles folder with node counts ranging from 3 to 150 nodes. This script generates hideout-free trees. A hideout is a subgraph that enables the target to theoretically evade capture indefinitely, Seager's example hideout is shown here:

<img src="images/hideout.png">

Graphs are limited to 150 nodes as it is a difficult task to generate large hideout-free trees. Graphs are generated using NetworkX's random_tree function (https://networkx.org/documentation/stable/reference/generated/networkx.generators.trees.random_tree.html).

### Target Strategies - heuristicMovement.py
As the game is usually analysed theoretically an optimal target with perfect knowledge is assumed. As this is not practical from an implementation perspective, several suboptimal target strategies have been implemented in the heuristicMovement.py file.
- Each target strategy is given as arguments:
  - tree - The NetworkX tree object
  - tDict - The tDict representation of the tree
  - lDict - the lDict representation of the tree
  - node - The node currently occupied by the target
- tRandom
  - The target moves to a completely random node in the neighbourhood of the current node
- tUpTree
  - The target moves up or down the levels of the tree with some pre-defined probability with a higher probability of moving **up** the tree
- tDownTree
  - The target moves up or down the levels of the tree with some pre-defined probability with a higher probability of moving **down** the tree
- tUpDown
  - A combination of the above two strategies with a chance of remaining at the same node for consecutive rounds
- tProbabilistic
  - The target moves to a node in the neighbourhood N where each node m in the neighbourhood is assigned the probability $\frac{deg(m)}{\sum_{n \in N}deg(n)}$
Each of these can be given to either a Target object (See Localisation, Probe, and Target Classes) or a Seager object (See Seager's Probing Strategy).

### Probing Strategies - heuristicMovement.py
The heuristicMovement.py file also contains some simple functions for probe placement. Each probing strategy initially probes the root of the tree.
- Each probing strategy is given as arguments:
  - tree - The NetworkX tree object
  - tDict - The tDict representation of the tree
  - lDict - the lDict representation of the tree
  - probeList - A list of all previous nodes probed
  - d - The distance between the previous probe and the target
- pRandom
  - Probes are placed completely randomly on the tree
- pRandomLeaf
  - Probes are placed on completely random leaf nodes in the tree
Each of these can be given to a Probe object (See Localisation, Probe, and Target Classes)

### Probing Strategies - heuristicClass.py
The Simplified Seager strategy is implemented as a part of the Probe class found in heuristicClass.py (See Localisation, Probe, and Target Classes). Each probing strategy initially probes the root of the tree. Instead of providing a probe movement function as above, the Probe class can be initialised with one of the four following strings:
- tLeft - Probe the "top left" node of the target set
- tRight - Probe the "top right" node of the target set
- bLeft - Probe the "bottom left" node of the target set
- bRight - Probe the "bottom right" node of the target set

#### Target Set
The target set is the possible locations that the target may occupy after a given probe. This is determined by comparing the distance returned by a prove with each possible node the target may occupy in order to narrow down the target's location. Each probing strategy initially probes the root of the tree, and therefore the target could occupy any node on level d of the tree where d is the distance returned by the initial probe. After the target moves it could be on any node on level d, the parents of these nodes or the children of these nodes. After this initial probe the target set is updated based on future probes. Seager's strategy formalises the target set as the set R and separates it into three sets, one for each level the target may occupy at a certain point

### Localisation, Probe, and Target Classes (Simplified Seager) - heuristicClass.py
The heuristicClass.py file contains several classes that manage the game for heuristic strategies such as the Simplified Seager strategy (See Probe).

#### Target
The Target class manages gameplay for the target player.
- Initialisation
  - moveFunc - Function governing move generation for the target player (See Target Strategies)
- Functions
  - initial
    - Chooses an initial node for the target (Currently random but can be predefined)
    - Args:
      - tree - NetworkX representation of the tree
  - move
    - Uses the given move generation function to generate a move which is returned
    - Args:
      - tree - NetworkX representation of the tree
      - tDict - The tDict representation of the tree
      - lDict - the lDict representation of the tree 

#### Probe
The Probe class manages gameplay for the probing player.
- Initialisation
  - moveFunc - Function governing move generation for the probing player (See Probing Strategies)

#### Localisation


### Seager's Probing Strategy - seager.py
