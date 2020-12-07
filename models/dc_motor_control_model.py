import dc_motor_model_bs
import pi_controller
import json
import numpy as np
import matplotlib.pyplot as plt
import reference_signal
import time


class Simulation:
    def __init__(self, motor_data_path, pi_controller_data_path):
        motor_data         = json.load(open(motor_data_path))
        pi_controller_data = json.load(open(pi_controller_data_path))

        self.dc_motor      = dc_motor_model_bs.DC_Motor(motor_data)
        self.pi_controller = pi_controller.PI_Controller(pi_controller_data)

        # Simulation parameters
        dt     = 0.001
        freq_s = 500

        ref_signal = reference_signal.Speed_Reference_Signal()
        simulation_data = ref_signal.get_simulation_data()

        self.w_ref      = simulation_data["w_ref"]
        self.t          = simulation_data["t"]
        self.dt         = simulation_data["dt"]
        self.iterations = simulation_data["iterations"]

        self.freq_s = freq_s
        # self.every_nth_sample = self.__get_sampled_indexes()
        self.every_nth_sample = 1

        self.T_l = np.ones(self.iterations)

        self.w = np.zeros(self.iterations)
        self.w_measure_time = np.zeros(self.iterations)


    def __get_sampled_indexes(self):
        every_nth_sample = int((1/self.dt)*(1/self.freq_s))
        return every_nth_sample


    def run_simulation(self, show=True, noise=False, T_l=0):
        # O>xxx<=>xxx<=>xxx<=>xxx<O #
        #   Simulation main loop    #
        # O>xxx<=>xxx<=>xxx<=>xxx<O #
        self.T_l *= T_l

        for i in range(self.iterations):
            if i%1000 == 0:
                print(str((i/self.iterations)*100)+"%")

            # O>xxx<=>xxx<=>xxx<=>xxx<O #
            #  Feedback loop sum block  #
            # O>xxx<=>xxx<=>xxx<=>xxx<O #
            if i == 0:
                e = self.w_ref[i]
            else:
                e = self.w_ref[i] - self.w[i-1]
                
            # O>xxx<=>xxx<=>xxx<=>xxx<O #
            #    PI controller block    #
            # O>xxx<=>xxx<=>xxx<=>xxx<O #
            u_dict = {"e": np.array([e])}
            y_dict_pi_controller = self.pi_controller.simulation_euler_anti_windup(self.dt, 1, u_dict)
            # y_pi_controller = pi_controller.simulation_euler(dt, 1, u_dict)
            v_s = y_dict_pi_controller["y"][0]

            # O>xxx<=>xxx<=>xxx<=>xxx<O #
            #         DC motor          #
            # O>xxx<=>xxx<=>xxx<=>xxx<O #
            u_dict = {"v_s": np.array([v_s   ]), 
                      "T_l": np.array([self.T_l[i]])}
            y_dict_dc_motor = self.dc_motor.simulation_euler(self.dt, 1, u_dict)
            self.w[i] = y_dict_dc_motor["w_m"][0]
            self.w_measure_time[i] = time.time()

            if noise:
                # self.w[i] += 5*np.sin(20*self.t[i])# + np.random.randint(-10, 10)
                noise = np.random.normal(0, .1)
                self.w[i] += noise
        
        if show:
            self.__show_simulation_results()

        return self.w[::self.every_nth_sample]


    def __show_simulation_results(self):
        # plt.plot(self.t, self.w, "-b", label="motor speed")
        plt.plot(self.t, self.w_ref[:self.iterations], "-r", label="motor speed reference")
        plt.step(self.t[::self.every_nth_sample], self.w[::self.every_nth_sample], "-b", where='post', label="motor speed")
        plt.xlim([0, self.t[-1]])
        plt.xlabel("t[s]")
        plt.ylabel("w[rad/s]")
        plt.legend(loc="right")
        plt.grid(which="both")
        plt.show()


if __name__ == "__main__":
    dc_motor_data_path = "./dc_motor_data_bs.json"
    pi_controller_data_path = "./pi_controller_data.json"
    show = False
    noise = False

    simulation = Simulation(dc_motor_data_path, pi_controller_data_path)
    w0 = simulation.run_simulation(show=show, noise=noise, T_l=0)
    simulation = Simulation(dc_motor_data_path, pi_controller_data_path)
    w1 = simulation.run_simulation(show=show, noise=noise, T_l=0.007)   # 0.007 for dt=0.001
    simulation = Simulation(dc_motor_data_path, pi_controller_data_path)
    w2 = simulation.run_simulation(show=show, noise=noise, T_l=0.015)   # 0.015 for dt=0.001

    plt.plot(simulation.t, simulation.w_ref[:simulation.iterations], "-r", label="motor speed reference")
    plt.step(simulation.t, w0, "-b", where='post', label="motor speed healthy")
    plt.step(simulation.t, w1, "-y", where='post', label="motor speed degraded")
    plt.step(simulation.t, w2, "-g", where='post', label="motor speed broken")
    plt.xlim([0, simulation.t[-1]])
    plt.xlabel("t[s]")
    plt.ylabel("w[rad/s]")
    plt.legend(loc="right")
    plt.grid(which="both")
    plt.show()