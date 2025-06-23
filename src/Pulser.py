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

    def Identificar(self) -> str:
        """
        Identifica el modelo del generador de pulsos.
            Returns:
                str: Modelo del generador de pulsos.
        """
        try:
            idn = self.conexion.query("*IDN?")
            if "Keysight" in idn:
                self.modelo = "Keysight"
            if "Siglent" in idn:
                self.modelo = "Siglent"
            if "Tektronix" in idn:
                self.modelo = "Tektronix"
            if "RS" in idn:
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
        
    def disable_output(self, canal: int = 1):
        """
        Deshabilita la salida del generador de pulsos.
            Args:
                canal (int): Número del canal (1 a nCanales).
        """
        comando = f"C{canal}:OUTP OFF"
        self.conexion.write(comando)

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
            print("Conexión cerrada.")
        else:
            print("No hay conexión abierta para cerrar.")

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
        self.close()
        print("Generador de pulsos eliminado y conexión cerrada.")