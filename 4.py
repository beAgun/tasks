import sys
from math import sqrt
from random import randint
import networkx as nx
import matplotlib.pyplot as plt


#input = sys.stdin.readline
try:
    print('Input n from 2 to 20:')
    n = int(input())
    assert 2 <= n <= 20
    print('Input number of option, 1 - min or 2 - max:')
    option = int(input())
    assert option in (1, 2)
except (ValueError, AssertionError):
    print('Incorrect input')
    sys.exit()

points = []
max_y, min_x = 0, 101
for i in range(n):
    x, y = randint(1, 100), randint(1, 100)
    max_y = max(max_y, y)
    min_x = min(min_x, x)
    points += [(x, y)]

plt.figure(figsize=(8, 8))

graph = nx.Graph()
nodes = {i: points[i] for i in range(n)}
graph.add_nodes_from(nodes)

arr = [[0 for j in range(n)] for i in range(n)]
for i in range(n):
    for j in range(n):
       arr[i][j] = arr[j][i] = \
           sqrt((points[i][0] - points[j][0])**2 + (points[i][1] - points[j][1])**2)

for i in range(n):
    for j in range(n):
        if i != j:
            graph.add_edge(i, j, weight=arr[i][j])

dp = {}
ans = -1
start_vertex = 0
subset = 2**start_vertex
for vertex in range(1, n):
    dp[(subset | (1 << vertex), vertex)] = [arr[start_vertex][vertex], [start_vertex, vertex]]


for subset in range(1, 2**n):
    if subset & (1 << start_vertex) == 0:
        continue

    for now in range(1, n):
        if subset & (1 << now) == 0:
            continue
        subset_without_now = subset & ~(1 << now)

        if option == 1:
            dp.setdefault((subset, now), [float('+inf'), []])
        else:
            dp.setdefault((subset, now), [float('-inf'), []])

        for prev in range(1, n):
            if subset_without_now & (1 << prev) == 0:
                continue

            if (subset_without_now, prev) in dp:
                if option == 1:
                    if dp[(subset_without_now, prev)][0] + arr[prev][now] < dp[(subset, now)][0]:
                        dp[(subset, now)][0] = dp[(subset_without_now, prev)][0] + arr[prev][now]
                        dp[(subset, now)][1] = dp[(subset_without_now, prev)][1] + [now]
                else:
                    if dp[(subset_without_now, prev)][0] + arr[prev][now] > dp[(subset, now)][0]:
                        dp[(subset, now)][0] = dp[(subset_without_now, prev)][0] + arr[prev][now]
                        dp[(subset, now)][1] = dp[(subset_without_now, prev)][1] + [now]

        if subset == 2**n - 1:
            if ans == -1:
                ans = dp[(subset, now)][0] + arr[0][now], dp[(subset, now)][1] + [0]
            else:
                if option == 1:
                    if dp[(subset, now)][0] + arr[0][now] < ans[0]:
                        ans = dp[(subset, now)][0] + arr[0][now], dp[(subset, now)][1] + [0]
                else:
                    if dp[(subset, now)][0] + arr[0][now] > ans[0]:
                        ans = dp[(subset, now)][0] + arr[0][now], dp[(subset, now)][1] + [0]

if ans != -1:
    edgelist = []
    length = round(ans[0], 2)
    good_vertexes = ans[1]
    for i in range(1, len(good_vertexes)):
        edgelist += [(good_vertexes[i - 1], good_vertexes[i])]

    plt.figure()
    nx.draw(graph, nodes, width=1, edge_color="#C0C0C0", with_labels=True,
            node_color='#4ca1ed')
    nx.draw(graph, nodes, width=2, edge_color="red", edgelist=edgelist,
            node_color='#4ca1ed')

    plt.title(f'Length is {str(length)}', fontsize=20)
    plt.savefig('res4', bbox_inches='tight')