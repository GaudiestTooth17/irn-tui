#!/usr/bin/python3
import numpy as np
from typing import Iterable, Tuple, Callable
from enum import IntEnum
from collections import namedtuple
from utility import read_adj_list, read_disease
from numba import njit, prange


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


def visualize_sim(matrix_file_name: str, disease_file_name: str, num_steps: int,
                  visualization_name: str):
    matrix = read_adj_list(matrix_file_name)
    disease, init_func = read_disease(disease_file_name)
    initial_seir = init_func(matrix.shape[0])
    seirs = simulate(matrix, initial_seir, num_steps, disease)
    save_visualization(seirs, visualization_name)


@njit
def run_sim_batch(matrix_file_name: str, disease_file_name: str, num_steps: int,
                  num_sims: int) -> float:
    matrix = read_adj_list(matrix_file_name)
    disease, init_func = read_disease(disease_file_name)
    initial_seir = init_func(matrix.shape[0])
    num_susceptible = [find_num_susceptible_nodes(simulate(matrix, initial_seir, num_steps, disease))
                       for _ in prange(num_sims)]
    return sum(num_susceptible)/len(num_susceptible)


@njit(parallel=True)
def simulate(matrix: np.ndarray, starting_seir: np.ndarray, num_steps: int,
             disease: Disease) -> np.ndarray:
    """
    :param matrix: adjacency matrix of graph
    :param seir: starting numbers of s, e, i, r
    :param num_steps: number of steps to run for
    :return: An array containing the state history of each of the nodes.
             The last index iterates over the steps.
    """
    seirs = np.zeros((starting_seir.shape[0], starting_seir.shape[1], num_steps),
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
        seirs[:, :, step] = seir

    return seirs


@njit(parallel=True)
def find_num_susceptible_nodes(seirs: np.ndarray) -> int:
    return np.sum(seirs[:, State.S.value, -1] > 0)


def save_visualization(seirs: np.ndarray, name: str):
    with open(name, 'w') as out_file:
        for step in range(seirs.shape[2]):
            susceptible_nodes = np.where(seirs[:, State.S.value, step] > 0)[0]
            exposed_nodes = np.where(seirs[:, State.E.value, step] > 0)[0]
            infectious_nodes = np.where(seirs[:, State.I.value, step] > 0)[0]
            removed_nodes = np.where(seirs[:, State.R.value, step] > 0)[0]
            out_file.writelines(('\n'.join(f'{node} {State.S.value}' for node in susceptible_nodes),
                                 '\n'.join(f'{node} {State.E.value}' for node in exposed_nodes),
                                 '\n'.join(f'{node} {State.I.value}' for node in infectious_nodes),
                                 '\n'.join(f'{node} {State.R.value}' for node in removed_nodes),
                                 '\n'))
