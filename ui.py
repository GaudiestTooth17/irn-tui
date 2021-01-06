#!/usr/bin/python3
"""
This is a ui script for the infection resistant network project. The goal is to bring
all the tools together into one cohesive package to make experimenation easier.
"""
import subprocess as sp
from typing import Any, Optional, Dict


GRAPH_DIR = 'graphs'
BIN_DIR = 'bin'
DISEASE_DIR = 'diseases'


def main():
    while True:
        next_function = main_menu()
        next_function()


def main_menu():
    """
    :return: a function that does the next thing the user wants to do
    """
    selection = -1
    # a collection of choices with an index, plain English name, and a function to call
    choices = list(enumerate((('analyze graph', analyze_graph),
                             ('run simulation batch', run_simulation_batch),
                             ('visualize simulation', visaulize_sim),
                             ('quit', exit))))
    valid_numbers = list(map(lambda c: c[0], choices))

    while selection not in valid_numbers:
        print('Select an option:')
        for choice in choices:
            print(f'{choice[0]} {choice[1][0]}')
        selection = int_input()

    # return the function to call
    return dict(choices)[selection][1]


def analyze_graph():
    graph_name = select_file_from_dir(GRAPH_DIR, 'Select a graph to analyze:')

    print('you selected', graph_name)


def run_simulation_batch():
    graph_name = select_file_from_dir(GRAPH_DIR, 'Select a graph to use:')
    num_simulations = int_input('How many simulations? ')
    sim_length = int_input('How many steps for each simulation? ')
    output = run_cmd('bin/infection-resistant-network', graph_name,
                     str(num_simulations), str(sim_length))
    print(output)


def visaulize_sim():
    print('visaulize simulation')


def select_file_from_dir(dir_name: str, prompt: str) -> str:
    file_names = filter(lambda gn: len(gn), run_cmd('ls', dir_name).split('\n'))
    choices = dict(enumerate(file_names))

    selection = -1
    while selection not in choices.keys():
        print(prompt)
        print_choices(choices)
        selection = int_input('? ')

    return choices[selection]


def print_choices(choices: Dict[int, Any]) -> None:
    for choice in choices.items():
        print(choice[0], choice[1])


def safe_int(obj: Any) -> Optional[int]:
    try:
        return int(obj)
    except ValueError:
        return None


def int_input(msg='') -> int:
    x = safe_int(input(msg))
    if x is None:
        x = int_input(msg)
    return x


def run_cmd(cmd, *args) -> str:
    raw_output = sp.check_output([cmd] + args, stderr=sp.STDOUT)
    return raw_output.decode('utf-8')


if __name__ == "__main__":
    main()
