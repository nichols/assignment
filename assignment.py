
from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import itertools
import networkx as nx


# Matrix containing assignees' numeric preferences for each target.
# Each assignee's preferences are scaled so that the sum is 1.
class ScaledPrefMatrix:
  def __init__(self, assignee_indices, target_indices, matrix):
    self.assignee_indices = assignee_indices
    self.target_indices = target_indices
    self.matrix = matrix

  # pref_list is a table with labels in the first row and first column.
  # pref_list[0][j] is the name of assignee j
  # pref_list[i][0] is the name of target i
  # pref_list[i][j+1] is the preference of assignee j for target i
  @classmethod
  def from_unscaled_list(cls, pref_list):
    # Python3 dicts remember insertion order.
    assignee_indices = {v: i for i,v in enumerate(pref_list[0])}
    target_indices = {v[0]: i for i,v in enumerate(pref_list[1:])}
    matrix = [row[1:] for row in pref_list[1:]]
    matrix = [list(i) for i in zip(*matrix)]  # transpose matrix

    # Scale each user's preference row.
    for row in matrix:
      row_sum = sum(row)
      for i in range(len(row)):
        row[i] /= row_sum
    return cls(assignee_indices, target_indices, matrix)

  def pref(self, assignee, target):
    i = self.assignee_indices[assignee]
    j = self.target_indices[target]
    return self.matrix[i][j]

  @property
  def assignees(self):
    return self.assignee_indices.keys()

  @property
  def targets(self):
    return self.target_indices.keys()

  # Make a bipartite graph with an edge connecting each assignee to each target
  # weighted according to the assignee's preference for that target.
  def create_graph(self):
    graph = nx.Graph()
    for assignee in self.assignees:
      graph.add_node(assignee)
    for target in self.targets:
      graph.add_node(target)
      for assignee in self.assignees:
        graph.add_edge(assignee, target, weight=self.pref(assignee, target))
    return graph

  def to_string(self, col_width=10):
    # header row
    s = " ".join((x.rjust(col_width) for x in itertools.chain([""], self.targets)))
    # add row for each assignee
    for assignee, i in self.assignee_indices.items():
      s += "\n" + " ".join((x.rjust(col_width)
                            for x in itertools.chain([assignee], ("{:.2f}".format(r).rjust(col_width)
                                                                  for r in self.matrix[i]))))
    return s

  def __str__(self):
    return self.to_string(max((len(target) for target in self.targets)))


# Maximum weight matching for a complete weighted bipartite graph.
def optimal_matching(graph, keys=None):
  if not keys:
    keys, _ = nx.bipartite.sets(graph)
  matching = nx.algorithms.matching.max_weight_matching(graph, maxcardinality=True)
  return ((u, v, graph.edges[u, v]['weight']) for u, v in matching)


def create_assignment(pref_list):
  pref_matrix = ScaledPrefMatrix.from_unscaled_list(pref_list)
  print("Preferences:")
  print(pref_matrix)

  assignment = optimal_matching(pref_matrix.create_graph(), keys=pref_list[0])
  total_weight = 0.0
  print("Optimal assignment:")
  for row in assignment:
    print("{}: {} (weight {:.2f})".format(*row))
    total_weight += row[2]
  print("Total weight: {:.2f}".format(total_weight))
  return assignment


def main():
  # Simple test case
  pref_list = [["Foo", "Bar", "Baz"], ["Apple", 0, 1, 1], ["Pear", 2, 0, 0], ["Banana", 1, 2, 2]]
  create_assignment(pref_list)


if __name__ == '__main__':
  main()
