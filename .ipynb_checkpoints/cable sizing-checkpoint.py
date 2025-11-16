import pandas as pd
import openpyxl

# Reference tables (simplified for demo)
correction_factors_temp = {25: 1.0, 30: 1.0, 35: 0.94, 40: 0.87}
grouping_factors = {1: 1.0, 2: 0.8, 3: 0.7, 4: 0.65, 5: 0.6}
insulation_factors = {"None": 1.0, "Thermal": 0.89}
voltage_drop_table = {"2.5mm²": 18, "4mm²": 11, "6mm²": 7.3, "10mm²": 4.4}
tabulated_current = {"2.5mm²": 27, "4mm²": 37, "6mm²": 47, "10mm²": 65}
max_zs_table = {"B32": 1.44, "B63": 0.73, "C32": 0.72, "C63": 0.36}  # Example values

def calculate_cable_sizing(row):
    # Extract input values
    power_kw = row['Power_kW']
    voltage = row['Voltage_V']
    pf = row['Power_Factor']
    cable_size = row['Cable_Size']
    length_m = row['Length_m']
    ambient_temp = row['Ambient_Temp']
    num_circuits = row['Num_Circuits']
    insulation_type = row['Insulation_Type']
    device_rating = row['Device_Rating']
    device_type = row['Device_Type']
    Ze = row['Ze']
    R1_R2 = row['R1_R2']
    
    # Load current (Ib)
    Ib = (power_kw * 1000) / (voltage * pf)
    
    # Correction factors
    Ca = correction_factors_temp.get(ambient_temp, 1.0)
    Cg = grouping_factors.get(num_circuits, 0.5)
    Ci = insulation_factors.get(insulation_type, 1.0)
    
    # Tabulated current and adjusted capacity
    It = tabulated_current.get(cable_size, 0)
    Iz = It * Ca * Cg * Ci
    
    # Voltage drop calculation
    mV_per_A_per_m = voltage_drop_table.get(cable_size, 0)
    Vdrop = (mV_per_A_per_m * Ib * length_m) / 1000
    
    # Zs calculation
    Zs = Ze + R1_R2
    max_zs = max_zs_table.get(device_type, 0)
    
    # Compliance check
    compliance = "PASS" if (Iz >= Ib and Iz >=, device_rating and Vdrop <= 5 a    nd Zs <= max_zs) else "FAIL"
        
    return {
            "Ib (A)":     round(Ib, 2),
            "Ca": Ca,
            "Cg": Cg,
        "Ci": Ci,
            "It (A)": It,
        "Iz (A)": roun    d(Iz, 2),
        "Voltage Drop     (V)": round(Vdrop, 2),
            "Zs (Ω)": round(Zs, 3),
     }        "ax Zs (Ω)": max_zs,
        "Compliance": compliC:\Users\scott\MyNew SC Folder\BS7671_Cable_Sizing_Input.xlsx"
# Read input file (Excel or CSV)
input_file = "circuits.xlsx"  # Change to your file path
df = pd.read_excel(input_file)  # or pd.read_csv("circuits.csv")

# Perform calculations for each row
results = []
for _, row in df.iterrows():
    results.append(calculate_cable_sizing(row))

# Combine results with original data
results_df = pd.concat([df, pd.DataFrame(results)], axis=1)

# Save to Excel
output_file = "Cable_Sizing_Report.xlsx"
results_df.to_excel(output_file, index=False)

print(f"Report generated: {output_file}")
