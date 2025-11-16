import streamlit as st
import pandas as pd
import math
from io import BytesIO
import matplotlib.pyplot as plt

# Actual BS 7671 cable tables for sizes up to 1000 mm²
cable_table = {
    'PVC_Single': {
        'C': {1.0: 14, 1.5: 18, 2.5: 24, 4: 32, 6: 41, 10: 57, 16: 76, 25: 101, 35: 125, 50: 150, 70: 192, 95: 232, 120: 269, 150: 309, 185: 356, 240: 415, 300: 476, 400: 546, 500: 615, 630: 700, 800: 780, 1000: 850},
        'D': {1.0: 13, 1.5: 16, 2.5: 21, 4: 28, 6: 36, 10: 50, 16: 66, 25: 87, 35: 106, 50: 130, 70: 167, 95: 202, 120: 234, 150: 270, 185: 310, 240: 360, 300: 410, 400: 470, 500: 530, 630: 600, 800: 670, 1000: 730}
    },
    'PVC_Multicore': {
        'C': {1.0: 13, 1.5: 16, 2.5: 21, 4: 28, 6: 36, 10: 50, 16: 66, 25: 87, 35: 106, 50: 130, 70: 167, 95: 202, 120: 234, 150: 270, 185: 310, 240: 360, 300: 410, 400: 470, 500: 530, 630: 600, 800: 670, 1000: 730},
        'D': {1.0: 12, 1.5: 15, 2.5: 19, 4: 26, 6: 34, 10: 47, 16: 62, 25: 82, 35: 100, 50: 123, 70: 155, 95: 188, 120: 218, 150: 250, 185: 285, 240: 330, 300: 375, 400: 430, 500: 480, 630: 540, 800: 600, 1000: 650}
    },
    'XLPE_Single': {
        'C': {1.0: 16, 1.5: 20, 2.5: 27, 4: 36, 6: 46, 10: 63, 16: 85, 25: 113, 35: 141, 50: 170, 70: 215, 95: 260, 120: 300, 150: 345, 185: 395, 240: 460, 300: 520, 400: 600, 500: 680, 630: 770, 800: 850, 1000: 930},
        'D': {1.0: 15, 1.5: 19, 2.5: 25, 4: 33, 6: 42, 10: 58, 16: 78, 25: 103, 35: 128, 50: 155, 70: 195, 95: 235, 120: 270, 150: 310, 185: 355, 240: 410, 300: 465, 400: 530, 500: 590, 630: 660, 800: 730, 1000: 800}
    },
    'XLPE_Multicore': {
        'C': {1.0: 15, 1.5: 19, 2.5: 25, 4: 33, 6: 42, 10: 58, 16: 78, 25: 103, 35: 128, 50: 155, 70: 195, 95: 235, 120: 270, 150: 310, 185: 355, 240: 410, 300: 465, 400: 530, 500: 590, 630: 660, 800: 730, 1000: 800},
        'D': {1.0: 14, 1.5: 18, 2.5: 24, 4: 31, 6: 40, 10: 55, 16: 74, 25: 98, 35: 122, 50: 148, 70: 185, 95: 222, 120: 255, 150: 290, 185: 330, 240: 380, 300: 430, 400: 490, 500: 540, 630: 600, 800: 660, 1000: 720}
    }
}

# Voltage drop tables updated for extended sizes (mV/A/m)
voltage_drop_table_single = {1.0: 44, 1.5: 29, 2.5: 18, 4: 11, 6: 7.3, 10: 4.4, 16: 2.8, 25: 1.75, 35: 1.25, 50: 0.95, 70: 0.68, 95: 0.52, 120: 0.42, 150: 0.36, 185: 0.32, 240: 0.27, 300: 0.23, 400: 0.20, 500: 0.18, 630: 0.16, 800: 0.14, 1000: 0.12}
voltage_drop_table_three = {1.0: 38, 1.5: 25, 2.5: 15, 4: 9.5, 6: 6.4, 10: 3.8, 16: 2.4, 25: 1.5, 35: 1.1, 50: 0.85, 70: 0.61, 95: 0.47, 120: 0.38, 150: 0.33, 185: 0.29, 240: 0.25, 300: 0.21, 400: 0.18, 500: 0.16, 630: 0.14, 800: 0.12, 1000: 0.10}

    
max_zs_table = {
    'MCB_B': 1.15, 'MCB_C': 0.57, 'MCB_D': 0.38,
    'Fuse_BS88': 0.8, 'Fuse_BS1361': 0.6
}

# Standard protective device ratings
standard_ratings = [6, 10, 16, 20, 25, 32, 40, 50, 63, 80, 100]

# Earth conductor sizing (simplified ratio method)
def earth_conductor_size(line_size):
    if line_size <= 16:
        return line_size
    elif line_size <= 35:
        return 16
    else:
        return line_size / 2

# Time-current curve approximations
def disconnection_time(device_type, fault_current, rating):
    if device_type.startswith('MCB'):
        if device_type == 'MCB_B': multiplier = 4
        elif device_type == 'MCB_C': multiplier = 7
        else: multiplier = 15
        return 0.1 if fault_current >= multiplier * rating else 5.0
    else:
        return 0.2 if fault_current >= 10 * rating else 5.0

def required_disconnection_time(rating):
    return 0.4 if rating <= 32 else 5.0

# Streamlit UI
st.title("BS 7671 Cable Sizing Tool with Auto Adjustment and Compliance Indicators")

# Inputs
power = st.number_input("Power (kW)", min_value=0.0, value=5.0)
voltage = st.number_input("Voltage (V)", min_value=0.0, value=230.0)
pf = st.number_input("Power Factor", min_value=0.1, max_value=1.0, value=1.0)
length = st.number_input("Cable Length (m)", min_value=0.0, value=10.0)
phase = st.selectbox("Phase", ["Single", "Three"])
cable_type = st.selectbox("Cable Type", ["PVC", "XLPE"])

construction = st.selectbox("Cable Construction", ["Single-core", "Multicore"])

# Determine cable key
cable_key = f"{cable_type}_{'Single' if construction == 'Single-core' else 'Multicore'}"

method = st.selectbox("Installation Method", ["C", "D", "E", "F"])
device_type = st.selectbox("Device Type", ["MCB_B", "MCB_C", "MCB_D", "Fuse_BS88", "Fuse_BS1361"])
ambient_temp = st.number_input("Ambient Temperature (°C)", min_value=0, value=30)
num_circuits = st.number_input("Number of Circuits Grouped", min_value=1, value=1)
insulation_length = st.number_input("Length in Thermal Insulation (mm)", min_value=0, value=0)
Cs = st.number_input("Soil Thermal Resistivity Factor (Cs)", min_value=0.1, value=1.0)
Cd = st.number_input("Depth of Laying Factor (Cd)", min_value=0.1, value=1.0)

# Lookup tables for Ca based on cable type
ca_table_pvc = {25:1.03, 30:1.00, 35:0.94, 40:0.87, 45:0.79, 50:0.71}
ca_table_xlpe = {25:1.02, 30:1.00, 35:0.96, 40:0.91, 45:0.87, 50:0.82}
Ca = ca_table_pvc.get(ambient_temp, 1.0) if cable_type == "PVC" else ca_table_xlpe.get(ambient_temp, 1.0)

# Grouping factor (Cg)
cg_table = {1:1.00, 2:0.80, 3:0.70, 4:0.65, 5:0.60, 6:0.57}
Cg = cg_table.get(num_circuits, 0.57)

# Thermal insulation factor (Ci)
if insulation_length <= 50:
    Ci = 0.89
elif insulation_length <= 100:
    Ci = 0.81
elif insulation_length <= 200:
    Ci = 0.68
elif insulation_length <= 400:
    Ci = 0.55
else:
    Ci = 0.50
fault_current = st.number_input("Fault Current (A)", min_value=0.0, value=500.0)
Ze = st.number_input("External Earth Impedance (Ze) Ω", min_value=0.0, value=0.35)

# Cable size dropdown with Auto option
sizes = sorted(cable_table[cable_key][method].keys())
user_size = st.selectbox("Cable Size (mm²)", ["Auto"] + [str(s) for s in sizes])

if st.button("Calculate"):
    # Design current
    Ib = (power * 1000) / (voltage * pf) if phase == 'Single' else (power * 1000) / (math.sqrt(3) * voltage * pf)

    # Auto-select protective device rating
    rating = next((r for r in standard_ratings if r >= Ib), max(standard_ratings))

    # Required Iz
    correction = Ca * Cg * Ci * Cs * Cd
    required_Iz = rating / correction

    # Initialize variables
    selected_size = None
    capacity = None
    earth_size = None
    vd_ok = Zs_ok = sc_ok = earth_sc_ok = time_ok = False
    vd = Zs_calc = sc_required_size = actual_time = required_time = 0.0

    if user_size != "Auto":
        # User-selected size
        selected_size = float(user_size)
        capacity = cable_table[cable_key][method][selected_size]
        earth_size = earth_conductor_size(selected_size)

        # Compliance checks
        vd_mV = voltage_drop_table_single[selected_size] if phase == 'Single' else voltage_drop_table_three[selected_size]
        vd = (vd_mV * Ib * length / 1000) if phase == 'Single' else (math.sqrt(3) * vd_mV * Ib * length / 1000)
        vd_limit = voltage * 0.05
        vd_ok = vd <= vd_limit

        R_line = 0.018 * length / selected_size
        R_earth = 0.018 * length / earth_size
        Zs_calc = Ze + R_line + R_earth
        Zs_ok = Zs_calc <= max_zs_table[device_type]

        k = 115
        sc_required_size = math.sqrt(fault_current**2 * 0.4) / k
        sc_ok = selected_size >= sc_required_size
        earth_sc_ok = earth_size >= sc_required_size

        actual_time = disconnection_time(device_type, fault_current, rating)
        required_time = required_disconnection_time(rating)
        time_ok = actual_time <= required_time

        # Warning if fails compliance
        failed_checks = []
        if not vd_ok: failed_checks.append("Voltage Drop")
        if not Zs_ok: failed_checks.append("Zs")
        if not sc_ok: failed_checks.append("Short-Circuit (Line)")
        if not earth_sc_ok: failed_checks.append("Short-Circuit (Earth)")
        if not time_ok: failed_checks.append("Disconnection Time")
        if capacity < required_Iz: failed_checks.append("Iz Compliance")

        if failed_checks:
            st.error("⚠ The following checks failed: " + ", ".join(failed_checks))
        else:
            st.success("✅ All checks passed successfully.")
    else:
        # Auto-adjust cable size until all checks pass
        for size in sizes:
            capacity = cable_table[cable_key][method][size]
            earth_size = earth_conductor_size(size)

            if capacity < required_Iz:
                continue

            vd_mV = voltage_drop_table_single[size] if phase == 'Single' else voltage_drop_table_three[size]
            vd = (vd_mV * Ib * length / 1000) if phase == 'Single' else (math.sqrt(3) * vd_mV * Ib * length / 1000)
            vd_limit = voltage * 0.05
            vd_ok = vd <= vd_limit

            R_line = 0.018 * length / size
            R_earth = 0.018 * length / earth_size
            Zs_calc = Ze + R_line + R_earth
            Zs_ok = Zs_calc <= max_zs_table[device_type]

            k = 115
            sc_required_size = math.sqrt(fault_current**2 * 0.4) / k
            sc_ok = size >= sc_required_size
            earth_sc_ok = earth_size >= sc_required_size

            actual_time = disconnection_time(device_type, fault_current, rating)
            required_time = required_disconnection_time(rating)
            time_ok = actual_time <= required_time

            if vd_ok and Zs_ok and sc_ok and earth_sc_ok and time_ok:
                selected_size = size
                break

    # Results
    st.subheader("Results")
    st.write(f"**Design Current (Ib):** {Ib:.2f} A")
    st.write(f"**Auto-selected Protective Device Rating (It):** {rating} A")
    st.write(f"**Required Iz:** {required_Iz:.2f} A")
    st.write(f"**Ca (Ambient Temp):** {Ca}, **Cg (Grouping):** {Cg}, **Ci (Insulation):** {Ci}, **Cs (Soil):** {Cs}, **Cd (Depth):** {Cd}")
    st.write(f"**Combined Correction Factor:** {correction:.2f}")
    st.write(f"**External Earth Impedance (Ze):** {Ze} Ω")
    st.write(f"**Selected Cable Size:** {selected_size} mm² (Capacity: {capacity} A)")
    st.write(f"**Earth Conductor Size:** {earth_size} mm²")

    # Compliance checks with tooltips
    checks = [
        ("Voltage Drop", vd_ok, "Ensures voltage drop ≤ 5% of nominal voltage."),
        ("Zs", Zs_ok, "Verifies earth fault loop impedance ≤ max allowed for device."),
        ("Short-Circuit (Line)", sc_ok, "Checks line conductor withstands fault current."),
        ("Short-Circuit (Earth)", earth_sc_ok, "Checks earth conductor withstands fault current."),
        ("Disconnection Time", time_ok, "Device must disconnect within required time."),
        ("Iz Compliance", capacity >= required_Iz, "Cable current-carrying capacity ≥ required Iz.")
    ]

    st.subheader("Compliance Checks")
    for name, status, tip in checks:
        badge = "✅ Pass" if status else "❌ Fail"
        html = f"<span title='{tip}'><strong>{name}:</strong> {badge}</span>"
        st.markdown(html, unsafe_allow_html=True)


    # Plot curves
    st.subheader("Time-Current Curves for MCB Types B, C, D")
    currents = [rating * x for x in range(1, 21)]
    times_B = [100/(c/rating) for c in currents]
    times_C = [200/(c/rating) for c in currents]
    times_D = [400/(c/rating) for c in currents]

    fig, ax = plt.subplots()
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.plot(currents, times_B, label='Type B', color='blue')
    ax.plot(currents, times_C, label='Type C', color='orange')
    ax.plot(currents, times_D, label='Type D', color='green')

    color_marker = 'green' if time_ok else 'red'
    ax.scatter(fault_current, actual_time, color=color_marker, s=100, label='Fault Current')
    ax.axhline(y=required_time, color='red', linestyle='--', label='Required Time')

    ax.set_xlabel('Current (A)')
    ax.set_ylabel('Time (s)')
    ax.set_title('Time-Current Curves (Log-Log)')
    ax.legend()
    st.pyplot(fig)

    # Excel export
    data = {
        'Power (kW)': power, 'Voltage (V)': voltage, 'PF': pf, 'Length (m)': length,
        'Phase': phase, 'Cable Type': cable_type, 'Install Method': method,
        'Device Type': device_type, 'Device Rating (A)': rating,
        'Fault Current (A)': fault_current, 'External Earth Impedance (Ze)': Ze, 'Cs (Soil)': Cs, 'Cd (Depth)': Cd,
        'Design Current (Ib)': Ib, 'Required Iz': required_Iz,
        'Cable Size': selected_size, 'Capacity': capacity,
        'Earth Size': earth_size,
        'Voltage Drop (V)': vd, 'VD OK': vd_ok,
        'Zs (Ω)': Zs_calc, 'Zs OK': Zs_ok,
        'SC Required Size (mm²)': sc_required_size, 'SC OK': sc_ok,
        'Earth SC OK': earth_sc_ok,
        'Disconnection Time (s)': actual_time, 'Time OK': time_ok
    }
    df = pd.DataFrame([data])

    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False)
    excel_data = output.getvalue()

    st.download_button(
        label="Download Results as Excel",
        data=excel_data,
        file_name="bs7671_results.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
