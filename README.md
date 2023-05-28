# Search Approaches to the Localisation Game
The localisation game is a graph-based pursuit-evasion game where a hidden target moves between the nodes of a graph and a probing player attempts to detemrine its location using distance queries. The primary focus of this project is to assess Suzanne Seager's strategy for rooted trees (https://www.sciencedirect.com/science/article/pii/S0304397512006469).

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

![alt text]([http://url/to/img.png](https://github.com/Horse-Lips/Localisation_in_Trees/blob/master/images/hideout.png?raw=true))
