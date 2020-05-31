# Pancake Flipping

This repository contains a pancake flipping game I made during the weeks of the COVID-19 stay-at-home orders. It's a simple computer game but has some fun graph theory history and theoretical foundations.

#### The pancake flipping problem

In a [1975 issue](https://www.jstor.org/stable/2318260) of _The American Mathematical Monthly_, an American Geometer named Jacob Goodman posed an "Elementary Problem" under the pseudonym of Harry Dweighter (read his name aloud...): "The chef in our place is sloppy, and when he prepares a stack of pancakes they come out all different sizes. Therefore, when I deliver them to a customer, on the way to the table I rearrange them (so that the smallest winds up on top, and so on, down to the largest on the bottom) by grabbing several from the top and flipping them over, repeating this (varying the number I flip) as many times as necessary. If there are _n_ pancakes, what is the maximum number of flips (as a function of _n_) that I will ever have to use to rearrange them?"

This question is a variation on the general sorting problem, where the only permissible operation is _prefix reversal_, that is, if we consider the order of the stack a sequence (1, 2, ..., n) the reversal of the elements of some prefix of the sequence. Sequence [A058986](https://oeis.org/A058986) describes the maximum number of flips required for stacks of pancakes up to 19.

Of an interesting historical note, the only academic mathematics paper published by William H. Gates (aka Bill Gates...yes, him.) concerns pancake flipping. In a [1979 issue](https://www.sciencedirect.com/science/article/pii/0012365X79900682) of _Discrete Mathematics_, he published a paper in conjunction with Christos H. Papadimitriou, which placed an upper bound of (5 * _n_ + 5) / 3, which was subsequently improved to (18 / 11) * _n_ by a separate team of researchers. The current estimate is between (15 / 14) * _n_ and (18 / 11) * _n_, but the exact value is not known.

Another articulation of the pancake flipping problem involves burnt pancakes, which adds a requirement to the original problem by stipulating that each pancake must end up burnt side down. Sequence [A078941](https://oeis.org/A078941) describes the maximum number of flips required for stacks of pancakes up to 12.

#### Graph theory

In the field of [graph theory](https://en.wikipedia.org/wiki/Graph_theory), a graph is a mathematical structure used to model pairwise relations between objects. A graph consists of _vertices_ (or _nodes_), which are connected by _edges_. A _path_ is a sequence of edges connecting distinct vertices. The _distance_ between two vertices is the number of edges in the shortest path between them. The _diameter_ of a graph is the longest path between any two vertices.

A pancake graph, _P(n)_, is a particular type of graph with n! vertices labeled with the permutations of (1, 2, ..., n) and whose edges connect vertices that are transitive by prefix reversal. Thus a 3 pancake graph would have 3 * 2 * 1 = 6 vertices labeled (1, 2, 3), (2, 1, 3), (1, 3, 2), (2, 1, 3), (2, 3, 1), (3, 1, 2), and (3, 2, 1); vertex (1, 2, 3), for example, would have edges with vertices (2, 1, 3) and (3, 2, 1).

In this arrangement, each vertex represents a particular ordering of a stack of pancakes, with the first element in the list at the top of the stack. A properly ordered stack would be the identity permutation, (1, 2, ..., n). A path from vertex A to B is a sequence of spatula flips to get from one arrangement of pancakes to another. The pancake flipping problem, which counts the most flips necessary to order a stack of _n_ pancakes, is the same as calculating the diameter of the pancake graph, _P(n)_.

In the burnt pancake variation, the vertices a signed (+ or -) and with each prefix reversal, the sign of the flipped pancakes changes. This graph has n! * 2^n vertices.

#### How to play

The latest version of the game (on the master branch) is pancake flipping with different sized stacks of normal or burned pancakes.

1. Run the file, "pancake_flipping.py"
2. Click on any pancake to flip it and the pancakes above it
3. In as few moves as possible, try to get the stack in order from smallest to largest (smallest at the top) with burnt sides down (when playing with burnt pancakes)
4. When you win, a fresh stack appears

Notes:

* Click the "Reset" button to return the stack to its original order and set the moves counter to 0
* Click the "Burned?" button to toggle between normal and burned pancake versions of the game
* Click the "More food" and "Less food" buttons to change the number of pancakes