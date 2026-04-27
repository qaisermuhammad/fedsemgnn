def cpu_power(util, p_state=1.0, p_idle=8.0, p_max=95.0):
    return p_idle + (p_max - p_idle) * (util**1.3) * p_state

def gpu_power(util, p_idle=15.0, p_max=280.0):
    return p_idle + (p_max - p_idle) * (util**1.1)
