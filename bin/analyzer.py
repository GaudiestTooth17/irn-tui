#!/usr/bin/python3
"""
A Python script that uses networkx an matplotlib to measure aspects of networks
"""
import matplotlib.pyplot as plt
import collections
import networkx as nx
import numpy as np
import sys
from typing import Dict, List, Set


def read_adj_list(fileName) -> np.ndarray:
    """
    This reads in the data from half a symmetric matrix and mirrors it.
    If the whole matrix is present in the file, that won't cause problems.
    This cannot read unsymmetric matrices.
    """
    with open(fileName, 'r') as f:
        line = f.readline()
        shape = (int(line[:-1]), int(line[:-1]))
        matrix = np.zeros(shape, dtype=np.uint8)

        line = f.readline()[:-1]
        i = 1
        while len(line) > 0:
            coord = line.split(' ')
            matrix[int(coord[0]), int(coord[1])] = 1
            matrix[int(coord[1]), int(coord[0])] = 1
            line = f.readline()[:-1]
            i += 1
    return matrix


def show_deg_dist_from_matrix(matrix: np.ndarray, title, *, color='b', display=False, save=False):
    """
    This shows a degree distribution from a matrix.
    :param matrix: The matrix.
    :param title: The title.
    :param color: The color of the degree distribution.
    :param display: Whether or not to display it.
    :param save: Whether or not to save it.
    :return: None
    """
    graph = nx.from_numpy_matrix(matrix)
    degree_sequence = sorted([d for n, d in graph.degree()], reverse=True)
    degreeCount = collections.Counter(degree_sequence)
    deg, cnt = zip(*degreeCount.items())

    fig, ax = plt.subplots()
    plt.bar(deg, cnt, width=0.80, color=color)

    plt.title(title)
    plt.ylabel("Count")
    plt.xlabel("Degree")
    ax.set_xticks([d + 0.4 for d in deg])
    ax.set_xticklabels(deg)

    if display:
        plt.show()
        # print(title + ' displayed')
    if save:
        plt.savefig(title)
        with open(title + '.csv', 'w') as file:
            for i in range(len(cnt)):
                file.write(f'{deg[i]},{cnt[i]}\n')
        # print(title + ' saved')
    plt.clf()


def make_node_to_degree(adj_mat) -> List[int]:
    node_to_degree = [0 for _ in range(adj_mat.shape[0])]
    for i in range(adj_mat.shape[0]):
        for j in range(adj_mat.shape[1]):
            if adj_mat[i][j] > 0:
                node_to_degree[i] += 1
    return node_to_degree


def show_clustering_coefficent_dist(node_to_coefficient: Dict[int, float], node_to_degree: Dict[int, int]) -> None:
    degree_to_avg_coefficient = {}
    for node, coefficient in node_to_coefficient.items():
        if node_to_degree[node] not in degree_to_avg_coefficient:
            degree_to_avg_coefficient[node_to_degree[node]] = []
        degree_to_avg_coefficient[node_to_degree[node]].append(coefficient)
    for degree, coefficients in degree_to_avg_coefficient.items():
        degree_to_avg_coefficient[degree] = sum(coefficients)/len(coefficients)

    plot_data = list(degree_to_avg_coefficient.items())
    plot_data.sort(key=lambda e: e[0])
    plt.plot(tuple(e[0] for e in plot_data), tuple(e[1] for e in plot_data))
    plt.xlabel('degree')
    plt.ylabel('average clustering coefficient')

    avg_clustering_coefficient = sum((e[1] for e in plot_data)) / len(plot_data)
    print(f'Average clustering coefficient for all nodes: {avg_clustering_coefficient}')

    plt.show()


def calc_edge_density(adj_mat) -> float:
    num_edges = 0
    for i in range(adj_mat.shape[0]):
        for j in range(i+1, adj_mat.shape[1]):
            if adj_mat[i][j] > 0:
                num_edges += 1
    density = num_edges / (adj_mat.shape[0]*(adj_mat.shape[0]-1)/2)
    return density


def get_components(graph) -> List[Set]:
    """
    returns a list of the components in graph
    :param graph: a networkx graph
    """
    return list(nx.connected_components(graph))


def analyze_graph(adj_matrix, name) -> None:
    """
    shows degree distribution, degree assortativity coefficient, clustering coefficient,
    edge density
    """
    G = nx.Graph(adj_matrix)
    edge_density = calc_edge_density(adj_mat)
    dac = nx.degree_assortativity_coefficient(G)
    clustering_coefficients = nx.clustering(G)
    node_to_degree = make_node_to_degree(adj_mat)
    components = get_components(G)

    print(f'Edge density: {edge_density}')
    print(f'Degree assortativity coefficient: {dac}')
    show_clustering_coefficent_dist(clustering_coefficients, node_to_degree)
    print(f'size of components: {[len(comp) for comp in components]}')
    show_deg_dist_from_matrix(adj_mat, name, display=True)


if __name__ == '__main__':
    adj_mat = read_adj_list(sys.argv[1])
    analyze_graph(adj_mat, sys.argv[1])
