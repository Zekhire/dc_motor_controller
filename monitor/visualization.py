import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np
import json

import queue
import sys

import datetime


def date_conversion(t_sample, date, relative_time):
    if relative_time:
        date_converted = round(t_sample, 3)
    else:
        timestamp = datetime.datetime.fromtimestamp(date)
        date_converted = timestamp.strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
    return date_converted


def controll_visualization(q_s2v, monitor_data, **kwargs):
    # editable parameters
    grid_color = [92/255, 214/255, 222/255, 1]

    # unpack monitor data
    visualization_data = monitor_data["visualization"]
    last_n        = visualization_data["last_n"]
    tick_nth      = visualization_data["tick_nth"]
    relative_time = visualization_data["relative_time"]

    # Prepare lists for data
    t_local     = []
    w_ref_local = []
    w_local     = []
    dates_local = []

    # Prepare lists for ticks
    xticks       = []
    xtickslabels = []

    # Configure plot
    plt.style.use('dark_background')
    fig, ax = plt.subplots()
    fig.canvas.toolbar.pack_forget()
    if relative_time:
        ax.set_xlabel('time [s]')
    else:
        ax.set_xlabel('date')
    ax.set_ylabel('w [rad/s]')

    # Get handles for axes
    ln0, = plt.plot([], [], 'b-o', label="w", markersize=3)
    ln1, = plt.step([], [], 'r-',  label="w ref", where='post')

    # Add legend
    ax.legend(loc="upper right")

    class Pack:
        def __init__(self):
            self.was_first = 0
            self.starter   = 0
            self.i         = 0

    def update(frame, q_s2v, pack, emptying=True, received_limit=2):
        received = 0
        while True or received < received_limit:
            # Get data from condition monitoring
            try:
                # Get tuple with data from source
                data_tuple   = q_s2v.get(timeout=0)
                w_sample     = data_tuple[0]
                w_ref_sample = data_tuple[1]
                date         = data_tuple[2]

                # Need to save first date (for reference)
                if pack.was_first == 0:
                    pack.was_first = 1
                    pack.starter = date

                pack.i += 1

                # distance between next samples are determined by
                # this substraction
                t_sample = date - pack.starter

                # convert date to relative one or absolute 
                date_converted = date_conversion(t_sample, date, relative_time)

                # There is need to save this on disc
                w_local.append(w_sample)
                dates_local.append(date_converted)
                t_local.append(t_sample)
                w_ref_local.append(w_ref_sample)
                del w_local    [0:-last_n]     # don't need to store this in file 
                del dates_local[0:-last_n]     # don't need to store this in file 
                del t_local    [0:-last_n]     # don't need to store this in file 
                del w_ref_local[0:-last_n]     # don't need to store this in file 

                # compute xtics
                if pack.i%tick_nth==0:
                    xticks.append(t_local[-1])
                    xtickslabels.append(dates_local[-1])
                    pack.i = 0
                xticks_local       = xticks      [-int(last_n/tick_nth):]
                xtickslabels_local = xtickslabels[-int(last_n/tick_nth):]

                # Set dates on xtics
                ax.set_xticks(xticks_local)
                ax.set_xticklabels(xtickslabels_local, rotation=45)

                # speed plot
                ln0.set_data(t_local, w_local)

                # Set x/y lims
                ax.set_xlim(t_local[0], t_local[-1])
                ax.set_ylim(0, 120)

                # reference speed plot
                ln1.set_data(t_local, w_ref_local)

                received += 1
            except queue.Empty:
                break

        return ln0, ln1

    ani = FuncAnimation(fig, update, fargs=(q_s2v, Pack(),), interval=1, blit=False)
    plt.grid(which='both', color=grid_color)
    plt.show()
