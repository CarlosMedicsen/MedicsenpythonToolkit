import pyvisa

class Pulser:
    """
    Clase para controlar un generador de pulsos.
        Atributos:
            conexion (pyvisa.Resource): Objeto de conexión con el generador de pulsos.
            modelo (str): Modelo del generador de pulsos.
    """
    
    def __init__(self, direccion: str, nCanales: int):
        """
        Inicializa la conexión con el generador de pulsos.
            Args:
                direccion (str): Dirección VISA del generador de pulsos.
        """
        self.direccion = direccion
        self.nCanales = nCanales
        self.connect()
        self.modelo = None
        self.Identificar()
        self.amp1 = 0.25
        self.amp2 = 0.25
        self.output1 = False
        self.output2 = False

    def Identificar(self) -> str:
        """
        Identifica el modelo del generador de pulsos.
            Returns:
                str: Modelo del generador de pulsos.
        """
        try:
            idn = self.conexion.query("*IDN?")
            if "keysight" in idn.lower():
                self.modelo = "Keysight"
            if "siglent" in idn.lower():
                self.modelo = "Siglent"
            if "tektronix" in idn.lower():
                self.modelo = "Tektronix"
            if "rs" in idn.lower():
                self.modelo = "RS"
            else:
                self.modelo = "Desconocido"
                print("Modelo de generador de pulsos no reconocido.")
        except pyvisa.VisaIOError as e:
            raise RuntimeError(f"Error al identificar el generador de pulsos: {e}")
        
    def connect(self):
        """
        Establece la conexión con el generador de pulsos.
            Returns:
                pyvisa.Resource: Objeto de conexión con el generador de pulsos.
        """
        rm = pyvisa.ResourceManager()
        self.conexion = rm.open_resource(self.direccion)
        return self.conexion
    
    def set_frecuencia(self, frecuencia: float, canal: int = 1):
        """
        Establece la frecuencia del generador de pulsos.
            Args:
                frecuencia (float): Frecuencia en Hz.
        """
        comando = f"C{canal}:BSWV FRQ,{frecuencia}"
        self.conexion.write(comando)
    
    def set_amplitud(self, amplitud: float, canal: int = 1):
        """
        Establece la amplitud del generador de pulsos.
            Args:
                amplitud (float): Amplitud en V.
        """
        if amplitud > 0.8:
            raise ValueError("La amplitud no puede ser mayor a 0.8 V.")
        
        comando = f"C{canal}:BSWV AMP,{amplitud}"
        self.conexion.write(comando)

        if canal == 1:
            self.amp1 = amplitud
        if canal == 2:
            self.amp2 = amplitud

    def set_offset(self, offset: float, canal: int = 1):
        """
        Establece el offset del generador de pulsos.
            Args:
                offset (float): Offset en V.
        """
        comando = f"C{canal}:BSWV OFS,OFS{offset}"
        self.conexion.write(comando)
    
    def enable_output(self, canal: int = 1):
        """
        Habilita la salida del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
        """
        comando = f"C{canal}:OUTP ON"
        self.conexion.write(comando)
        self.output1 = True if canal == 1 else self.output1
        self.output2 = True if canal == 2 else self.output2
    output_on = enable_output
        
    def disable_output(self, canal: int = 1):
        """
        Deshabilita la salida del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
        """
        comando = f"C{canal}:OUTP OFF"
        self.conexion.write(comando)
    output_off = disable_output

    def output_impedance(self, impedancia: float, canal: int = 1):
        """
        Establece la impedancia de salida del generador de pulsos.
            Args:
                impedancia (float): Impedancia en ohmios.
        """
        comando = f"C{canal}:OUTP Z,{impedancia}"
        self.conexion.write(comando)
    
    def get_frecuencia(self, canal: int = 1) -> float:
        """
        Obtiene la frecuencia del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
            Returns:
                float: Frecuencia en Hz.
        """
        comando = f"C{canal}:BSWV FRQ?"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())
    
    def get_amplitud(self, canal: int = 1) -> float:
        """
        Obtiene la amplitud del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
            Returns:
                float: Amplitud en V.
        """
        comando = f"C{canal}:BSWV AMP?"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())

    def get_offset(self, canal: int = 1) -> float:
        """
        Obtiene el offset del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
            Returns:
                float: Offset en V.
        """
        comando = f"C{canal}:BSWV OFS?"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())
    
    def get_output_impedance(self, canal: int = 1) -> float:
        """
        Obtiene la impedancia de salida del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
            Returns:
                float: Impedancia en ohmios.
        """
        comando = f"C{canal}:OUTP Z?"
        resultado = self.conexion.query(comando)
        return float(resultado.strip())
    
    def close(self):
        """
        Cierra la conexión con el generador de pulsos.
        """
        if self.conexion:

            self.conexion.close()
            self.conexion = None
        else:
            print("No hay conexión abierta para cerrar.")

    def __enter__(self):
        """
        Método para usar el generador de pulsos como un contexto.
            Returns:
                Pulser: Instancia del generador de pulsos.
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Método para cerrar la conexión al salir del contexto.
            Args:
                exc_type: Tipo de excepción.
                exc_value: Valor de la excepción.
                traceback: Traza de la excepción.
        """
        if self.output1:
            self.disable_output(1)
        if self.output2:
            self.disable_output(2)
        self.close()

    def __str__(self):
        """
        Devuelve una representación en cadena del generador de pulsos.
            Returns:
                str: Información del generador de pulsos.
        """
        if not self.conexion:
            self.connect()
        if not self.modelo:
            self.Identificar()
        return f"Generador de Pulsos ID: {self.direccion}\nModelo: {self.modelo}\nCanales: {self.nCanales}\n"
    
    def __del__(self):
        """
        Destructor para cerrar la conexión al eliminar el objeto.
        """
        try:
            if hasattr(self, 'conexion') and self.conexion is not None:
                if self.output1:
                    self.disable_output(1)
                if self.output2:
                    self.disable_output(2)

            self.close()
            print("Generador de pulsos eliminado y conexión cerrada.")
        except Exception as e:
            pass
        

class SimulacionPulser:
    """
    Class to simulate a pulse generator.
        Attributes:
            vPulser1 (float): Voltage of the channel1 of pulse generator.
            vPulser2 (float): Voltage of the channel2 of pulse generator.
    """
    def __init__(self, direccion: str, nCanales: int):
        """
        Initializes the pulse generator simulation.
            Args:
                vPulser1 (float): Voltage of the channel1 of pulse generator.
                vPulser2 (float): Voltage of the channel2 of pulse generator.
                output1 (bool): Output status of channel1.
                output2 (bool): Output status of channel2.
        """
        self.direccion = direccion
        self.nCanales = nCanales
        self.conexion = None
        self.modelo = "Simulacion"
        self.amp1 = 0.25
        self.amp2 = 0.25

        global vPulser1, vPulser2, output1, output2, frec1, frec2
        frec1 = 0
        frec2 = 0
        vPulser1 = 0.25
        vPulser2 = 0.25
        output1 = False 
        output2 = False

    def Identificar(self) -> str:
        """
        Identifica el modelo del generador de pulsos.
            Returns:
                str: Modelo del generador de pulsos.
        """
        self.modelo = "Simulacion"
        return self.modelo
        
    def connect(self):
        """
        Simulates the connection to the pulse generator.
            Returns:
                str: Connection status.
        """
        self.conexion = "Simulated Connection"
        return self.conexion

    def set_frecuencia(self, frecuencia: float, canal: int = 1):
        """
        Sets the frequency of the pulse generator.
            Args:
                frecuencia (float): Frequency in Hz.
        """
        global frec1, frec2
        if canal == 1:
            global frec1
            frec1 = frecuencia
        if canal == 2:
            global frec2
            frec2 = frecuencia
    
    def set_amplitud(self, amplitud: float, canal: int = 1):
        """
        Sets the amplitude of the pulse generator.
            Args:
                amplitud (float): Amplitude in V.
        """
        global vPulser1, vPulser2
        if canal == 1:
            global vPulser1
            vPulser1 = amplitud
            self.amp1 = amplitud
        if canal == 2:
            global vPulser2
            vPulser2 = amplitud
            self.amp2 = amplitud
    
    def set_offset(self, offset: float, canal: int = 1):
        """
        Sets the offset of the pulse generator.
            Args:
                offset (float): Offset in V.
        """
        # Not implemented in simulation, but can be added if needed.
        pass

    def enable_output(self, canal: int = 1):
        """
        Enables the output of the pulse generator.
            Args:
                canal (int): Channel number (1 to nCanales).
        """
        if canal == 1:
            global output1
            output1 = True
        if canal == 2:
            global output2
            output2 = True
    output_on = enable_output

    def disable_output(self, canal: int = 1):
        """
        Disables the output of the pulse generator.
            Args:
                canal (int): Channel number (1 to nCanales).
        """
        if canal == 1:
            global output1
            output1 = False
        if canal == 2:
            global output2
            output2 = False
    output_off = disable_output

    def get_frecuencia(self, canal: int = 1) -> float:
        """
        Gets the frequency of the pulse generator.
            Args:
                canal (int): Channel number (1 to nCanales).
            Returns:
                float: Frequency in Hz.
        """
        try:
            if canal == 1:
                return frec1
            if canal == 2:
                return frec2
        except:
            return 0.0
            
    def get_amplitud(self, canal: int = 1) -> float:
        """
        Gets the amplitude of the pulse generator.
            Args:
                canal (int): Channel number (1 to nCanales).
            Returns:
                float: Amplitude in V.
        """
        try:
            if canal == 1:
                return vPulser1
            if canal == 2:
                return vPulser2
        except:
            return 0.0
    
    def get_offset(self, canal: int = 1) -> float:
        """
        Gets the offset of the pulse generator.
            Args:
                canal (int): Channel number (1 to nCanales).
            Returns:
                float: Offset in V.
        """
        # Not implemented in simulation, but can be added if needed.
        return 0.0
    
    def get_output_impedance(self, canal: int = 1) -> float:
        """
        Gets the output impedance of the pulse generator.
            Args:
                canal (int): Channel number (1 to nCanales).
            Returns:
                float: Output impedance in ohms.
        """
        # Not implemented in simulation, but can be added if needed.
        return 50.0
    
    def __enter__(self):
        """
        Método para usar el generador de pulsos como un contexto.
            Returns:
                Pulser: Instancia del generador de pulsos.
        """
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        """
        Método para cerrar la conexión al salir del contexto.
            Args:
                exc_type: Tipo de excepción.
                exc_value: Valor de la excepción.
                traceback: Traza de la excepción.
        """
        if self.output1:
            self.disable_output(1)
        if self.output2:
            self.disable_output(2)
        self.close()

    def __str__(self):
        """
        Devuelve una representación en cadena del generador de pulsos.
            Returns:
                str: Información del generador de pulsos.
        """
        if not self.conexion:
            self.connect()
        if not self.modelo:
            self.Identificar()
        return f"Generador de Pulsos ID: {self.direccion}\nModelo: {self.modelo}\nCanales: {self.nCanales}\n"
    
    def __del__(self):
        """
        Destructor para cerrar la conexión al eliminar el objeto.
        """
        pass