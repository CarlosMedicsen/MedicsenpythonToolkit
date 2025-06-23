class PID:
    """Controlador PID basico (Proporcional, Integral, Derivativo)."""

    def __init__(self, Kp, Ki, Kd, setpoint=0.0, max_output = float('inf')):
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
        
        self.previous_error = error
        
        return output
    def __str__(self):
        """
        Representación en cadena del objeto PID.
            Returns:
                str: Representación en cadena del objeto PID.
        """
        return f"--- Info PID --- \n - Kp={self.Kp},\n - Ki={self.Ki},\n - Kd={self.Kd},\n - setpoint={self.setpoint}, \n - max_output={self.max_output})"