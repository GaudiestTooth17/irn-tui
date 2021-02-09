#!/usr/bin/python3
"""
This is a ui script for the infection resistant network project. The goal is to bring
all the tools together into one cohesive package to make experimenation easier.
"""
import time
from typing import Dict, Any, Tuple
from utility import run_cmd, int_input, bool_input, float_input, int_list_input, read_adj_list
from inspect import getmembers, isfunction
import analysis as an
import constants
import networkx as nx


def main():
    run_cmd('mkdir', constants.TMP_DIR, silent=True)
    while True:
        next_function = main_menu()
        next_function()


def main_menu():
    """
    :return: a function that does the next thing the user wants to do
    """
    selection = -1
    # a collection of choices with an index, plain English name, and a function to call
    choices = list(enumerate((('quit', exit),
                             ('analyze graph', analyze_graph),
                             ('run simulation batch', run_simulation_batch),
                             ('visualize simulation', visualize_sim),
                             ('load visualization', load_visualization),
                             ('create a new disease', create_new_disease))))
    valid_numbers = list(map(lambda c: c[0], choices))

    while selection not in valid_numbers:
        print('Select an option:')
        for choice in choices:
            print(f'{choice[0]} {choice[1][0]}')
        selection = int_input()

    # return the function to call
    return dict(choices)[selection][1]


def analyze_graph():
    # TODO: add the go program for analyzing graphs
    graph_name = select_file_from_dir(constants.GRAPH_DIR, 'Select a graph to analyze:')
    choices = dict(enumerate(getmembers(an, isfunction)))

    selections = [-1]
    while not all((s in choices.keys() for s in selections)):
        print('Select the analyses to run:')
        print_func_choices(choices)
        selections = int_list_input('? ')

    analyses = (choices[sel][1] for sel in selections)
    graph = nx.Graph(read_adj_list(graph_name))
    for analysis in analyses:
        print(analysis(graph))


def run_simulation_batch():
    """
    Runs a group of simulations and displays a summary of the results
    """
    graph_name = select_file_from_dir(constants.GRAPH_DIR, 'Select a graph to use:')
    disease_name = select_file_from_dir(constants.DISEASE_DIR, 'Select a disease to use:')
    num_simulations = int_input('How many simulations? ')
    sim_length = int_input('How many steps for each simulation? ')
    output = run_cmd(constants.SIM_BIN, disease_name, graph_name,
                     str(num_simulations), str(sim_length))
    print()
    print(output)


def visualize_sim():
    """
    Runs a simulation and then opens the visualization program to show an animation
    """
    graph_name = select_file_from_dir(constants.GRAPH_DIR, 'Select a graph to use:')
    disease_name = select_file_from_dir(constants.DISEASE_DIR, 'Select a disease to use:')
    save_vis = bool_input('Would you like to save the visualization?')
    if save_vis:
        vis_name = input('Enter a name: ')
        file_name = f'{constants.VIS_DIR}/{vis_name}.txt'
    else:
        file_name = f'{constants.TMP_DIR}vis_{"".join(time.ctime().split(" "))}.txt'

    output = run_cmd(constants.SIM_BIN, disease_name, graph_name)
    print(output.split('\n')[-1])
    with open(file_name, 'w') as vis_file:
        with open(graph_name, 'r') as graph_file:
            graph_text = graph_file.readlines()
            vis_file.writelines(graph_text + ([] if graph_text[-1] == '\n' else ['\n']))
            vis_file.write(output)
    run_cmd(constants.VIS_BIN, file_name)


def load_visualization():
    """
    load a previously saved visualization and display it
    """
    visualization_name = select_file_from_dir(constants.VIS_DIR, 'Select a visualization:')
    run_cmd(constants.VIS_BIN, visualization_name)


def create_new_disease():
    """
    Create and save a new disease
    """
    disease_name = input("What is the disease's name? ")
    time_to_i = int_input('How many steps to transition to infectious state? ')
    time_to_r = int_input('How many steps to transition to removed state? ')
    inf_prob = float_input('What is the probability of transmission to neighbors? ')
    start_num_infected = int_input('How many nodes should be infectious at the start? ')
    with open(f'{constants.DISEASE_DIR}/{disease_name}.txt', 'w') as dis_file:
        dis_file.write(f'{time_to_i} {time_to_r} {inf_prob} {start_num_infected}\n')


def select_file_from_dir(dir_name: str, prompt: str) -> str:
    """
    Read the contents of a directory and allow the user to select one of the files in it.
    """
    file_names = filter(lambda gn: len(gn), run_cmd('ls', dir_name).split('\n'))
    choices = dict(enumerate(file_names))

    selection = -1
    while selection not in choices.keys():
        print(prompt)
        print_choices(choices)
        selection = int_input('? ')

    return dir_name + '/' + choices[selection]


def print_choices(choices: Dict[int, Any]) -> None:
    """
    This is at the heart of the menu system. A collection of choices with corresponding
    integers is displayed so that users only have to type a number to choose something.
    """
    for choice in choices.items():
        print(choice[0], choice[1])


def print_func_choices(choices: Dict[int, Tuple[str, Any]]) -> None:
    """
    A collection of function names with corresponding integers is displayed so that users
    only have to type a number to choose one. The Any in the type signature is actually a function.
    """
    for choice in choices.items():
        print(choice[0], choice[1][0])


if __name__ == "__main__":
    main()
