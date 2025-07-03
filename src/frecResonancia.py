import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from Tools.Osciloscopio import Osciloscopio
from Tools.Pulser import Pulser
from Tools.PID import PID
import time

def meanfrecResonance(osci: Osciloscopio, pulser : Pulser, fr_start : float, fr_end : float, nb_points : int, nb_rep : int) -> tuple :

    # empty list to collect the maximum frequency at each iteration
    fr_max_pow_list = []
    fr_phase_null_list = []

    for rep in range (0, nb_rep):
        # empty list to collect data
        pow = []
        phase = []
        frequency = []

        # generator settings
        fr = fr_start # start
        step = np.linspace(fr_start, fr_end, nb_points)
        pulser.set_amplitud(0.2)  # Amplitud inicial en V
        pulser.set_frecuencia(fr)  # Frecuencia en Hz
        pulser.enable_output()

        while fr < fr_end :
            pulser.set_frecuencia(fr)
            time.sleep(0.03)
            frequency.append(fr)
            pow.append(osci.MedirPotencia(1,2))
            phase.append(osci.MedirFase(1,2))
            fr += step
                
        pulser.disable_output()

        # two ways to find the resonance frequency
        index_max_pow = np.argmax(pow)
        max_pow = pow[index_max_pow]
        fr_max_pow = frequency[0] + index_max_pow * step

        index_phase_null = np.argmin(np.abs(phase))
        phase_null = phase[index_phase_null]
        fr_phase_null = frequency[0] + index_phase_null * step

        fr_max_pow_list.append(fr_max_pow)
        fr_phase_null_list.append(fr_phase_null)

        print(f"Resonance frequency at iteration {rep} is {fr_max_pow} with power = {max_pow} and index = {index_max_pow}")
        print(f"Resonance frequency at iteration {rep} is {fr_phase_null} with power = {phase_null} and index = {index_phase_null}")

        # print the curves
        fig_pow, ax_pow = plt.subplots()
        ax_pow.plot(frequency, pow)
        ax_pow.set_title(f"iteration {rep}")
        ax_pow.set_xlabel("Frequency (Hz)")
        ax_pow.set_ylabel("Power (W)")
        ax_pow.set_ylim()  
        ax_pow.grid(True)
        plt.show()

        fig_phase, ax_phase = plt.subplots()
        ax_phase.plot(frequency, phase)
        ax_phase.set_title(f"iteration {rep}")
        ax_phase.set_xlabel("Frequency (Hz)")
        ax_phase.set_ylabel("Power (W)")
        ax_phase.set_ylim()  
        ax_phase.grid(True)
        plt.show()

    # table with values of the resonance frequency found at each iteration
    data = {
    "max freq power": fr_max_pow_list,
    "max freq phase": fr_phase_null_list,
    }

    #load data into a DataFrame object and print it 
    df = pd.DataFrame(data)
    print(df)

    # finding the mean and the minimum and maximum in order to find the standart error
    
    mean_pow = np.mean(fr_max_pow_list)
    mean_phase = np.mean(fr_phase_null_list)

    std_dev_pow = np.std(fr_max_pow_list)
    std_dev_phase = np.std(fr_phase_null_list)

    std_error_pow = std_dev_pow / np.sqrt(len(fr_max_pow_list))
    std_error_phase = std_dev_phase / np.sqrt(len(fr_phase_null_list))

    print(f"frequency power mean = {mean_pow} ± {std_error_pow}")
    print(f"frequency phase mean = {mean_phase} ± {std_error_phase}")

    return fr_max_pow_list, fr_phase_null_list

def frecResonance(osci: Osciloscopio, pulser : Pulser, fr_start : float, fr_end : float, nb_points : int) -> None:
    
    # empty list to collect data
    pow = []
    phase = []
    frequency = []

    # generator settings
    fr = fr_start # start
    step = np.linspace(fr_start, fr_end, nb_points)
    pulser.set_amplitud(0.2)  # Amplitud inicial en V
    pulser.set_frecuencia(fr)  # Frecuencia en Hz
    pulser.enable_output()

    while fr < fr_end :
        pulser.set_frecuencia(fr)
        time.sleep(0.03)
        frequency.append(fr)
        pow.append(osci.MedirPotencia(1,2))
        phase.append(osci.MedirFase(1,2))
        fr += step
            

    pulser.disable_output()

    # two ways to find the resonance frequency
    index_max_pow = np.argmax(pow)
    max_pow = pow[index_max_pow]
    fr_max_pow = frequency[0] + index_max_pow * step

    index_phase_null = np.argmin(np.abs(phase))
    phase_null = phase[index_phase_null]
    fr_phase_null = frequency[0] + index_phase_null * step

    print(f"Resonance frequency is {fr_max_pow} with power = {max_pow} and index = {index_max_pow}")
    print(f"Resonance frequency is {fr_phase_null} with power = {phase_null} and index = {index_phase_null}")

    # print the curves
    fig_pow, ax_pow = plt.subplots()
    ax_pow.plot(frequency, pow)
    ax_pow.set_xlabel("Frequency (Hz)")
    ax_pow.set_ylabel("Power (W)")
    ax_pow.set_ylim()  
    ax_pow.grid(True)
    plt.show()

    fig_phase, ax_phase = plt.subplots()
    ax_phase.plot(frequency, phase) 
    ax_phase.set_xlabel("Frequency (Hz)")
    ax_phase.set_ylabel("Power (W)")
    ax_phase.set_ylim()  
    ax_phase.grid(True)
    plt.show()

    return fr_max_pow, fr_phase_null


if __name__ == "__main__":
    # finding the osciloscope and connecting to it 
    osci = Osciloscopio()
    pulser = Pulser()
    # finding the pulser and connecting to it
    with pulser as pulser:
       fr_max_pw, fr_phase_null = frecResonance(osci, pulser, 34000, 42000, 320) 