from typing import Any, Optional, List, Tuple
import subprocess as sp
import matplotlib.pyplot as plt
import collections
import numpy as np
import networkx as nx
from typing import Dict
from sim import Disease, SEIRInitFunc


def safe_cast(obj: Any, T) -> Optional[int]:
    """
    :param T: the type to cast to
    :return: something converted to an integer if possible, None if impossible
    """
    try:
        return T(obj)
    except ValueError:
        return None


def int_input(msg='') -> int:
    """
    Like input, but guaranteed to return an int.
    If the user doesn't input an int, it repeats the prompt.
    """
    x = safe_cast(input(msg), int)
    if x is None:
        x = int_input(msg)
    return x


def float_input(msg='') -> float:
    """
    Like int_input, but for floating point values
    """
    x = safe_cast(input(msg), float)
    while x is None:
        x = safe_cast(input(msg), float)
    return x


def bool_input(msg='') -> bool:
    """
    Similar to input, but returns a bool.
    :return: True if the user inputs 'y' or 'Y', False otherwise.
    """
    x = input(f'{msg} (y/n) ')
    return x.lower() == 'y'


def int_list_input(msg='') -> List[int]:
    xs = input(msg)
    ints = [safe_cast(x, int) for x in xs.split(' ')]
    if any((x is None for x in ints)):
        int_list_input(msg)
    return ints


def run_cmd(cmd, *args, silent=False) -> str:
    """
    Runs a terminal command.
    :param cmd: the name of the command.
    :param args: the arguments to pass it (should be strings).
    :param silent: Whether or not to fail silently
    :return: The stdout and stderr output that the command generated if it ran successfully.
    Otherwise, it returns '' after printing an error message.
    """
    try:
        raw_output = sp.check_output([cmd] + list(args), stderr=sp.STDOUT)
        return raw_output.decode('utf-8')
    except sp.CalledProcessError as e:
        if not silent:
            print('\nCould not execute command\n')
            print(e)
        return ''


class DirContents:
    def __init__(self, dir_name: str, contents: List[str]) -> None:
        self.dir_name = dir_name
        self.contents = contents

    def __getitem__(self, item):
        if item in self.contents:
            return f'{self.dir_name}/{item}'
        raise Exception(f'{item} NOT FOUND')

    def __len__(self):
        return len(self.contents)


def ls_dir(dir: str) -> DirContents:
    files = [fn for fn in run_cmd('ls', dir).split('\n') if len(fn) > 1]
    return DirContents(dir, files)


def read_adj_list(file_name) -> np.ndarray:
    """
    This reads in the data from half a symmetric matrix and mirrors it.
    If the whole matrix is present in the file, that won't cause problems.
    This cannot read unsymmetric matrices.
    """
    with open(file_name, 'r') as f:
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
    degree_count = collections.Counter(degree_sequence)
    deg, cnt = zip(*degree_count.items())

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


def read_disease(file_name: str) -> Tuple[Disease, SEIRInitFunc]:
    with open(file_name, 'r') as f:
        fields = f.readline().split(' ')
    disease = Disease(int(fields[0]), int(fields[1]), float(fields[2]))

    num_to_infect = int(fields[4])

    def init_func(num_nodes: int) -> np.ndarray:
        nonlocal num_to_infect
        # the four is for the four states in SEIR
        seir = np.zeros((num_nodes, 4), dtype=np.int32)
        seir[np.random.randint(seir.shape[0], size=num_to_infect)] = 1
        return seir

    return disease, init_func
