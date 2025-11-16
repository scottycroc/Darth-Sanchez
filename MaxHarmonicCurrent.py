"""
Full interactive script for harmonic current calculations with THD.
Features:
- CLI and GUI modes
- Manual input or CSV import for harmonic spectrum
- Series and shunt configurations
- THD calculation for voltage and current
- Save THD values in CSV output
- Generate plots (current, voltage, combined) and save as PNG and JSON
- Display THD in CLI and GUI outputs
"""

import pandas as pd
import plotly.graph_objects as go
import tkinter as tk
from tkinter import filedialog, messagebox
import sys
import math

# ---------------- Utility Functions ---------------- #

def calculate_impedances(fundamental_freq, harmonic, C, L, R):
    f_h = harmonic * fundamental_freq
    X_C = 1 / (2 * math.pi * f_h * C) if C > 0 else float('inf')
    X_L = 2 * math.pi * f_h * L if L > 0 else 0
    return X_C, X_L, R

def calculate_series_current(V_h, X_C, X_L, R):
    Z = complex(R, (X_L - X_C))
    return V_h / abs(Z)

def calculate_shunt_currents(V_h, X_C, X_L, R):
    I_C = V_h / X_C if X_C != float('inf') else 0
    I_L = V_h / X_L if X_L != 0 else 0
    I_R = V_h / R if R != 0 else 0
    return I_C, I_L, I_R

def calculate_thd(values):
    if len(values) < 2:
        return 0.0
    fundamental = values[0]
    harmonics = values[1:]
    numerator = math.sqrt(sum(v**2 for v in harmonics))
    return (numerator / fundamental) * 100 if fundamental != 0 else 0.0

def generate_plots(df, config):
    # Current Spectrum Plot
    fig_current = go.Figure()
    fig_current.add_trace(go.Bar(x=df['Harmonic'], y=df['Series Current (A)'], name='Series Current'))
    fig_current.update_layout(title='Current Spectrum', xaxis_title='Harmonic', yaxis_title='Current (A)')
    fig_current.write_image('current_spectrum.png')
    fig_current.write_json('current_spectrum.json')

    # Voltage Spectrum Plot
    fig_voltage = go.Figure()
    fig_voltage.add_trace(go.Bar(x=df['Harmonic'], y=df['Voltage (V)'], name='Voltage'))
    fig_voltage.update_layout(title='Voltage Spectrum', xaxis_title='Harmonic', yaxis_title='Voltage (V)')
    fig_voltage.write_image('voltage_spectrum.png')
    fig_voltage.write_json('voltage_spectrum.json')

    # Combined Plot
    fig_combined = go.Figure()
    fig_combined.add_trace(go.Bar(x=df['Harmonic'], y=df['Voltage (V)'], name='Voltage', yaxis='y'))
    fig_combined.add_trace(go.Bar(x=df['Harmonic'], y=df['Series Current (A)'], name='Current', yaxis='y2'))
    fig_combined.update_layout(
        title='Voltage and Current Spectrum',
        xaxis=dict(title='Harmonic'),
        yaxis=dict(title='Voltage (V)', side='left'),
        yaxis2=dict(title='Current (A)', overlaying='y', side='right'),
        barmode='group'
    )
    fig_combined.write_image('voltage_current_spectrum.png')
    fig_combined.write_json('voltage_current_spectrum.json')

# ---------------- Core Calculation ---------------- #

def process_data(fundamental_freq, C, L, R, harmonics, voltages, config):
    data = []
    series_currents = []
    for h, V_h in zip(harmonics, voltages):
        X_C, X_L, R_val = calculate_impedances(fundamental_freq, h, C, L, R)
        series_current = calculate_series_current(V_h, X_C, X_L, R_val)
        series_currents.append(series_current)
        if config == 'shunt':
            I_C, I_L, I_R = calculate_shunt_currents(V_h, X_C, X_L, R_val)
        else:
            I_C, I_L, I_R = series_current, series_current, series_current
        data.append([h, V_h, series_current, I_C, I_L, I_R])

    df = pd.DataFrame(data, columns=['Harmonic', 'Voltage (V)', 'Series Current (A)', 'Current C (A)', 'Current L (A)', 'Current R (A)'])
    # Calculate THD
    voltage_thd = calculate_thd(voltages)
    current_thd = calculate_thd(series_currents)
    df.loc[len(df)] = ['THD (%)', voltage_thd, current_thd, '', '', '']
    return df, voltage_thd, current_thd

# ---------------- CLI Mode ---------------- #

def cli_mode():
    print("=== Harmonic Calculator (CLI Mode) ===")
    fundamental_freq = float(input("Enter fundamental frequency (Hz): "))
    C = float(input("Enter capacitance (F): "))
    L = float(input("Enter inductance (H): "))
    R = float(input("Enter resistance (Ohms): "))
    config = input("Enter configuration (series/shunt): ").strip().lower()
    input_method = input("Enter 'manual' or 'csv' for harmonic spectrum input: ").strip().lower()

    harmonics = []
    voltages = []
    if input_method == 'manual':
        n = int(input("Enter number of harmonics: "))
        for _ in range(n):
            h = int(input("Harmonic order: "))
            v = float(input("Voltage (V): "))
            harmonics.append(h)
            voltages.append(v)
    elif input_method == 'csv':
        csv_path = input("Enter CSV file path: ")
        df_csv = pd.read_csv(csv_path)
        harmonics = df_csv['Harmonic'].tolist()
        voltages = df_csv['Voltage'].tolist()
    else:
        print("Invalid input method.")
        return

    df, v_thd, i_thd = process_data(fundamental_freq, C, L, R, harmonics, voltages, config)
    df.to_csv('harmonic_results.csv', index=False)
    generate_plots(df, config)
    print(f"Results saved to harmonic_results.csv")
    print(f"Voltage THD: {v_thd:.2f}%")
    print(f"Current THD: {i_thd:.2f}%")

# ---------------- GUI Mode ---------------- #

def gui_mode():
    def browse_csv():
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)

    def calculate():
        try:
            fundamental_freq = float(freq_entry.get())
            C = float(c_entry.get())
            L = float(l_entry.get())
            R = float(r_entry.get())
            config = config_var.get()
            harmonics = []
            voltages = []
            if input_var.get() == 'csv':
                csv_path = csv_entry.get()
                df_csv = pd.read_csv(csv_path)
                harmonics = df_csv['Harmonic'].tolist()
                voltages = df_csv['Voltage'].tolist()
            else:
                messagebox.showinfo("Info", "Manual input via GUI not implemented. Use CSV option.")
                return

            df, v_thd, i_thd = process_data(fundamental_freq, C, L, R, harmonics, voltages, config)
            df.to_csv('harmonic_results.csv', index=False)
            generate_plots(df, config)
            messagebox.showinfo("Results", f"Results saved to harmonic_results.csv\nVoltage THD: {v_thd:.2f}%\nCurrent THD: {i_thd:.2f}%")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    root = tk.Tk()
    root.title("Harmonic Calculator")

    tk.Label(root, text="Fundamental Frequency (Hz):").grid(row=0, column=0)
    freq_entry = tk.Entry(root)
    freq_entry.grid(row=0, column=1)

    tk.Label(root, text="Capacitance (F):").grid(row=1, column=0)
    c_entry = tk.Entry(root)
    c_entry.grid(row=1, column=1)

    tk.Label(root, text="Inductance (H):").grid(row=2, column=0)
    l_entry = tk.Entry(root)
    l_entry.grid(row=2, column=1)

    tk.Label(root, text="Resistance (Ohms):").grid(row=3, column=0)
    r_entry = tk.Entry(root)
    r_entry.grid(row=3, column=1)

    tk.Label(root, text="Configuration:").grid(row=4, column=0)
    config_var = tk.StringVar(value='series')
    tk.OptionMenu(root, config_var, 'series', 'shunt').grid(row=4, column=1)

    tk.Label(root, text="Input Method:").grid(row=5, column=0)
    input_var = tk.StringVar(value='csv')
    tk.OptionMenu(root, input_var, 'csv').grid(row=5, column=1)

    tk.Label(root, text="CSV File:").grid(row=6, column=0)
    csv_entry = tk.Entry(root)
    csv_entry.grid(row=6, column=1)
    tk.Button(root, text="Browse", command=browse_csv).grid(row=6, column=2)

    tk.Button(root, text="Calculate", command=calculate).grid(row=7, column=0, columnspan=3)

    root.mainloop()

# ---------------- Main ---------------- #

if __name__ == "__main__":
    print("Select mode:")
    print("1. CLI")
    print("2. GUI")
    choice = input("Enter choice (1/2): ").strip()
    if choice == '1':
        cli_mode()
    elif choice == '2':
        gui_mode()
    else:
        print("Invalid choice.")