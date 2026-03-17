"""
BAV Aortic Stress Prediction - ML Training Pipeline
Complete code for training and saving your model
"""

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score, classification_report
import joblib
import json
from datetime import datetime

class BAVMLPipeline:
    def __init__(self):
        self.regression_models = {}
        self.classification_model = None
        self.scaler = StandardScaler()
        self.feature_names = None
        self.metadata = {}
        
    def load_simulation_data(self, csv_path):
        """
        Load your COMSOL/ANSYS simulation results
        Expected CSV columns:
        - pressure_peak_mmHg
        - pulse_frequency_hz
        - wall_stiffness_mpa
        - is_bav (0 or 1)
        - aortic_diameter_mm
        - max_wall_stress_pa (target)
        - max_strain_percent (target)
        - peak_wss_pa (target)
        - risk_category (Low/Medium/High) (target)
        """
        df = pd.read_csv(csv_path)
        print(f"✓ Loaded {len(df)} simulation samples")
        print(f"✓ Columns: {df.columns.tolist()}")
        return df
    
    def prepare_data(self, df):
        """Split features and targets"""
        # Input features
        feature_cols = [
            'pressure_peak_mmHg', 
            'pulse_frequency_hz',
            'wall_stiffness_mpa',
            'is_bav',
            'aortic_diameter_mm'
        ]
        
        X = df[feature_cols]
        self.feature_names = feature_cols
        
        # Regression targets
        y_stress = df['max_wall_stress_pa']
        y_strain = df['max_strain_percent']
        y_wss = df['peak_wss_pa']
        
        # Classification target
        y_risk = df['risk_category']
        
        return X, y_stress, y_strain, y_wss, y_risk
    
    def train_regression_models(self, X, y_dict):
        """
        Train separate models for each continuous output
        y_dict = {'stress': y_stress, 'strain': y_strain, 'wss': y_wss}
        """
        X_train, X_test, = train_test_split(X, test_size=0.2, random_state=42)
        
        # Scale features
        X_train_scaled = self.scaler.fit_transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        results = {}
        
        for target_name, y in y_dict.items():
            print(f"\n🔧 Training {target_name} predictor...")
            
            y_train, y_test = train_test_split(y, test_size=0.2, random_state=42)
            
            # Random Forest Regressor
            model = RandomForestRegressor(
                n_estimators=200,
                max_depth=15,
                min_samples_split=5,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=-1
            )
            
            model.fit(X_train_scaled, y_train)
            
            # Evaluate
            y_pred = model.predict(X_test_scaled)
            r2 = r2_score(y_test, y_pred)
            mae = mean_absolute_error(y_test, y_pred)
            
            # Cross-validation
            cv_scores = cross_val_score(model, X_train_scaled, y_train, 
                                       cv=5, scoring='r2')
            
            print(f"  R² Score: {r2:.4f}")
            print(f"  MAE: {mae:.4f}")
            print(f"  CV R² (mean): {cv_scores.mean():.4f} (±{cv_scores.std():.4f})")
            
            # Feature importance
            importance = pd.DataFrame({
                'feature': self.feature_names,
                'importance': model.feature_importances_
            }).sort_values('importance', ascending=False)
            
            print(f"  Top features: {importance.head(3)['feature'].tolist()}")
            
            self.regression_models[target_name] = model
            results[target_name] = {
                'r2': r2,
                'mae': mae,
                'cv_r2_mean': cv_scores.mean(),
                'feature_importance': importance.to_dict('records')
            }
        
        return results
    
    def train_risk_classifier(self, X, y_risk):
        """Train model to classify dilation risk (Low/Medium/High)"""
        print(f"\n🎯 Training risk classifier...")
        
        X_train, X_test, y_train, y_test = train_test_split(
            X, y_risk, test_size=0.2, random_state=42, stratify=y_risk
        )
        
        X_train_scaled = self.scaler.transform(X_train)
        X_test_scaled = self.scaler.transform(X_test)
        
        model = GradientBoostingClassifier(
            n_estimators=150,
            learning_rate=0.1,
            max_depth=5,
            random_state=42
        )
        
        model.fit(X_train_scaled, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test_scaled)
        print("\nClassification Report:")
        print(classification_report(y_test, y_pred))
        
        self.classification_model = model
        
        return {
            'accuracy': model.score(X_test_scaled, y_test),
            'report': classification_report(y_test, y_pred, output_dict=True)
        }
    
    def save_models(self, output_dir='models'):
        """Save all trained models and metadata"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        # Save models
        joblib.dump(self.scaler, f'{output_dir}/scaler.pkl')
        joblib.dump(self.regression_models, f'{output_dir}/regression_models.pkl')
        joblib.dump(self.classification_model, f'{output_dir}/risk_classifier.pkl')
        
        # Save metadata
        metadata = {
            'feature_names': self.feature_names,
            'trained_at': datetime.now().isoformat(),
            'model_version': '1.0'
        }
        
        with open(f'{output_dir}/metadata.json', 'w') as f:
            json.dump(metadata, f, indent=2)
        
        print(f"\n✅ Models saved to {output_dir}/")
        print("   - scaler.pkl")
        print("   - regression_models.pkl")
        print("   - risk_classifier.pkl")
        print("   - metadata.json")


# ==================== USAGE EXAMPLE ====================

if __name__ == "__main__":
    # Initialize pipeline
    pipeline = BAVMLPipeline()
    
    # Load your simulation data
    df = pipeline.load_simulation_data('simulation_results.csv')
    
    # Prepare data
    X, y_stress, y_strain, y_wss, y_risk = pipeline.prepare_data(df)
    
    # Train regression models
    regression_results = pipeline.train_regression_models(X, {
        'stress': y_stress,
        'strain': y_strain,
        'wss': y_wss
    })
    
    # Train risk classifier
    classification_results = pipeline.train_risk_classifier(X, y_risk)
    
    # Save everything
    pipeline.save_models('models')
    
    print("\n🎉 Training complete! Models ready for deployment.")