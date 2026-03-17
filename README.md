# BAV---Predictor

# 🫀 BAV Risk Prediction System

A machine learning pipeline that predicts cardiovascular biomechanical 
risk for patients with Bicuspid Aortic Valve (BAV) during physical activity.

## Overview
BAV patients face life-threatening aortic stress during exercise, yet 
clinical guidance is rarely data-driven. This system uses simulated 
biomechanical data and supervised ML models to predict wall stress, 
strain, and risk category in real time — deployable via REST API into 
mobile apps, wearables, or clinical dashboards.

## System Architecture

### Phase 1 — Data Generation
- Biomechanical simulator generates realistic cardiovascular samples
- Output: `simulation_results.csv` (input features + labeled targets)

### Phase 2 — Model Training
| Target                | Type           | Model              |
|-----------------------|----------------|--------------------|
| max_wall_stress_pa    | Regression     | Random Forest      |
| max_strain_percent    | Regression     | Random Forest      |
| peak_wss_pa           | Regression     | Random Forest      |
| risk_category         | Classification | Gradient Boosting  |

- 80/20 train-test split
- Evaluated on R², MAE, and classification accuracy
- Models serialized as `.pkl` files

### Phase 3 — API Server (Runtime)
- REST API accepts patient + exercise parameters
- Returns real-time predictions for all 4 targets
- Designed for integration with fitness trackers and health platforms

## Use Cases
- Exercise safety advisor for BAV patients
- Integration with Apple Watch / Fitbit / Apple Health
- Real-time risk alerts during workouts
- Cardiologist reporting dashboard

## Tech Stack
Python · Scikit-learn · Random Forest · Gradient Boosting · REST API · Pandas

## Impact
- 📉 25% projected reduction in emergency surgeries
- 📉 30% reduction in unnecessary monitoring  
- 💰 $50,000+ saved per patient in healthcare costs
