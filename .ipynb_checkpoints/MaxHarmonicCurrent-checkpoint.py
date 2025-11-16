import numpy as np

import pandas as pd

import plotly.express as px



# -----------------------------

# User Inputs

# -----------------------------

f1 = 50  # Fundamental frequency (Hz)

harmonics = [1, 3, 5, 7, 9, 11, 13, 15]  # Harmonic orders

voltages = [230, 10, 8, 6, 5, 4, 3, 2]   # Harmonic voltage spectrum (V RMS)

 

# Filter component values

C = 100e-6   # Capacitance in Farads (100 µF)

L = 0.01     # Inductance in Henry (10 mH)

R = 1        # Resistance in Ohms

 

# -----------------------------

# Calculations

# -----------------------------

results = []

 

for h, Vh in zip(harmonics, voltages):

    fh = h * f1  # harmonic frequency

    Zc = 1 / (1j * 2 * np.pi * fh * C)

    Zl = 1j * 2 * np.pi * fh * L

    Zr = R

   

    Ic = Vh / Zc

    Il = Vh / Zl

    Ir = Vh / Zr

   

    results.append({

        'Harmonic': h,

        'Frequency (Hz)': fh,

        'Voltage (V)': Vh,

        'I_C (A)': abs(Ic),

        'I_L (A)': abs(Il),

        'I_R (A)': abs(Ir)

    })

 

df = pd.DataFrame(results)

 

# -----------------------------

# Maximum Currents

# -----------------------------

max_Ic = df['I_C (A)'].max()

max_Il = df['I_L (A)'].max()

max_Ir = df['I_R (A)'].max()

 

print("Harmonic Current Spectrum:")

print(df)

print("\nMaximum Currents:")

print(f"Max I_C = {max_Ic:.4f} A")

print(f"Max I_L = {max_Il:.4f} A")

print(f"Max I_R = {max_Ir:.4f} A")

 

# -----------------------------

# Plot harmonic spectrum

# -----------------------------

fig = px.line(df, x='Harmonic', y=['I_C (A)', 'I_L (A)', 'I_R (A)'],

              markers=True,

              title='Harmonic Current Spectrum through C, L, R',

              labels={'value': 'Current (A)', 'Harmonic': 'Harmonic Order'},

              template='plotly_dark')