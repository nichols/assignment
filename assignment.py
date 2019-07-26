
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
  # pref_list[0][j+1] is the name of assignee j
  # pref_list[i+1][0] is the name of target i
  # pref_list[i+1][j+1] is the preference of assignee j for target i
  @classmethod
  def from_unscaled_list(cls, pref_list):
    # Python3 dicts remember insertion order.
    assignee_indices = dict(zip(pref_list[0][1:], range(len(pref_list[0]))))
    target_indices = dict(zip((row[0] for row in pref_list[1:]), range(len(pref_list))))
    matrix = [[cell or 0 for cell in row[1:]] for row in pref_list[1:]]
    matrix = [list(i) for i in zip(*matrix)]  # transpose matrix

    # Scale each user's preference row.
    for i in range(len(matrix)):
      row_sum = sum(matrix[i])
      if row_sum == 0:
        matrix[i] = [1 / len(matrix[i]) for _ in matrix[i]]
      else:
        matrix[i] = [x / row_sum for x in matrix[i]]
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

  def to_string(self, precision=2):
    first_col_width = max((len(assignee) for assignee in self.assignees))
    col_width = max([precision + 2] + [len(target) for target in self.targets])
    # header row
    s = "".rjust(first_col_width) + " " + " ".join((x.rjust(col_width) for x in self.targets))
    # add row for each assignee
    for assignee, i in self.assignee_indices.items():
      s += ("\n{val:>{width}} ".format(val=assignee, width=first_col_width)
            + " ".join(("{val:>{width}.2f}".format(val=x, width=col_width) for x in self.matrix[i])))
    return s

  def __str__(self):
    return self.to_string()


# Assignment is a max-weight matching in this complete weighted bipartite graph.
def assignment_from_graph(graph, keys=None):
  if not keys:
    keys, _ = nx.bipartite.sets(graph)
  matching = nx.algorithms.matching.max_weight_matching(graph, maxcardinality=True)
  # matching is a set of edges (u,v). nx doesn't know the graph is bipartite, so
  # there's no consistency in whether the assignee is u or v.
  assignment = {}
  for k in keys:
    # find an edge in the matching containing k
    edge = next(iter(filter(lambda e: k in e, matching)))
    v = edge[1] if edge[0] == k else edge[0]
    assignment[k] = v
    matching.remove(edge)
  return assignment


def assign(pref_list):
  pref_matrix = ScaledPrefMatrix.from_unscaled_list(pref_list)
  assignees = pref_matrix.assignees
  targets = pref_matrix.targets
  print("Preferences:")
  print(pref_matrix)

  assignment = assignment_from_graph(pref_matrix.create_graph(), keys=assignees)
  total_weight = 0.0
  assignee_col_width = max((len(assignee) for assignee in assignees))
  print("\nOptimal assignment:")
  for assignee in assignees:
    target = assignment[assignee]
    pref = pref_matrix.pref(assignee, target)
    print("{}: {} (weight {:.2f})".format(assignee.rjust(assignee_col_width), target, pref))
    total_weight += pref

  print("\nTotal weight: {:.2f}".format(total_weight))
  unassigned_targets = set(targets) - set(assignment.values())
  if unassigned_targets:
    print("\nUnassigned targets: " + ", ".join(unassigned_targets))


def _test_data():
  return [["", "Foo", "Bar", "Baz"], ["Apple", 0, 1, 1], ["Pear", 2, 0, 0], ["Banana", 1, 2, 2]]


def main():
  pref_list = _test_data()
  assign(pref_list)


if __name__ == '__main__':
  main()
