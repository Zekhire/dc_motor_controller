import numpy as np
import json
import matplotlib.pyplot as plt

class DC_Motor:
    def __init__(self, motor_data):
        self.motor_data = motor_data
        
        # electrical
        electrical_dict = motor_data["electrical"]
        R = electrical_dict["R"]
        L = electrical_dict["L"]
        K_e = electrical_dict["K_e"]

        # mechanical
        mechanical_dict = motor_data["mechanical"]
        J = mechanical_dict["J"]
        K_t = mechanical_dict["K_t"]
        K_f = mechanical_dict["K_f"]

        self.J = J
        self.K_t = K_t

        # initial conditions
        initial_dict = motor_data["initial"]
        x1 = initial_dict["i"]
        x2 = initial_dict["w_m"]
        x3 = initial_dict["theta_m"]

        # state-space model
        a11 = -R/L
        a12 = -K_e/L
        a21 =  K_t/J
        a22 = -K_f/J
        a32 = 1
        self.A = np.matrix([[a11, a12, 0], [a21, a22, 0], [0, 1, 0]])
        
        b11 = 1/L
        b22 = -1/J
        self.B = np.matrix([[b11, 0], [0, b22], [0, 0]])

        c41 = K_t 
        self.C = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1], [c41, 0, 0]])
        self.x = np.matrix([[x1], [x2], [x3]])

        # print(self.A)
        # print(self.B)
        # print(self.C)
        # exit()

    def refresh(self):
        # initial conditions
        initial_dict = self.motor_data["initial"]
        x1 = initial_dict["i"]
        x2 = initial_dict["w_m"]
        x3 = initial_dict["theta_m"]
        self.x = np.matrix([[x1], [x2], [x3]])


    def simulation_euler(self, dt, iterations, u_dict):
        # Prepare arrays for signals
        i       = np.zeros(iterations)
        w_m     = np.zeros(iterations)
        theta_m = np.zeros(iterations)
        T_e     = np.zeros(iterations)

        # Simulation
        for j in range(iterations):
            # if (j%1000 == 0):
            #     print(j, iterations)

            y = self.C*self.x
            # Unpack output signals
            i[j]       = y[0]
            w_m[j]     = y[1]
            theta_m[j] = y[2]
            T_e[j]     = y[3]

            # Euler
            u = np.matrix([[u_dict["v_s"][j]], 
                           [u_dict["T_l"][j]]])
            self.x = self.x + dt*(self.A*self.x + self.B*u)


        y_dict = {
            "i": i,
            "w_m": w_m,
            "theta_m": theta_m,
            "T_e": T_e
        }
        return y_dict
        


def derivative(u, dt):
    u_prim = np.zeros(len(u))
    for i in range(len(u)):
        if i > 0:
            u_prim[i] = (u[i]-u[i-1])/dt
        else:
            u_prim[i] = u[i]
    return u_prim


def save_outputs(t, y):
    data_file = open("dc_motor_step_response.txt", "w")
    for i in range(len(t)):
        if i%10 != 0:
            continue
        data_file.write(str(t[i])+" "+str(y[i])+"\n")
    data_file.close()


if __name__ == "__main__":
    motor_data = json.load(open("./dc_motor_data_bs.json"))
    dc_motor = DC_Motor(motor_data)

    t_end = 100
    dt = 0.01
    iterations = int(t_end/dt)
    print(iterations)

    t = np.ones(iterations)
    t = t*dt
    t = np.cumsum(t)
    t = t-dt


    v_s = 12*np.ones(iterations)
    T_l = 0*np.ones(iterations)
    u_dict = {
        "v_s": v_s,
        "T_l": T_l
        }

    simulation_results = dc_motor.simulation_euler(dt, iterations, u_dict)
    # save_outputs(t, simulation_results["w_m"])

    plt.plot(t, simulation_results["w_m"])
    plt.xlabel("t [s]")
    plt.ylabel("w_m [rad/s]")
    plt.minorticks_on()
    plt.grid(b=True, which='both')
    plt.show()

    plt.plot(t, simulation_results["w_m"]*60/(2*np.pi))
    plt.xlabel("t[s]")
    plt.ylabel("Mech. speed [rpm]")
    plt.minorticks_on()
    plt.grid(b=True, which='both')
    plt.show()