"""
Synthetic Data Generator for BAV Project
Use this if you don't have enough COMSOL simulation data yet
This creates realistic-looking training data based on biomechanical principles
"""

import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler

def generate_bav_dataset(n_samples=500, random_state=42):
    """
    Generate synthetic BAV simulation data
    Based on biomechanical relationships from literature
    """
    np.random.seed(random_state)
    
    data = []
    
    for i in range(n_samples):
        # Input parameters (features)
        pressure_peak = np.random.choice([120, 150, 170, 220, 250, 300])
        pulse_freq = np.random.uniform(0.8, 1.5)  # 48-90 bpm
        wall_stiffness = np.random.uniform(0.5, 2.5)
        is_bav = np.random.choice([0, 1], p=[0.3, 0.7])  # 70% BAV patients
        aortic_diameter = np.random.uniform(30, 50) if is_bav else np.random.uniform(28, 38)
        
        # Add some noise
        noise_stress = np.random.normal(0, 0.1)
        noise_strain = np.random.normal(0, 0.05)
        noise_wss = np.random.normal(0, 0.08)
        
        # Biomechanical relationships (simplified models)
        # Wall stress increases with pressure and diameter, decreases with stiffness
        base_stress = (pressure_peak * 133.322) * (aortic_diameter / 1000) / (wall_stiffness * 0.003)
        bav_multiplier = 1.4 if is_bav else 1.0
        max_wall_stress = base_stress * bav_multiplier * (1 + noise_stress)
        
        # Strain related to stress and stiffness
        max_strain = (max_wall_stress / (wall_stiffness * 1e6)) * 100 * (1 + noise_strain)
        
        # WSS increases with pressure and frequency
        peak_wss = (pressure_peak / 120) * pulse_freq * 2.5 * (1 + noise_wss)
        
        # Risk categorization
        risk_score = 0
        if max_wall_stress > 500000: risk_score += 2
        if max_strain > 15: risk_score += 2
        if aortic_diameter > 42: risk_score += 2
        if is_bav: risk_score += 1
        if pressure_peak > 220: risk_score += 1
        
        if risk_score >= 5:
            risk_category = "High"
        elif risk_score >= 3:
            risk_category = "Medium"
        else:
            risk_category = "Low"
        
        data.append({
            'pressure_peak_mmHg': pressure_peak,
            'pulse_frequency_hz': round(pulse_freq, 2),
            'wall_stiffness_mpa': round(wall_stiffness, 2),
            'is_bav': is_bav,
            'aortic_diameter_mm': round(aortic_diameter, 1),
            'max_wall_stress_pa': round(max_wall_stress, 2),
            'max_strain_percent': round(max_strain, 3),
            'peak_wss_pa': round(peak_wss, 3),
            'risk_category': risk_category
        })
    
    df = pd.DataFrame(data)
    return df


def validate_dataset(df):
    """Check if generated data looks reasonable"""
    print("=" * 50)
    print("Dataset Validation Report")
    print("=" * 50)
    
    print(f"\n📊 Total samples: {len(df)}")
    print(f"\n📈 Feature statistics:")
    print(df[['pressure_peak_mmHg', 'pulse_frequency_hz', 'wall_stiffness_mpa', 
              'aortic_diameter_mm']].describe())
    
    print(f"\n🎯 Target statistics:")
    print(df[['max_wall_stress_pa', 'max_strain_percent', 'peak_wss_pa']].describe())
    
    print(f"\n⚖️ Class distribution:")
    print(df['risk_category'].value_counts())
    print(f"\n🫀 BAV distribution:")
    print(df['is_bav'].value_counts())
    
    # Check for correlations (should see expected relationships)
    print(f"\n🔗 Key correlations:")
    print(f"Pressure vs Wall Stress: {df['pressure_peak_mmHg'].corr(df['max_wall_stress_pa']):.3f}")
    print(f"Diameter vs Wall Stress: {df['aortic_diameter_mm'].corr(df['max_wall_stress_pa']):.3f}")
    print(f"BAV vs Strain: {df['is_bav'].corr(df['max_strain_percent']):.3f}")
    
    print("\n✅ Dataset ready for training!")


def augment_with_comsol_data(synthetic_df, comsol_csv_path):
    """
    Combine synthetic data with your real COMSOL results
    """
    try:
        real_df = pd.read_csv(comsol_csv_path)
        print(f"✓ Loaded {len(real_df)} real simulation samples")
        
        # Combine datasets
        combined_df = pd.concat([synthetic_df, real_df], ignore_index=True)
        print(f"✓ Combined dataset: {len(combined_df)} total samples")
        
        return combined_df
    except FileNotFoundError:
        print(f"⚠️ No COMSOL data found at {comsol_csv_path}")
        print("Using synthetic data only")
        return synthetic_df


# ==================== MAIN EXECUTION ====================

if __name__ == "__main__":
    print("🔬 Generating synthetic BAV training data...\n")
    
    # Generate synthetic dataset
    df = generate_bav_dataset(n_samples=500, random_state=42)
    
    # Validate
    validate_dataset(df)
    
    # Optionally merge with real COMSOL data if you have it
    # df = augment_with_comsol_data(df, 'comsol_results.csv')
    
    # Save
    output_file = 'simulation_results.csv'
    df.to_csv(output_file, index=False)
    print(f"\n💾 Saved to {output_file}")
    
    # Show sample
    print(f"\n📋 Sample data:")
    print(df.head(10))
    
    print("\n" + "=" * 50)
    print("✅ Ready to train! Run: python train_model.py")
    print("=" * 50)