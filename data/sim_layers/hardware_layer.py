import random

def schedule_delay(util):  # util in [0,1]
    base = 0.2e-3  # 0.2 ms
    tail = random.lognormvariate(mu=-8, sigma=1.2)  # long-tail queuing
    return base + util * 0.6e-3 + tail

def phy_mac_jitter(snr_db):
    return max(0.0, random.gauss(0.3e-3, 0.2e-3) - snr_db*1e-5)

def thermal_throttle(temp_c):
    # return freq_scale in (0.5..1.0)
    if temp_c < 70: return 1.0
    if temp_c < 80: return 0.9
    if temp_c < 90: return 0.75
    return 0.6
