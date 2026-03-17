"""
FastAPI Backend for BAV Aortic Stress Predictions
Loads trained models and serves predictions via REST API
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import joblib
import numpy as np
import json
from typing import Dict, List
import os

# Initialize FastAPI
app = FastAPI(
    title="BAV Aortic Stress Predictor",
    description="ML-powered predictions for bicuspid aortic valve hemodynamics",
    version="1.0"
)

# CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global variables for loaded models
scaler = None
regression_models = None
risk_classifier = None
metadata = None

# ==================== DATA MODELS ====================

class PatientInput(BaseModel):
    pressure_peak_mmHg: float = Field(..., ge=80, le=350, description="Peak systolic pressure")
    pulse_frequency_hz: float = Field(..., ge=0.5, le=2.0, description="Heart rate in Hz")
    wall_stiffness_mpa: float = Field(..., ge=0.1, le=5.0, description="Aortic wall stiffness")
    is_bav: int = Field(..., ge=0, le=1, description="0=Normal, 1=BAV")
    aortic_diameter_mm: float = Field(..., ge=20, le=60, description="Aortic diameter")
    
    class Config:
        json_schema_extra = {
            "example": {
                "pressure_peak_mmHg": 250,
                "pulse_frequency_hz": 1.0,
                "wall_stiffness_mpa": 1.5,
                "is_bav": 1,
                "aortic_diameter_mm": 42
            }
        }

class PredictionOutput(BaseModel):
    max_wall_stress_pa: float
    max_strain_percent: float
    peak_wss_pa: float
    risk_category: str
    risk_probabilities: Dict[str, float]
    feature_values: Dict[str, float]
    interpretation: str

class ExercisePreset(BaseModel):
    name: str
    pressure_peak_mmHg: float
    description: str

# ==================== MODEL LOADING ====================

@app.on_event("startup")
async def load_models():
    """Load all trained models on server startup"""
    global scaler, regression_models, risk_classifier, metadata
    
    model_dir = 'models'
    
    try:
        scaler = joblib.load(f'{model_dir}/scaler.pkl')
        regression_models = joblib.load(f'{model_dir}/regression_models.pkl')
        risk_classifier = joblib.load(f'{model_dir}/risk_classifier.pkl')
        
        with open(f'{model_dir}/metadata.json', 'r') as f:
            metadata = json.load(f)
        
        print("✅ Models loaded successfully!")
        print(f"   Features: {metadata['feature_names']}")
        print(f"   Trained: {metadata['trained_at']}")
        
    except Exception as e:
        print(f"❌ Error loading models: {e}")
        raise RuntimeError("Failed to load ML models. Train models first!")

# ==================== API ENDPOINTS ====================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "model_version": metadata.get('model_version') if metadata else None,
        "trained_at": metadata.get('trained_at') if metadata else None
    }

@app.get("/exercise-presets", response_model=List[ExercisePreset])
async def get_exercise_presets():
    """Get predefined exercise conditions"""
    return [
        {
            "name": "Resting",
            "pressure_peak_mmHg": 120,
            "description": "Normal resting state"
        },
        {
            "name": "Pushups",
            "pressure_peak_mmHg": 150,
            "description": "Light resistance exercise"
        },
        {
            "name": "Sprint",
            "pressure_peak_mmHg": 170,
            "description": "High-intensity cardio"
        },
        {
            "name": "Heavy Squat",
            "pressure_peak_mmHg": 250,
            "description": "Heavy resistance training"
        },
        {
            "name": "Maximal Lift",
            "pressure_peak_mmHg": 300,
            "description": "Maximal exertion"
        }
    ]

@app.post("/predict", response_model=PredictionOutput)
async def predict(patient: PatientInput):
    """
    Make predictions for given patient parameters
    """
    try:
        # Prepare input array
        X = np.array([[
            patient.pressure_peak_mmHg,
            patient.pulse_frequency_hz,
            patient.wall_stiffness_mpa,
            patient.is_bav,
            patient.aortic_diameter_mm
        ]])
        
        # Scale input
        X_scaled = scaler.transform(X)
        
        # Regression predictions
        stress = regression_models['stress'].predict(X_scaled)[0]
        strain = regression_models['strain'].predict(X_scaled)[0]
        wss = regression_models['wss'].predict(X_scaled)[0]
        
        # Risk classification
        risk_category = risk_classifier.predict(X_scaled)[0]
        risk_proba = risk_classifier.predict_proba(X_scaled)[0]
        risk_classes = risk_classifier.classes_
        
        risk_probabilities = {
            cls: float(prob) for cls, prob in zip(risk_classes, risk_proba)
        }
        
        # Generate interpretation
        interpretation = generate_interpretation(
            patient, stress, strain, wss, risk_category
        )
        
        return PredictionOutput(
            max_wall_stress_pa=float(stress),
            max_strain_percent=float(strain),
            peak_wss_pa=float(wss),
            risk_category=risk_category,
            risk_probabilities=risk_probabilities,
            feature_values={
                "pressure_peak_mmHg": patient.pressure_peak_mmHg,
                "pulse_frequency_hz": patient.pulse_frequency_hz,
                "wall_stiffness_mpa": patient.wall_stiffness_mpa,
                "is_bav": patient.is_bav,
                "aortic_diameter_mm": patient.aortic_diameter_mm
            },
            interpretation=interpretation
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")

@app.post("/batch-predict")
async def batch_predict(patients: List[PatientInput]):
    """
    Predict for multiple patients (useful for comparison charts)
    """
    results = []
    for patient in patients:
        result = await predict(patient)
        results.append(result)
    return results

@app.get("/feature-importance")
async def get_feature_importance():
    """
    Return feature importance for each prediction target
    """
    importance_data = {}
    
    for target_name, model in regression_models.items():
        feature_importance = [
            {
                "feature": feature,
                "importance": float(imp)
            }
            for feature, imp in zip(metadata['feature_names'], model.feature_importances_)
        ]
        feature_importance.sort(key=lambda x: x['importance'], reverse=True)
        importance_data[target_name] = feature_importance
    
    return importance_data

# ==================== HELPER FUNCTIONS ====================

def generate_interpretation(patient: PatientInput, stress: float, strain: float, 
                           wss: float, risk: str) -> str:
    """Generate human-readable interpretation"""
    
    valve_type = "bicuspid aortic valve (BAV)" if patient.is_bav else "normal tricuspid valve"
    
    interpretation = f"Patient with {valve_type} under {patient.pressure_peak_mmHg} mmHg peak pressure:\n\n"
    
    # Stress interpretation
    if stress > 500000:  # 500 kPa
        interpretation += f"⚠️ Wall stress ({stress/1000:.1f} kPa) is elevated, indicating high mechanical load.\n"
    else:
        interpretation += f"✓ Wall stress ({stress/1000:.1f} kPa) is within acceptable range.\n"
    
    # Strain interpretation
    if strain > 15:
        interpretation += f"⚠️ Wall strain ({strain:.1f}%) suggests significant deformation.\n"
    else:
        interpretation += f"✓ Wall strain ({strain:.1f}%) is moderate.\n"
    
    # Risk interpretation
    if risk == "High":
        interpretation += f"\n🚨 HIGH RISK: Recommend avoiding heavy resistance exercise and regular monitoring."
    elif risk == "Medium":
        interpretation += f"\n⚠️ MEDIUM RISK: Moderate exercise with medical supervision recommended."
    else:
        interpretation += f"\n✓ LOW RISK: Standard exercise guidelines apply."
    
    return interpretation

# ==================== RUN SERVER ====================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)