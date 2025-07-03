import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from Tools.Osciloscopio import Osciloscopio
from Tools.Pulser import Pulser
from Tools.Decorators import cronometer
from Tools.PID import PID
import threading
import queue
import time

def PWfdbk():
    """
    Función principal para ejecutar el control de potencia con retroalimentación.
    """
    # Configuración del osciloscopio
    osci = Osciloscopio("USB0::0xF4EC::0xEE3A::SDS1MKGX802538::0::INSTR", 2) #osciloscopio Siglent
    print(osci)

    # Configuración del generador de pulsos
    pulser = Pulser("USB0::0xF4EC::0xEE38::SDG1XDDC801175::0::INSTR", 2)
    pulser.set_frecuencia(38000)  # Frecuencia en Hz
    pulser.set_amplitud(0.25)  # Amplitud inicial en V
    print(pulser)

    # Configuración del PID
    kP = 2
    kI = 0.01
    kD = 0

    pid = PID( kP=kP, kI=kI, kD=kD, setpoint=0.25, max_output=0.8)  # Setpoint de 0.25 V

    # cola para almacenar los datos de potencia
    potencia_queue = queue.Queue()

    # Iniciar el bucle de medición en un hilo separado
    medicion_thread = threading.Thread(target=bucleMedicion, args=(osci, potencia_queue))
    medicion_thread.daemon = True  # Permite que el hilo se cierre al finalizar el programa
    medicion_thread.start()

    pulser.ouput_on()
    for i in np.linspace(0, 10, 100):  # Simulación por 10 segundos
        pass

def SimpleFeedback() -> None:
    # Configuración del osciloscopio
    osci = Osciloscopio()

    # Configuración del generador de pulsos
    pulser = Pulser()
    frecuencia = 38000
    pulser.set_frecuencia(frecuencia)  # Frecuencia en Hz
    pulser.set_amplitud(0.25)  # Amplitud inicial en V
    print(pulser)

    # Configuración del PID
    kP = 1 #Si hay 1W de diferenciam, el PID subirá 0.1V
    kI = 0.2
    kD = 0.2

    PowerRef = 2 #W

    pid = PID(Kp=kP, Ki=kI, Kd=kD, setpoint=PowerRef)
    
    print("Iniciando el control de potencia...\n")
    print(f"Referencia de potencia: {PowerRef} W\n")
    print(f"Parámetros PID: kP={kP}, kI={kI}, kD={kD}\n")
    print("tiempo Experimento: 10 segundos\n")

    data = pd.DataFrame(columns=['Tiempo (s)', 'Potencia (W)', 'Salida PID (V)'])
    output = 0.0
    with pulser as pulser:
        pulser.output_on()
        t0 = time.time()
        Texp = t0 + 10
        while time.time() < Texp:
            try:
                pulser.set_amplitud(pulser.amp1 + output)
            except ValueError:
                pulser.set_amplitud(0.6)
            #P = osci.MedirPotencia(1, 2)
            P = osci.MedirPotenciaMedicsen()
            t = time.time()
            dt = t - t0
            output = pid.update(P, dt=dt)
            t0 = time.time()
            #print(f"PID output: {output:.2f} V, Potencia medida: {P:.2f} W, Tiempo: {time.time():.2f} s")
            #print(f"seting amplitude to {pulser.amp1 + output:.2f} V")
            nueva_fila = pd.DataFrame([{'Tiempo (s)': t, 'Potencia (W)': P, 'Salida PID (V)': output}])
            data = pd.concat([data, nueva_fila], ignore_index=True)
        pulser.output_off()

    print("Control de potencia finalizado.\n")
    
    print(data)

    # Graficar resultados
    plt.figure(figsize=(10, 6))
    plt.plot(data['Tiempo (s)'], data['Potencia (W)'], label='Potencia medida (W)', color='blue')
    plt.plot(data['Tiempo (s)'], data['Salida PID (V)'], label='Salida PID (V)', color='orange')
    plt.xlabel('Tiempo (s)')
    plt.ylabel('Valor')
    plt.title(f"Control de Potencia con PID a f = {frecuencia}")
    plt.legend()
    plt.grid()
    plt.show()

def stepResponse(osci: Osciloscopio, pulser: Pulser, pid: PID) -> None:
    """
    Realiza una respuesta al escalón del sistema.
        Args:
            osci (Osciloscopio): Objeto del osciloscopio para medir la respuesta.
            pulser (Pulser): Objeto del generador de pulsos para aplicar el escalón.
            pid (PID): Controlador PID para ajustar la salida.
        Returns:
            Vector de tiempos y valores medidos.
    """
    from frecResonancia import frecResonancia

    #fr = frecResonancia(osci, pulser)
    fr = 37849
    # Configuración del generador de pulsos
    pulser.set_amplitud(0.05)  # Amplitud inicial en V
    pulser.set_frecuencia(fr)  # Frecuencia en Hz
    pulser.enable_output()
    # Medición inicial
    P_inicial = osci.MedirPotencia(1,2)
    print(f"Valor inicial medido: {P_inicial} W")

    t0 = time.time()
    t = 0
    i = 0
    Parr = []
    tarr = []
    tmarr = []
    st = False
    while t < 15: 
        p, tm = cronometer(osci.MedirPotenciaMedicsen)(1,3)
        t = time.time() - t0

        if t > 7 and st == False:
            pulser.set_amplitud(0.25) 
            st = True
        i += 1
        print(f"Tiempo: {t:.1f} iter = {i}, P = {p}")
        Parr.append(p)
        tarr.append(t)
        tmarr.append(tm)
    pulser.disable_output()
    pps = i/tarr[i-1]
    print(f"Measurements made at {pps} points per second")
    print(f"avr loop time {np.mean(tarr)}")
    avrT = np.mean(tmarr)
    print(f"avr measure time {avrT}")
    print(f"Sampling rate = {1/avrT} Hz")

    plt.plot(tarr,Parr, 'o', markersize=2)
    plt.show()
        

def UnmeasuredStep(frec):
    """
    Performs a power step from no output to 0.25V
        Args:
            frec(float): Resonant frec of tranducer.
    """
    with Pulser() as pulse:
        pulse.set_frecuencia(frec)
        pulse.set_amplitud(0.25)
        time.sleep(5)
        pulse.output_on()
        time.sleep(5)


def bucleMedicion(osci: Osciloscopio, potencia_queue: queue.Queue, tiempoSampleo: float = 0.02) -> None:
    """
    Bucle de medición que actualiza la potencia y la envía a la cola.
        Args:
            osci (Osciloscopio): Objeto del osciloscopio para medir la potencia.
            potencia_queue (queue.Queue): Cola para almacenar los datos de potencia.
    """
    while True:
        P = osci.MedirPotencia(1, 2)
        potencia_queue.put(P)
        time.sleep(tiempoSampleo)  # Espera [segundos] entre mediciones

if __name__ == "__main__":
    osci = Osciloscopio()
    pid = PID(0, 0, 0)
    with Pulser() as pulser:
        stepResponse(osci, pulser, pid)

    