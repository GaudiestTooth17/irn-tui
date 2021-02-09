#!/usr/bin/python3
"""
A Python script that uses networkx an matplotlib to measure aspects of networks
"""
import networkx as nx
from typing import List, Set


def calc_edge_density(graph: nx.Graph) -> float:
    adj_mat = nx.to_numpy_matrix(graph)
    num_edges = 0
    for i in range(adj_mat.shape[0]):
        for j in range(i+1, adj_mat.shape[1]):
            if adj_mat[i][j] > 0:
                num_edges += 1
    density = num_edges / (adj_mat.shape[0]*(adj_mat.shape[0]-1)/2)
    return density


def get_component_sizes(graph) -> List[Set]:
    """
    returns a list of the components in graph
    :param graph: a networkx graph
    """
    return [len(cc) for cc in nx.connected_components(graph)]


def find_degree_assortativity_coeffecient(graph):
    return nx.degree_assortativity_coefficient(graph)


def find_clustering_coefficients(graph):
    return nx.clustering(graph)
