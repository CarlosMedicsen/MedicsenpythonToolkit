import pyvisa
import os
import numpy as np
import random as rd
import json
import time

class Osciloscopio:
    def __init__(self, id: str = "", numcanales:int = 0):
        if id == "":
            self.AutoConnect()
        else:
            self.id = id
            self.numcanales = numcanales
        self.modelo = None
        self.connect()
        self.Identificar()

    def connect(self):
        rm = pyvisa.ResourceManager()
        self.conexion = rm.open_resource(self.id)
    
    def AutoConnect(self) -> bool:
        """
        Auto Connect protocol for the known Osciloscope.
        Looks for connected Osciloscopes In the Equipement json
        Connects to them and auto Configures.
        Raises:
            LookupError: if no known device is connected.
        """
        connectedDevices = pyvisa.ResourceManager().list_resources()
        
        ruta_json = os.path.join(os.path.dirname(__file__), "Equipment.json")
        with open(ruta_json, 'r') as f:
            knownDevices = json.load(f)

        for id in connectedDevices:
            for nombre, datos in knownDevices.get("osciloscopios", {}).items():
                if id in datos.get("aliases", []):
                    self.id = id
                    self.numcanales = datos.get("numCanales")
                    print(f"Se ha conectado el osci: {nombre} automáticamente.")
                    return
        raise LookupError(f"No known Osciloscope conected, please connect a known osciloscope")

    def Identificar(self) -> str:
        """
        Identifica el modelo del osciloscopio conectado.
            Returns:
                str: Modelo del osciloscopio.
        """
        if not hasattr(self, 'conexion'):
            raise RuntimeError("No hay conexión abierta. Por favor, conecte primero.")
        
        try:
            idn = self.conexion.query("*IDN?")
            if "siglent" in idn.lower():
                self.modelo = "Siglent"
            if "keysight" in idn.lower():
                self.modelo = "Keysight"
            if not self.modelo:
                self.modelo = "Desconocido"
                print("Modelo de osciloscopio no reconocido.")

        except pyvisa.VisaIOError as e:
            raise RuntimeError(f"Error al identificar el osciloscopio: {e}")

        return self.conexion.query("*IDN?").strip()

    def MedirVpp_Keysight(self, chan: int) -> float:
        """
        Mide el valor de Vpp del canal especificado en un osciloscopio Keysight.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de Vpp (En V) del canal especificado.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        comando = f"MEASURE:VPP? CHAN{chan}"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())

    def MedirVpp_Siglent(self, chan: int) -> float:
        """
        Mide el valor de Vpp del canal especificado en un osciloscopio Sylgent.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de Vpp (En V) del canal especificado.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
       
        comando = f":C{chan}:PARAMETER_VALUE? PKPK"
        val = self.conexion.query(comando)
        _, valor_str = val.split(",")
        resultado = float(valor_str.strip("()V \n\r\t"))
        return float(resultado.strip())
    
    def MedirFase_Keysight(self, chan1: int, chan2: int) -> float:
        """
        Mide la fase entre dos canales especificados en un osciloscopio.
            Args:
                chan1 (int): Número del primer canal (1 a numcanales).
                chan2 (int): Número del segundo canal (1 a numcanales).
            Raises:
                ValueError: Si los números de canal no son válidos.
            Returns:
                float: Valor de fase (En grados) entre los dos canales especificados.
        """
        if chan1 < 1 or chan1 > self.numcanales or chan2 < 1 or chan2 > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        comando = f"MEASURE:PHASE? CHAN{chan1},CHAN{chan2}"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())
    
    def MedirFase_Siglent(self, chan1: int, chan2: int) -> float:
        """
        Mide la fase entre dos canales especificados en un osciloscopio Sylgent.
            Args:
                chan1 (int): Número del primer canal (1 a numcanales).
                chan2 (int): Número del segundo canal (1 a numcanales).
            Raises:
                ValueError: Si los números de canal no son válidos.
            Returns:
                float: Valor de fase (En grados) entre los dos canales especificados.
        """
        mok = 0
        i = 0
        if chan1 < 1 or chan1 > self.numcanales or chan2 < 1 or chan2 > self.numcanales:
            raise ValueError("Número de canal no válido")
        while(mok == 0):
            comando = f"C{chan1}-C{chan2}:MEAD? PHA"
            val = self.conexion.query(comando)
            _, valor_str = val.split(",")
            resultado = valor_str.strip("()degree \n\r\t")
            if resultado == '****':
                i += 1
                time.sleep(0.1)
            else:
                if i >= 20:
                    raise RuntimeError("Error al medir la fase, verifique las conexiones.")
                else:
                    mok = 1 #solo paro cuando la fase se mide bien.
        return float(resultado.strip())
    
    def MedirFase(self, chan1: int, chan2: int) -> float:
        """
        Mide la fase entre dos canales especificados en un osciloscopio.
            Args:
                chan1 (int): Número del primer canal (1 a numcanales).
                chan2 (int): Número del segundo canal (1 a numcanales).
            Raises:
                ValueError: Si los números de canal no son válidos.
            Returns:
                float: Valor de fase (En grados) entre los dos canales especificados.
        """
        if self.modelo == "Siglent":
            return self.MedirFase_Siglent(chan1, chan2)
        else:
            return self.MedirFase_Keysight(chan1, chan2)
        
    def MedirFrecuencia_Keysight(self, chan: int) -> float:
        """
        Mide la frecuencia del canal especificado en un osciloscopio.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de frecuencia (En Hz) del canal especificado.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        comando = f"MEASURE:FREQUENCY? CHAN{chan}"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())
    
    def MedirVrms_Keysight(self, chan: int) -> float:
        """
        Mide el valor de Vrms del canal especificado en un osciloscopio Keysight.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de Vrms (En V) del canal especificado.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        comando = f"MEASURE:VRMS? CHAN{chan}"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())
    
    def MedirVrms_Siglent(self, chan: int) -> float:
        """
        Mide el valor de Vrms del canal especificado en un osciloscopio Sylgent.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de Vrms (En V) del canal especificado.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        comando = f":C{chan}:PARAMETER_VALUE? RMS"
        val = self.conexion.query(comando)
        _, valor_str = val.split(",")
        resultado = float(valor_str.strip("()V \n\r\t"))
        return resultado

    def MedirVrms(self, chan: int) -> float:
        """
        Mide el valor de Vrms del canal especificado en un osciloscopio.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de Vrms (En V) del canal especificado.
        """
        if self.modelo == "Siglent":
            return self.MedirVrms_Siglent(chan)
        else:
            return self.MedirVrms_Keysight(chan)

    def MedirPotenciaCompleta(self, chanV: int, chanI: int) -> tuple:
        """
        Mide la potencia del canal especificado en un osciloscopio Keysight.
            Args:
                chanV (int): Número del canal de voltaje (1 a numcanales).
                chanI (int): Número del canal de corriente (1 a numcanales).
            Raises:
                ValueError: Si los números de canal no son válidos.
            Returns:
                tuple: Tupla con el valor de potencia (En W), voltaje (En V), corriente (En A) y fase (En grados) del canal especificado.
        """
        if chanV < 1 or chanV > self.numcanales or chanI < 1 or chanI > self.numcanales or chanV == chanI:
            raise ValueError("Número de canal no válido")
        
        V = self.MedirVrms(chanV)
        I = self.MedirVrms(chanI)
        fase = self.MedirFase(chanV, chanI)
        P = V * I/0.2 * np.cos(np.deg2rad(fase))
        return P, V, I, fase
    
    def MedirPotencia(self, chanV: int, chanI: int) -> float:
        """
        Mide la potencia del canal especificado en un osciloscopio.
            Args:
                chanV (int): Número del canal de voltaje (1 a numcanales).
                chanI (int): Número del canal de corriente (1 a numcanales).
            Raises:
                ValueError: Si los números de canal no son válidos.
            Returns:
                float: Valor de potencia (En W) del canal especificado.            
        """
        tuple = self.MedirPotenciaCompleta(chanV, chanI)
        return tuple[0]  # Retorna solo la potencia

    def __str__(self):
        """
        Devuelve una representación en cadena del osciloscopio.
            Returns:
                str: Información del osciloscopio.
        """
        if not self.conexion:
            self.connect()
        if not self.modelo:
            self.Identificar()
        return f"Osciloscopio ID: {self.id}\nModelo: {self.modelo}\nCanales: {self.numcanales}\n"

    def close(self):
        """
        Cierra la conexión con el osciloscopio.
        """
        if hasattr(self, 'conexion'):
            self.conexion.close()
            del self.conexion
        else:
            raise RuntimeError("No hay conexión abierta para cerrar.")
        
    def __del__(self):
        """
        Destructor para asegurar que la conexión se cierra al eliminar la instancia.
        """
        try:
            self.close()
            print("Osciloscopio eliminado y conexión cerrada.")
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")

    def __repr__(self):
            """
            Returns a string representation of the simulated.
                Returns:
                    str: Information of the simulated oscilloscope.
            """
            return self.__str__()
    

class SimulacionOsciloscopio:

    """
    Class to simulate the Osciloscopio for testing purposes.
    """
    def __init__(self, id: str, numcanales:int):
        super().__init__(id, numcanales)
        self.id = id
        self.numcanales
        self.modelo = "Simulacion"
        self.fresonancia = 35000 + rd.randint(-2500, 2500)
    
    def connect(self):
        """
        Simulates the conection to the scope.
        """
        pass

    def Identificar(self) -> str:
        """
        Simulates the identification of the scope.
            Returns:
                str: Modelo of the simulated scope.
        """
        return self.modelo
    
    def MedirVpp(self, chan: int) -> float:
        """
        Simulates the Vpp measurement.
            Args:
                chan (int): Number of the channel (1 to numcanales).
            Raises:
                ValueError: If the channel number is not valid.
            Returns:
                float: Simulated Vpp value (in V) for the specified channel.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        if(chan == 1):
            try:
                Vpp = vPulser1 * 12000 # type: ignore
            except:
                Vpp = 0
            if(chan == 2):
                try:
                    Vpp = vPulser2 * 12000
                except:
                    Vpp = 0
        return Vpp
    MedirVpp_Siglent = MedirVpp_Keysight = MedirVpp

    def MedirFase(self, chan1: int, chan2: int) -> float:
        """
        Simulates the phase measurement between two channels.
            Args:
                chan1 (int): Number of the first channel (1 to numcanales).
                chan2 (int): Number of the second channel (1 to numcanales).
            Raises:
                ValueError: If the channel numbers are not valid.
            Returns:
                float: Simulated phase value (in degrees) between the two specified channels.
        """
        if chan1 < 1 or chan1 > self.numcanales or chan2 < 1 or chan2 > self.numcanales or chan1 == chan2:
            raise ValueError("Número de canal no válido")
        
        fase = rd.uniform(-10, 10)
        return fase
    MedirFase_Siglent = MedirFase_Keysight = MedirFase

    def MedirFrecuencia(self, chan: int) -> float:
        """
        Simulates the frequency measurement of a specified channel.
            Args:
                chan (int): Number of the channel (1 to numcanales).
            Raises:
                ValueError: If the channel number is not valid.
            Returns:
                float: Simulated frequency value (in Hz) for the specified channel.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        if chan == 1:
            try:
                f = frec1
            except:
                frec1 = 0
        if chan == 2:
            try:
                f = frec2
            except:
                frec2 = 0
        
        # Simulated frequency based on resonance frequency
        return f
    MedirFrecuencia_Siglent = MedirFrecuencia_Keysight = MedirFrecuencia

    def MedirVrms(self, chan: int) -> float:
        """
        Simulates the Vrms measurement of a specified channel.
            Args:
                chan (int): Number of the channel (1 to numcanales).
            Raises:
                ValueError: If the channel number is not valid.
            Returns:
                float: Simulated Vrms value (in V) for the specified channel.
        """
        if chan < 1 or chan > self.numcanales:
            raise ValueError("Número de canal no válido")
        
        if chan == 1:
            try:
                Vrms = vPulser1 * 12000 *0.707 # type: ignore
            except:
                Vrms = 0
        if chan == 2:
            try:
                Vrms = vPulser2 * 12000 *0.707 # type: ignore
            except:
                Vrms = 0
        
        return Vrms
    MedirVrms_Siglent = MedirVrms_Keysight = MedirVrms
    
    def MedirPotenciaCompleta(self, chanV: int, chanI: int) -> float:
        """
        Simulates the power measurement.
            Args:
                chanV (int): Number of the voltage channel (1 to numcanales).
                chanI (int): Number of the current channel (1 to numcanales).
            Raises:
                ValueError: If the channel numbers are not valid.
            Returns:
                float: Simulated power value (in W) for the specified channel.
        """
        if chanV < 1 or chanV > self.numcanales or chanI < 1 or chanI > self.numcanales or chanV == chanI:
            raise ValueError("Número de canal no válido")
        
        # Simulated values for voltage and current
        try:
            if chanV == 1:
                V = vPulser1 * 12000 # type: ignore
            if chanV == 2:
                V = vPulser2 * 12000 # type: ignore
        except:
            V = 0
        try:
            if chanI == 1:
                I = (1 + rd.random()) / (1 + ((frec1 / (self.resonance_freq / (2 * self.q_factor))) ** 2)) # type: ignore
            if chanI == 2:
                I = (1 + rd.random()) / (1 + ((frec2 / (self.resonance_freq / (2 * self.q_factor))) ** 2)) # type: ignore
        except:
            I = 0
        
        fase = rd.uniform(-10, 10)
        P = V * I * np.cos(np.deg2rad(fase))
        return P, V, I, fase
    
    def MedirPotencia(self, chanV: int, chanI: int) -> float:
        """
        Simulates the power measurement.
            Args:
                chanV (int): Number of the voltage channel (1 to numcanales).
                chanI (int): Number of the current channel (1 to numcanales).
            Raises:
                ValueError: If the channel numbers are not valid.
            Returns:
                float: Simulated power value (in W) for the specified channel.
        """
        tuple = self.MedirPotenciaCompleta(chanV, chanI)
        return tuple[0]
    
    def __str__(self):
        """
        Returns a string representation of the simulated oscilloscope.
            Returns:
                str: Information of the simulated oscilloscope.
        """
        return f"Simulacion Osciloscopio ID: {self.id}\nModelo: {self.modelo}\nCanales: {self.numcanales}\nFrec. Resonancia: {self.fresonancia} Hz\n"
    
    def close(self):
        """
        Simulates closing the connection to the oscilloscope.
        """
        pass

    def __del__(self):
        """
        Destructor to ensure the connection is closed when the instance is deleted.
        """
        pass

    def __repr__(self):
        """
        Returns a string representation of the simulated oscilloscope.
            Returns:
                str: Information of the simulated oscilloscope.
        """
        return self.__str__()
    
