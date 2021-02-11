#!/usr/bin/python3

from tkinter import Frame, Listbox, StringVar, Tk, Button, Entry, Label
from tkinter.constants import BOTTOM, END, LEFT, RIGHT
import constants as cns
from utility import ls_dir, run_cmd
import sim


def main():
    main_window = build_main_window()
    main_window.mainloop()


def build_main_window():
    root = Tk()
    root.title('DIRN Tool')
    root.geometry('800x400')
    frame = Frame(root)
    frame.pack()

    run_batch_button = Button(frame, command=lambda: run_batch_screen(root, frame),
                              text='Run batch')
    run_batch_button.pack(side=LEFT)

    run_vis_sim_button = Button(frame, command=lambda: run_vis_sim_screen(root, frame),
                                text='Visualize Simulation')
    run_vis_sim_button.pack(side=LEFT)

    analyze_graph_button = Button(frame, command=build_analyze_graph_window,
                                  text='Analyze a Graph')
    analyze_graph_button.pack(side=BOTTOM)

    load_visualization_button = Button(frame, command=build_load_visualization_window,
                                       text='Load Visualization')
    load_visualization_button.pack(side=BOTTOM)

    edit_diseases_button = Button(frame, command=build_edit_diseases_window,
                                  text='Edit Diseases')
    edit_diseases_button.pack(side=BOTTOM)

    return root


def run_batch_screen(root: Tk, old_frame: Frame):
    old_frame.forget()
    frame = Frame(root)
    frame.pack()

    # list of graphs and diseases
    graph_names = ls_dir(cns.GRAPH_DIR)
    disease_names = ls_dir(cns.DISEASE_DIR)
    list_box_height = max(len(graph_names), len(disease_names))

    graph_list_box = Listbox(frame, exportselection=False, height=list_box_height,
                             selectbackground='deepskyblue')
    graph_list_box.insert(END, *graph_names.contents)
    disease_list_box = Listbox(frame, exportselection=False, height=list_box_height,
                               selectbackground='deepskyblue')
    disease_list_box.insert(END, *disease_names.contents)

    # misc
    slb_label = Label(frame, text='Sim Length', width=10)
    sim_len_box = Entry(frame, textvariable=StringVar, bd=4)
    nsb_label = Label(frame, text='Num Sims', width=10)
    num_sims_box = Entry(frame, textvariable=StringVar, bd=4)
    r0_box = Label(frame, text='-', width=10)

    # buttons
    def go_back():
        frame.pack_forget()
        old_frame.pack()
    back_button = Button(frame, command=go_back, text='Back')

    def run():
        graph = graph_names[graph_list_box.get(graph_list_box.curselection())]
        disease = disease_names[disease_list_box.get(disease_list_box.curselection())]
        sim_len = sim_len_box.get()
        num_sims = num_sims_box.get()
        output = run_cmd(cns.SIM_BIN, disease, graph, num_sims, sim_len)
        r0_box.config(text=output, width=len(output))
    run_button = Button(frame, command=run, text='Run')

    # pack the widgets
    back_button.pack(side=BOTTOM)
    r0_box.pack(side=BOTTOM)
    graph_list_box.pack(side=RIGHT, after=back_button)
    disease_list_box.pack(side=RIGHT, after=graph_list_box)
    slb_label.pack(side=BOTTOM, after=disease_list_box)
    sim_len_box.pack(side=BOTTOM, after=slb_label)
    nsb_label.pack(side=BOTTOM, after=sim_len_box)
    num_sims_box.pack(side=BOTTOM, after=nsb_label)
    run_button.pack(side=BOTTOM, after=num_sims_box)


def run_vis_sim_screen(root: Tk, old_frame: Frame):
    old_frame.forget()
    frame = Frame(root)
    frame.pack()

    # list of graphs and diseases
    graph_names = ls_dir(cns.GRAPH_DIR)
    disease_names = ls_dir(cns.DISEASE_DIR)
    list_box_height = max(len(graph_names), len(disease_names))

    graph_list_box = Listbox(frame, exportselection=False, height=list_box_height,
                             selectbackground='deepskyblue')
    graph_list_box.insert(END, *graph_names.contents)
    disease_list_box = Listbox(frame, exportselection=False, height=list_box_height,
                               selectbackground='deepskyblue')
    disease_list_box.insert(END, *disease_names.contents)

    # misc
    r0_box = Label(frame, text='-', width=10)
    save_label = Label(frame, text='Visualization Name', width=18)
    save_box = Entry(frame, textvariable=StringVar, bd=4)

    # buttons
    def go_back():
        frame.pack_forget()
        old_frame.pack()
    back_button = Button(frame, command=go_back, text='Back')

    def run():
        graph = graph_names[graph_list_box.get(graph_list_box.curselection())]
        disease = disease_names[disease_list_box.get(disease_list_box.curselection())]
        output = sim.visualize_sim(graph, disease, 100)
        save_file_name = f'{cns.VIS_DIR}/{save_box.get()}'\
            if len(save_box.get()) > 0 else f'{cns.VIS_DIR}/tmp'
        result = output.split('\n')[-2]
        r0_box.config(text=result, width=len(result))
        with open(save_file_name, 'w') as vis_file:
            with open(graph, 'r') as graph_file:
                graph_text = graph_file.readlines()
                vis_file.writelines(graph_text + ([] if graph_text[-1] == '\n' else ['\n']))
                vis_file.write(output)
        run_cmd(cns.VIS_BIN, save_file_name)
    run_button = Button(frame, command=run, text='Run')

    # pack the widgets
    back_button.pack(side=BOTTOM)
    r0_box.pack(side=BOTTOM)
    graph_list_box.pack(side=RIGHT, after=back_button)
    disease_list_box.pack(side=RIGHT, after=graph_list_box)
    run_button.pack(side=BOTTOM, after=disease_list_box)
    save_label.pack(side=BOTTOM, after=run_button)
    save_box.pack(side=BOTTOM, after=save_label)


def build_analyze_graph_window():
    root = Tk()
    root.geometry('200x200')
    root.mainloop()


def build_load_visualization_window():
    root = Tk()
    root.geometry('200x200')
    root.mainloop()


def build_edit_diseases_window():
    root = Tk()
    root.geometry('200x200')
    root.mainloop()


if __name__ == '__main__':
    main()
