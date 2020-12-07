import matplotlib.pyplot as plt
import numpy as np


class Speed_Reference_Signal:
    def __init__(self, show=False):

        # self.iterations = int(t_max/dt)
        self.dt = 0.01
        u_step_magnitudes = [20, 60, 80, 40]
        step_period = 1000

        # u_step_magnitudes = [20, 40, 80,  60,  20, 
        #                     40, 20, 40, -20, -40, 
        #                     -20, 40, 20, -40, -20,
        #                     40, 60, 100, 100, 90,
        #                     50, 60, 40, 20, 60,
        #                     -20, -40, -20, 40, 20,
                            
        #                     55, 70, 80, 100, 75,
        #                     50, 60, 40, 50, 30,
        #                     10, 20, -20, -30, -15,
        #                     -20, -50, -25, 10, 30,
        #                     45, 50, 15, 30, 25,
        #                     50, 75, 90, 80, 20]


        u = np.array([])
        for i in range(len(u_step_magnitudes)):
            u = self.__append_step(u,  u_step_magnitudes[i],  step_period)   # step_period samples

        self.u = u
        self.iterations = len(self.u)

        t = np.ones(self.iterations)
        t = t*self.dt
        t = np.cumsum(t)
        self.t_max = t[-1]
        self.t = t-self.dt

        if show:
            self.__show_signal()


    def __append_step(self, u, magnitude, lenght):
        step = magnitude*np.ones(lenght)
        u = np.append(u, step)
        return u


    # def __append_slope(self, u, magnitude_start, magnitude_end, lenght):
    #     slope = np.ones(lenght)
    #     slope = np.cumsum(t)


    def __show_signal(self):
        plt.plot(self.t, self.u)
        plt.grid(which="both")
        plt.xlim([0, self.t[-1]])
        plt.show()

    def get_simulation_data(self):
        simulation_data = {
            "w_ref": self.u,
            "t": self.t,
            "dt": self.dt,
            "iterations": self.iterations,
            "t_max": self.t_max
        }
        return simulation_data

if __name__ == "__main__":
    speed_reference_signal = Speed_Reference_Signal(True)