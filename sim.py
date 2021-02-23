#!/usr/bin/python3
import numpy as np
from typing import Iterable, Tuple, Callable
from enum import IntEnum
from collections import namedtuple
from numba import njit, prange
import time


class State(IntEnum):
    S = 0
    E = 1
    I = 2
    R = 3


Disease = namedtuple('Disease', 'days_exposed days_infectious transmission_prob')

# Mutates an empty ndarray to create a starting SEIR configuration for a simulation
SEIRInitFunc = Callable[[np.ndarray], None]


def seir_list_to_ndarray(node_states: Iterable[Tuple[int, State]]) -> np.ndarray:
    nodes = np.fromiter((x[0] for x in node_states), dtype=np.int)
    states = np.fromiter((x[1].value for x in node_states), dtype=np.int)
    seir = np.zeros((len(node_states), 4))
    seir[nodes, states] = 1
    return seir


def visualize_sim(matrix_file_name: str, disease_file_name: str, num_steps: int) -> str:
    time_start = time.time()
    matrix = read_adj_list(matrix_file_name)
    disease, init_func = read_disease(disease_file_name)
    initial_seir = init_func(matrix.shape[0])
    seirs = _simulate(matrix, initial_seir, num_steps, disease)
    vis_str = make_visualization_str(seirs)
    summary = '{:.4} ({:.3} s)'.format(_find_num_susceptible_nodes(seirs)/matrix.shape[0],
                                       time.time()-time_start)
    return vis_str, summary


def run_sim_batch(matrix_file_name: str, disease_file_name: str, num_steps: int,
                  num_sims: int) -> float:
    matrix = read_adj_list(matrix_file_name)
    disease, init_func = read_disease(disease_file_name)
    initial_seir = init_func(matrix.shape[0])
    num_susceptible = (_find_num_susceptible_nodes(_simulate(matrix, initial_seir, num_steps, disease))
                       for _ in prange(num_sims))
    proportion_susceptible = (x/matrix.shape[0] for x in num_susceptible)
    return sum(proportion_susceptible)/num_sims


def _simulate(matrix: np.ndarray, starting_seir: np.ndarray, num_steps: int,
              disease: Disease) -> np.ndarray:
    """
    :param matrix: adjacency matrix of graph
    :param seir: starting numbers of s, e, i, r
    :param num_steps: number of steps to run for
    :return: An array containing the state history of each of the nodes.
             The last index iterates over the steps.
    """
    seirs = np.zeros((num_steps, starting_seir.shape[0], starting_seir.shape[1]),
                     dtype=starting_seir.dtype)
    seir = np.copy(starting_seir)
    for step in range(num_steps):
        # Probabilistic vales to use during the simulation
        probs = np.random.rand(len(matrix))
        # Infectious to Recoved
        to_r_filter = seir[:, 2] > disease.days_infectious
        seir[to_r_filter, 3] = -1
        seir[to_r_filter, 2] = 0
        # Exposed to Infectious
        to_i_filter = seir[:, 1] > disease.days_exposed
        seir[to_i_filter, 2] = -1
        seir[to_i_filter, 1] = 0
        # Susceptible to Exposed
        i_filter = seir[:, 2] > 0
        to_e_probs = 1 - (np.prod((1 - (matrix * disease.transmission_prob))[:, i_filter], axis=1))
        to_e_filter = (seir[:, 0] > 0) & (probs < to_e_probs)
        seir[to_e_filter, 1] = -1
        seir[to_e_filter, 0] = 0
        # Tracking days and seirs
        seir[(seir > 0)] += 1
        seir[(seir < 0)] = 1
        seirs[step, :, :] = seir

    return seirs


@njit(parallel=True)
def _find_num_susceptible_nodes(seirs: np.ndarray) -> int:
    return np.sum(seirs[:, State.S.value, -1] > 0)


def make_visualization_str(seirs: np.ndarray) -> str:
    vis_str = ''
    for step in range(seirs.shape[0]):
        susceptible_nodes = np.where(seirs[step, :, State.S.value] > 0)[0]
        exposed_nodes = np.where(seirs[step, :, State.E.value] > 0)[0]
        infectious_nodes = np.where(seirs[step, :, State.I.value] > 0)[0]
        removed_nodes = np.where(seirs[step, :, State.R.value] > 0)[0]

        s_lines = '\n'.join(f'{node} {State.S.value}' for node in susceptible_nodes)
        e_lines = '\n'.join(f'{node} {State.E.value}' for node in exposed_nodes)
        i_lines = '\n'.join(f'{node} {State.I.value}' for node in infectious_nodes)
        r_lines = '\n'.join(f'{node} {State.R.value}' for node in removed_nodes)
        if len(s_lines) > 0:
            vis_str += s_lines + '\n'
        if len(e_lines) > 0:
            vis_str += e_lines + '\n'
        if len(i_lines) > 0:
            vis_str += i_lines + '\n'
        if len(r_lines) > 0:
            vis_str += r_lines + '\n'
        # This extra newline is to separate the steps
        vis_str += '\n'
    # append 'end\n' because that's just what the visualizer program wants
    return vis_str + 'end\n'


def read_disease(file_name: str) -> Tuple[Disease, SEIRInitFunc]:
    with open(file_name, 'r') as f:
        fields = f.readline().split(' ')
    disease = Disease(int(fields[0]), int(fields[1]), float(fields[2]))
    num_to_infect = int(fields[3])

    def init_func(num_nodes: int) -> np.ndarray:
        nonlocal num_to_infect
        # the four is for the four states in SEIR
        seir = np.zeros((num_nodes, 4), dtype=np.int32)
        to_infect = np.random.randint(seir.shape[0], size=num_to_infect)
        susceptible_nodes = np.array([node for node in range(num_nodes)
                                      if node not in to_infect])
        seir[to_infect, State.I.value] = 1
        seir[susceptible_nodes, State.S.value] = 1
        return seir

    return disease, init_func


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
        while len(line) > 0:
            coord = line.split(' ')
            matrix[int(coord[0]), int(coord[1])] = 1
            matrix[int(coord[1]), int(coord[0])] = 1
            line = f.readline()[:-1]
    return matrix
