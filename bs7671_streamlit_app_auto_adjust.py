import streamlit as st
import pandas as pd
import math
from io import BytesIO
import matplotlib.pyplot as plt

# BS 7671 simplified tables
cable_table = {
    'PVC': {'C': {2.5: 27, 4: 36, 6: 46, 10: 63}, 'D': {2.5: 24, 4: 32, 6: 41, 10: 57}},
    'XLPE': {'C': {2.5: 31, 4: 42, 6: 54, 10: 73}, 'D': {2.5: 28, 4: 38, 6: 49, 10: 67}}
}
voltage_drop_table = {2.5: 18, 4: 11, 6: 7.3, 10: 4.4}  # mV/A/m for single-phase
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
method = st.selectbox("Installation Method", ["C", "D"])
device_type = st.selectbox("Device Type", ["MCB_B", "MCB_C", "MCB_D", "Fuse_BS88", "Fuse_BS1361"])
Ca = st.number_input("Ambient Temp Factor (Ca)", min_value=0.1, value=1.0)
Cg = st.number_input("Grouping Factor (Cg)", min_value=0.1, value=1.0)
Ci = st.number_input("Insulation Factor (Ci)", min_value=0.1, value=1.0)
fault_current = st.number_input("Fault Current (A)", min_value=0.0, value=500.0)

if st.button("Calculate"):
    # Design current
    Ib = (power * 1000) / (voltage * pf) if phase == 'Single' else (power * 1000) / (math.sqrt(3) * voltage * pf)

    # Auto-select protective device rating
    rating = next((r for r in standard_ratings if r >= Ib), max(standard_ratings))

    # Required Iz
    correction = Ca * Cg * Ci
    required_Iz = rating / correction

    # Auto-adjust cable size until all checks pass
    sizes = sorted(cable_table[cable_type][method].keys())
    selected_size = None
    capacity = None
    earth_size = None
    vd_ok = Zs_ok = sc_ok = earth_sc_ok = time_ok = False

    for size in sizes:
        capacity = cable_table[cable_type][method][size]
        earth_size = earth_conductor_size(size)

        if capacity < required_Iz:
            continue

        vd_mV = voltage_drop_table[size]
        vd = (vd_mV * Ib * length / 1000) if phase == 'Single' else (math.sqrt(3) * vd_mV * Ib * length / 1000)
        vd_limit = voltage * 0.05
        vd_ok = vd <= vd_limit

        R_line = 0.018 * length / size
        R_earth = 0.018 * length / earth_size
        Zs_calc = 0.35 + R_line + R_earth
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

    # Indicators
    def indicator(ok): return "✅ Pass" if ok else "❌ Fail"

    st.subheader("Results")
    st.write(f"**Design Current (Ib):** {Ib:.2f} A")
    st.write(f"**Auto-selected Protective Device Rating (It):** {rating} A")
    st.write(f"**Required Iz:** {required_Iz:.2f} A")
    st.write(f"**Selected Cable Size:** {selected_size} mm² (Capacity: {capacity} A)")
    st.write(f"**Earth Conductor Size:** {earth_size} mm²")

    compliance_data = {
        "Check": ["Voltage Drop", "Zs", "Short-Circuit (Line)", "Short-Circuit (Earth)", "Disconnection Time", "Iz Compliance"],
        "Result": [indicator(vd_ok), indicator(Zs_ok), indicator(sc_ok), indicator(earth_sc_ok), indicator(time_ok), indicator(capacity >= required_Iz)]
    }
    st.table(pd.DataFrame(compliance_data))

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
        'Fault Current (A)': fault_current,
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
