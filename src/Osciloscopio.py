import pyvisa

class Osciloscopio:
    def __init__(self, id: str, numcanales:int):
        self.id = id
        self.numcanales = numcanales
        self. modelo = None
        rm = pyvisa.ResourceManager()
        self.conexion = rm.open_resource(self.id)
        self.Identificar()


    def connect(self):
        rm = pyvisa.ResourceManager()
        self.conexion = rm.open_resource(self.id)
        return self.inst
    
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
            if "Siglent" in idn:
                self.modelo = "Siglent"
            if "Keysight" in idn:
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
        comando = f"MEASURE:VPP? CH{chan}"
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
    
    def MedirVpp(self, chan: int) -> float:
        """
        Mide el valor de Vpp del canal especificado en un osciloscopio.
            Args:
                chan (int): Número del canal (1 a numcanales).
            Raises:
                ValueError: Si el número de canal no es válido.
            Returns:
                float: Valor de Vpp (En V) del canal especificado.
        """
        if self.modelo == "Siglent":
            return self.MedirVpp_Siglent(chan)
        else:
            return self.MedirVpp_Keysight(chan)

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
        
        comando = f"MEASURE:PHASE? CH{chan1},CH{chan2}"
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
        if chan1 < 1 or chan1 > self.numcanales or chan2 < 1 or chan2 > self.numcanales:
            raise ValueError("Número de canal no válido")
        while(mok == 0):
            comando = f"C{chan1}-C{chan2}:MEAD? PHA"
            val = self.conexion.query(comando)
            _, valor_str = val.split(",")
            resultado = float(valor_str.strip("()degree \n\r\t"))
            if resultado == '****' or i < 10:
                i += 1
            else:
                if i >= 10:
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
        
        comando = f"MEASURE:FREQUENCY? CH{chan}"
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
        
        comando = f"MEASURE:VRMS? CH{chan}"
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
        return float(resultado.strip())

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
        except Exception as e:
            print(f"Error al cerrar la conexión: {e}")