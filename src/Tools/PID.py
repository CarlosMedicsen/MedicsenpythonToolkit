class PID:
    """Controlador PID basico (Proporcional, Integral, Derivativo)."""

    def __init__(self, Kp, Ki, Kd, setpoint=0.0, max_output = float('inf')):
        """
        Inicializa el controlador PID.
            Args:
                Kp (float): Ganancia proporcional.
                Ki (float): Ganancia integral.
                Kd (float): Ganancia derivativa.
                setpoint (float): Valor deseado al que se quiere llegar.
                max_output (float): Salida máxima permitida del controlador.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
        self.setpoint = setpoint
        self.max_output = max_output
        self.previous_error = 0.0
        self.integral = 0.0

    def update(self, measured_value, dt):
        """
        Actualiza el controlador PID con el valor medido y el intervalo de tiempo.
            Args:
                measured_value (float): Valor medido del sistema.
                dt (float): Intervalo de tiempo desde la última actualización.
            Returns:
                float: Salida del controlador PID, limitada por max_output.
        """
        error = self.setpoint - measured_value
        self.integral += error * dt
        derivative = (error - self.previous_error) / dt if dt > 0 else 0.0
        
        output = (self.Kp * error) + (self.Ki * self.integral) + (self.Kd * derivative)

        if output > self.max_output:
            output = self.max_output
        if output < -self.max_output:
            output = -self.max_output
        
        self.previous_error = error
        
        return output
    
    def set_setpoint(self, setpoint):
        """
        Establece el valor deseado al que se quiere llegar.
            Args:
                setpoint (float): Nuevo valor deseado.
        """
        self.setpoint = setpoint

    def set_gains(self, Kp, Ki, Kd):
        """
        Establece las ganancias del controlador PID.
            Args:
                Kp (float): Nueva ganancia proporcional.
                Ki (float): Nueva ganancia integral.
                Kd (float): Nueva ganancia derivativa.
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd
    
    def set_max_output(self, max_output):
        """
        Establece la salida máxima permitida del controlador.
            Args:
                max_output (float): Nuevo valor máximo de salida.
        """
        self.max_output = max_output

    def get_gains(self):
        """
        Obtiene las ganancias del controlador PID.
            Returns:
                tuple: (Kp, Ki, Kd)
        """
        return self.Kp, self.Ki, self.Kd
    
    def get_setpoint(self):
        """
        Obtiene el valor deseado al que se quiere llegar.
            Returns:
                float: Valor del setpoint.
        """
        return self.setpoint
    
    def get_max_output(self):
        """
        Obtiene la salida máxima permitida del controlador.
            Returns:
                float: Valor máximo de salida.
        """
        return self.max_output  
    
    def get_previous_error(self):
        """
        Obtiene el error previo del controlador PID.
            Returns:
                float: Valor del error previo.
        """
        return self.previous_error
    
    def get_integral(self):
        """
        Obtiene el valor integral acumulado del controlador PID.
            Returns:
                float: Valor de la integral.
        """
        return self.integral
        
    def reset(self):
        """
        Reinicia el controlador PID, reseteando el error previo y la integral.
        """
        self.previous_error = 0.0
        self.integral = 0.0

    def __str__(self):
        """
        Representación en cadena del objeto PID.
            Returns:
                str: Representación en cadena del objeto PID.
        """
        return f"--- Info PID --- \n - Kp={self.Kp},\n - Ki={self.Ki},\n - Kd={self.Kd},\n - setpoint={self.setpoint}, \n - max_output={self.max_output})"