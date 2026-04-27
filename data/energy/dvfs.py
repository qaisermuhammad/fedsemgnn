def dvfs_scale(temp_c):
    # Return freq_scale in (0.5..1.0) based on temperature
    if temp_c < 70: return 1.0
    if temp_c < 80: return 0.9
    if temp_c < 90: return 0.75
    return 0.6
