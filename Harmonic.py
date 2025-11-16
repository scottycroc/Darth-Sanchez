import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def c_type_filter_voltages(harmonics, V_harmonics, L, C1, C2, R, f_base=50):
    """
    Calculate voltages and currents for a C-type harmonic filter, including phase angles.
    """
    results = []

    for h, V in zip(harmonics, V_harmonics):
        f = h * f_base
        omega = 2 * np.pi * f
        
        # Impedances
        Z_L = 1j * omega * L
        Z_C1 = 1 / (1j * omega * C1)
        Z_C2 = 1 / (1j * omega * C2)
        Z_R = R
        
        # Damping branch impedance (R + C2 in series)
        Z_branch = Z_R + Z_C2
        
        # Parallel combination of C1 and damping branch
        Z_parallel = 1 / (1/Z_C1 + 1/Z_branch)
        
        # Total impedance: L in series with parallel network
        Z_total = Z_L + Z_parallel
        
        # Source current
        I_source = V / Z_total
        
        # Node voltage
        V_node = V - I_source * Z_L
        
        # Branch currents
        I_C1 = V_node / Z_C1
        I_branch = V_node / Z_branch
        
        # Voltages across components
        V_L = I_source * Z_L
        V_C1 = V_node
        V_R = I_branch * Z_R
        V_C2 = I_branch * Z_C2
        
        # Helper for magnitude and angle
        def mag_angle(x):
            return abs(x), np.angle(x, deg=True)
        
        results.append({
            "Harmonic": h,
            "Frequency (Hz)": f,
            "V_source_mag": abs(V),
            "I_source_mag": mag_angle(I_source)[0],
            "I_source_angle": mag_angle(I_source)[1],
            "V_L_mag": mag_angle(V_L)[0],
            "V_L_angle": mag_angle(V_L)[1],
            "V_C1_mag": mag_angle(V_C1)[0],
            "V_C1_angle": mag_angle(V_C1)[1],
            "V_R_mag": mag_angle(V_R)[0],
            "V_R_angle": mag_angle(V_R)[1],
            "V_C2_mag": mag_angle(V_C2)[0],
            "V_C2_angle": mag_angle(V_C2)[1],
            "I_C1_mag": mag_angle(I_C1)[0],
            "I_C1_angle": mag_angle(I_C1)[1],
            "I_branch_mag": mag_angle(I_branch)[0],
            "I_branch_angle": mag_angle(I_branch)[1]
        })
    
    return pd.DataFrame(results)

# Example usage
harmonics = [1, 3, 5, 7]
V_harmonics = [230, 10, 5, 3]
L = 0.01      # H
C1 = 100e-6   # F
C2 = 50e-6    # F
R = 0.5       # Ohms

df = c_type_filter_voltages(harmonics, V_harmonics, L, C1, C2, R)

# Export to Excel
df.to_excel("c_type_filter_results.xlsx", index=False)

# Plot voltages
plt.figure(figsize=(10,6))
plt.plot(df["Harmonic"], df["V_L_mag"], label="V_L")
plt.plot(df["Harmonic"], df["V_C1_mag"], label="V_C1")
plt.plot(df["Harmonic"], df["V_R_mag"], label="V_R")
plt.plot(df["Harmonic"], df["V_C2_mag"], label="V_C2")
plt.xlabel("Harmonic Order")
plt.ylabel("Voltage Magnitude (V)")
plt.title("Voltages Across Components")
plt.legend()
plt.grid(True)
plt.show()

# Plot currents
plt.figure(figsize=(10,6))
plt.plot(df["Harmonic"], df["I_source_mag"], label="I_source")
plt.plot(df["Harmonic"], df["I_C1_mag"], label="I_C1")
plt.plot(df["Harmonic"], df["I_branch_mag"], label="I_branch")
plt.xlabel("Harmonic Order")
plt.ylabel("Current Magnitude (A)")
plt.title("Currents in Filter")
plt.legend()
plt.grid(True)
plt.show()