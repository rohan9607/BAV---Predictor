"""
extract_comsol_data.py
Extracts data from your actual COMSOL CSV files
Place in: backend/comsol/
"""

import pandas as pd
import numpy as np

def extract_comsol_data():
    """
    Extract max values from your 3 COMSOL CSV files
    """
    print("="*80)
    print("🔬 EXTRACTING COMSOL DATA")
    print("="*80)
    
    results = {}
    
    # =============================================
    # 1. BLOOD VELOCITY FILE
    # =============================================
    print("\n📄 Reading L_blood_velo.csv...")
    try:
        # Skip metadata rows (first 5 rows)
        df_vel = pd.read_csv('L_blood_velo.csv', skiprows=5, header=None)
        
        # Columns based on your screenshot:
        # Column 0: V_in (m/f_in Hz) - ignore
        # Column 1: Time (s) - ignore  
        # Column 2: Time (s) - actual time
        # Column 3: Velocity magnitude (m/s)
        
        velocity_col = df_vel.iloc[:, 3]  # 4th column (index 3)
        velocity_col = pd.to_numeric(velocity_col, errors='coerce')
        max_velocity = velocity_col.max()
        
        print(f"✅ Success!")
        print(f"   Rows: {len(df_vel)}")
        print(f"   Max velocity: {max_velocity:.6f} m/s")
        
        # Calculate WSS (Wall Shear Stress)
        # WSS = μ × (dv/dy)
        # For rough estimate: WSS ≈ μ × velocity / boundary_layer_thickness
        # μ (blood) ≈ 0.004 Pa·s, boundary layer ≈ 0.001 m
        wss_estimate = (0.004 * max_velocity) / 0.001
        
        print(f"   Estimated WSS: {wss_estimate:.2f} Pa")
        results['peak_wss_pa'] = wss_estimate
        results['max_velocity_ms'] = max_velocity
        
    except Exception as e:
        print(f"❌ Error: {e}")
        results['peak_wss_pa'] = None
    
    # =============================================
    # 2. DISPLACEMENT FILE
    # =============================================
    print("\n📄 Reading L_displacement.csv...")
    try:
        # Skip metadata rows (first 5 rows)
        df_disp = pd.read_csv('L_displacement.csv', skiprows=5, header=None)
        
        # Columns based on your screenshot:
        # Column 0: Time (s)
        # Column 1: Displacement magnitude (mm)
        
        displacement_col = df_disp.iloc[:, 1]  # 2nd column
        displacement_col = pd.to_numeric(displacement_col, errors='coerce')
        max_displacement = displacement_col.max()
        
        print(f"✅ Success!")
        print(f"   Rows: {len(df_disp)}")
        print(f"   Max displacement: {max_displacement:.6f} mm")
        
        # Calculate strain
        # Strain = (displacement / original_length) × 100
        # Assuming wall thickness ≈ 2mm (typical aortic wall)
        wall_thickness = 2.0  # mm
        strain_percent = (max_displacement / wall_thickness) * 100
        
        print(f"   Calculated strain: {strain_percent:.2f}%")
        results['max_strain_percent'] = strain_percent
        results['max_displacement_mm'] = max_displacement
        
    except Exception as e:
        print(f"❌ Error: {e}")
        results['max_strain_percent'] = None
    
    # =============================================
    # 3. WALL STRESS FILE
    # =============================================
    print("\n📄 Reading L_wall_stress.csv...")
    try:
        # Skip metadata rows (first 5 rows)
        df_stress = pd.read_csv('L_wall_stress.csv', skiprows=5, header=None)
        
        # Columns based on your screenshot:
        # Column 0: V_in (m/f_in Hz)
        # Column 1: Time (s)
        # Column 2: Time (s)
        # Column 3: von Mises stress (N/m^2) = Pa
        
        stress_col = df_stress.iloc[:, 3]  # 4th column
        stress_col = pd.to_numeric(stress_col, errors='coerce')
        max_stress = stress_col.max()
        
        print(f"✅ Success!")
        print(f"   Rows: {len(df_stress)}")
        print(f"   Max stress: {max_stress:.2f} Pa")
        print(f"   Max stress: {max_stress/1000:.2f} kPa")
        print(f"   Max stress: {max_stress/1e6:.6f} MPa")
        
        results['max_wall_stress_pa'] = max_stress
        
    except Exception as e:
        print(f"❌ Error: {e}")
        results['max_wall_stress_pa'] = None
    
    # =============================================
    # ANALYSIS
    # =============================================
    print("\n" + "="*80)
    print("📊 EXTRACTED VALUES SUMMARY")
    print("="*80)
    
    print(f"\nOutput values (from COMSOL):")
    print(f"  • Max wall stress: {results.get('max_wall_stress_pa', 0):.2f} Pa")
    print(f"  • Max strain:      {results.get('max_strain_percent', 0):.4f} %")
    print(f"  • Peak WSS:        {results.get('peak_wss_pa', 0):.2f} Pa")
    
    # Check if values make sense
    print("\n" + "="*80)
    print("🔍 DATA QUALITY CHECK")
    print("="*80)
    
    stress = results.get('max_wall_stress_pa', 0)
    
    if stress < 10000:
        print("\n⚠️  WARNING: Stress values are VERY LOW")
        print(f"   Your max stress: {stress:.0f} Pa ({stress/1000:.2f} kPa)")
        print(f"   Expected range: 200,000-600,000 Pa (200-600 kPa)")
        print(f"   Your values are ~{200000/stress:.0f}x smaller than expected!")
        print("\n💡 Possible reasons:")
        print("   1. Wrong variable exported (not von Mises stress)")
        print("   2. Stress in small region, not whole aorta")
        print("   3. Very low pressure simulation (<50 mmHg)")
        print("   4. Unit mislabeling in COMSOL")
        print("\n❓ What pressure did you use in your simulation?")
        
    elif stress < 100000:
        print("\n⚠️  Stress values are lower than typical")
        print("   This might be okay for low-pressure simulations")
        
    else:
        print("\n✅ Stress values are in expected range!")
    
    return results


def get_simulation_parameters():
    """
    Interactive prompt to get simulation parameters
    """
    print("\n" + "="*80)
    print("❓ SIMULATION PARAMETERS")
    print("="*80)
    print("\nI need to know your simulation SETUP (not the results):")
    print("These are the boundary conditions YOU specified in COMSOL")
    
    params = {}
    
    # Pressure
    print("\n1️⃣  What INLET PRESSURE did you apply?")
    print("   Examples: 120 mmHg (resting), 250 mmHg (heavy squat)")
    pressure_input = input("   Enter pressure in mmHg [default: 220]: ").strip()
    params['pressure_peak_mmHg'] = float(pressure_input) if pressure_input else 220
    
    # Frequency
    print("\n2️⃣  What HEART RATE did you use?")
    print("   Convert to Hz: 60 bpm = 1.0 Hz, 75 bpm = 1.25 Hz")
    freq_input = input("   Enter frequency in Hz [default: 1.2]: ").strip()
    params['pulse_frequency_hz'] = float(freq_input) if freq_input else 1.2
    
    # Material stiffness
    print("\n3️⃣  What MATERIAL STIFFNESS (Young's modulus)?")
    print("   Typical aorta: 1.5 MPa")
    stiff_input = input("   Enter stiffness in MPa [default: 1.5]: ").strip()
    params['wall_stiffness_mpa'] = float(stiff_input) if stiff_input else 1.5
    
    # Valve type
    print("\n4️⃣  What VALVE TYPE is your geometry?")
    print("   0 = Normal tricuspid valve")
    print("   1 = Bicuspid aortic valve (BAV)")
    bav_input = input("   Enter 0 or 1 [default: 1]: ").strip()
    params['is_bav'] = int(bav_input) if bav_input else 1
    
    # Diameter
    print("\n5️⃣  What is the AORTIC DIAMETER in your geometry?")
    print("   Normal: 30-35mm, Dilated: 40-50mm")
    diam_input = input("   Enter diameter in mm [default: 42]: ").strip()
    params['aortic_diameter_mm'] = float(diam_input) if diam_input else 42
    
    return params


def create_training_data(comsol_results, sim_params):
    """
    Combine extracted results with simulation parameters
    """
    print("\n" + "="*80)
    print("🔧 CREATING ML TRAINING DATA")
    print("="*80)
    
    # Combine everything
    data = {
        **sim_params,
        **comsol_results
    }
    
    # Calculate risk category
    score = 0
    if data['max_wall_stress_pa'] > 500000: score += 2
    elif data['max_wall_stress_pa'] > 400000: score += 1
    
    if data['max_strain_percent'] > 15: score += 2
    elif data['max_strain_percent'] > 10: score += 1
    
    if data['aortic_diameter_mm'] > 42: score += 2
    elif data['aortic_diameter_mm'] > 38: score += 1
    
    if data['is_bav'] == 1: score += 1
    if data['pressure_peak_mmHg'] > 220: score += 1
    
    data['risk_category'] = 'High' if score >= 5 else 'Medium' if score >= 3 else 'Low'
    
    # Create DataFrame
    df = pd.DataFrame([data])
    
    # Reorder columns to match ML model expectations
    columns_order = [
        'pressure_peak_mmHg',
        'pulse_frequency_hz',
        'wall_stiffness_mpa',
        'is_bav',
        'aortic_diameter_mm',
        'max_wall_stress_pa',
        'max_strain_percent',
        'peak_wss_pa',
        'risk_category'
    ]
    
    df = df[columns_order]
    
    print("\n✅ Created training data:")
    print(df.to_string(index=False))
    
    # Save
    output_file = 'comsol_single_sample.csv'
    df.to_csv(output_file, index=False)
    
    print(f"\n💾 Saved to: {output_file}")
    
    return df


def suggest_next_steps(data):
    """
    Suggest what to do with this single data point
    """
    print("\n" + "="*80)
    print("🎯 NEXT STEPS")
    print("="*80)
    
    stress = data['max_wall_stress_pa'].values[0]
    
    if stress < 10000:
        print("""
⚠️  Your stress values are unexpectedly low.

RECOMMENDED APPROACH:
1. Verify in COMSOL that you exported the correct variable
2. Check the units in COMSOL (should be Pa or N/m²)
3. If values are correct, this represents a low-stress simulation

OPTION A - Use as validation only:
   → Keep your existing synthetic model
   → Use this COMSOL data to validate predictions
   → Shows model works on real CFD data

OPTION B - Scale the values:
   → If you believe stress should be 100x higher
   → I can multiply by a scaling factor
   → Then combine with synthetic data
        """)
    else:
        print("""
✅ Your data looks good!

Since you have only 1 simulation, RECOMMENDED APPROACH:

OPTION A - Combine with synthetic (BEST):
   → Synthetic: 499 samples (for learning patterns)
   → COMSOL: 1 sample (for validation)
   → Total: 500 samples
   → Model learns from synthetic, validates on your real data

OPTION B - Use for validation only:
   → Train model on 500 synthetic samples
   → Test accuracy on your 1 COMSOL sample
   → Show "Model predicts X, COMSOL actual is Y"
        """)
    
    print("\nWould you like me to:")
    print("  1. Combine with synthetic data")
    print("  2. Create validation test")
    print("  3. Fix stress values (if they're wrong)")


if __name__ == "__main__":
    print("\n🔬 COMSOL Data Extraction Tool")
    print("="*80)
    
    # Step 1: Extract COMSOL outputs
    comsol_results = extract_comsol_data()
    
    if all(v is not None for v in comsol_results.values()):
        # Step 2: Get simulation parameters
        print("\n" + "="*80)
        print("💡 TIP: If you don't know exact values, use estimates")
        print("   You can edit the CSV file afterwards")
        print("="*80)
        
        use_interactive = input("\nGet parameters interactively? (y/n) [y]: ").strip().lower()
        
        if use_interactive != 'n':
            sim_params = get_simulation_parameters()
        else:
            # Use defaults
            sim_params = {
                'pressure_peak_mmHg': 220,
                'pulse_frequency_hz': 1.2,
                'wall_stiffness_mpa': 1.5,
                'is_bav': 1,
                'aortic_diameter_mm': 42
            }
            print("\nUsing default parameters (edit CSV if needed)")
        
        # Step 3: Create training data
        training_data = create_training_data(comsol_results, sim_params)
        
        # Step 4: Suggest next steps
        suggest_next_steps(training_data)
        
        print("\n" + "="*80)
        print("✅ EXTRACTION COMPLETE!")
        print("="*80)
        print("\nFiles created:")
        print("  • comsol_single_sample.csv - Your COMSOL data in ML format")
        print("\nYou can now:")
        print("  • Edit the CSV if values need correction")
        print("  • Combine with synthetic data")
        print("  • Use for model validation")
        
    else:
        print("\n❌ Could not extract all required values")
        print("Please check your CSV files and try again")