#!/usr/bin/python3
"""
This is a ui script for the infection resistant network project. The goal is to bring
all the tools together into one cohesive package to make experimenation easier.
"""
import subprocess as sp
import time
from typing import Any, Optional, Dict


GRAPH_DIR = 'graphs'
BIN_DIR = 'bin'
DISEASE_DIR = 'diseases'
VIS_DIR = 'visualizations'
TMP_DIR = '/tmp/irn-ui-vis'
SIM_BIN = f'{BIN_DIR}/infection-resistant-network'
VIS_BIN = f'{BIN_DIR}/graph-visualizer'


def main():
    run_cmd('mkdir', TMP_DIR, silent=True)
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
    graph_name = select_file_from_dir(GRAPH_DIR, 'Select a graph to analyze:')

    print('you selected', graph_name)


def run_simulation_batch():
    """
    Runs a group of simulations and displays a summary of the results
    """
    graph_name = select_file_from_dir(GRAPH_DIR, 'Select a graph to use:')
    disease_name = select_file_from_dir(DISEASE_DIR, 'Select a disease to use:')
    num_simulations = int_input('How many simulations? ')
    sim_length = int_input('How many steps for each simulation? ')
    output = run_cmd(SIM_BIN, disease_name, graph_name,
                     str(num_simulations), str(sim_length))
    print()
    print(output)


def visualize_sim():
    """
    Runs a simulation and then opens the visualization program to show an animation
    """
    graph_name = select_file_from_dir(GRAPH_DIR, 'Select a graph to use:')
    disease_name = select_file_from_dir(DISEASE_DIR, 'Select a disease to use:')
    save_vis = bool_input('Would you like to save the visualization?')
    if save_vis:
        vis_name = input('Enter a name: ')
        file_name = f'{VIS_DIR}/{vis_name}.txt'
    else:
        file_name = f'{TMP_DIR}vis_{"".join(time.ctime().split(" "))}.txt'

    output = run_cmd(SIM_BIN, disease_name, graph_name)
    print(output.split('\n')[-1])
    with open(file_name, 'w') as vis_file:
        with open(graph_name, 'r') as graph_file:
            graph_text = graph_file.readlines()
            vis_file.writelines(graph_text + ([] if graph_text[-1] == '\n' else ['\n']))
            vis_file.write(output)
    run_cmd(VIS_BIN, file_name)


def load_visualization():
    """
    load a previously saved visualization and display it
    """
    visualization_name = select_file_from_dir(VIS_DIR, 'Select a visualization:')
    run_cmd(VIS_BIN, visualization_name)


def create_new_disease():
    """
    Create and save a new disease
    """
    disease_name = input("What is the disease's name? ")
    time_to_i = int_input('How many steps to transition to infectious state? ')
    time_to_r = int_input('How many steps to transition to removed state? ')
    inf_prob = float_input('What is the probability of transmission to neighbors? ')
    start_num_infected = int_input('How many nodes should be infectious at the start? ')
    with open(f'{DISEASE_DIR}/{disease_name}.txt', 'w') as dis_file:
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


if __name__ == "__main__":
    main()
