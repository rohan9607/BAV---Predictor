// frontend/src/App.jsx - Vanilla CSS version
import React, { useState, useEffect } from 'react';
import { Activity, Heart, AlertTriangle, TrendingUp, Info, Smartphone } from 'lucide-react';
import BAVFitnessApp from './demo/BAVFitnessApp';

function App() {
  const [formData, setFormData] = useState({
    pressure_peak_mmHg: 120,
    pulse_frequency_hz: 1.0,
    wall_stiffness_mpa: 1.5,
    is_bav: 1,
    aortic_diameter_mm: 35
  });
  
  const [prediction, setPrediction] = useState(null);
  const [loading, setLoading] = useState(false);
  const [exercisePresets, setExercisePresets] = useState([]);
  const [error, setError] = useState(null);
  const [switchToApp, setSwitchToApp] = useState(false);
  const API_URL = 'http://localhost:8000';
  
  useEffect(() => {
    fetch(`${API_URL}/exercise-presets`)
      .then(res => res.json())
      .then(data => setExercisePresets(data))
      .catch(err => {
        console.error('Failed to load presets:', err);
        setError('Backend not responding. Make sure API is running on port 8000');
      });
  }, []);
  
  const handlePresetClick = (preset) => {
    setFormData(prev => ({
      ...prev,
      pressure_peak_mmHg: preset.pressure_peak_mmHg
    }));
  };
  
  const handlePredict = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${API_URL}/predict`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      
      if (!response.ok) {
        throw new Error('Prediction failed');
      }
      
      const data = await response.json();
      setPrediction(data);
    } catch (err) {
      setError('Prediction failed. Ensure the backend is running: python api.py');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const getRiskClass = (risk) => {
    switch(risk) {
      case 'Low': return 'risk-low';
      case 'Medium': return 'risk-medium';
      case 'High': return 'risk-high';
      default: return '';
    }
  };
  
  return (
    switchToApp ? 
    <BAVFitnessApp/>
    :
    <div className="container">
      {/* Header */}
      <div className="header">
        <div className="header-title">
          <Heart size={48} color="#ef4444" />
          <h1>BAV Aortic Stress Predictor</h1>
        </div>
  {/* ← NEW BUTTON – fits the theme perfectly */}
    <button className="switch-app-btn" onClick={() => setSwitchToApp(true)}>
      <Smartphone className="w-5 h-5" />
      Switch To Fitness App
    </button>
        <p className="header-subtitle">
          Machine Learning-powered hemodynamic analysis for bicuspid aortic valve patients
        </p>
      </div>
      
      {/* Error Alert */}
      {error && (
        <div className="alert-error">
          <strong>Error:</strong> {error}
        </div>
      )}
      
      <div className="grid">
        {/* Input Panel */}
        <div className="card">
          <div className="card-header">
            <Activity size={24} />
            Patient Parameters
          </div>
          
          {/* Exercise Presets */}
          <div className="form-group">
            <label className="form-label">Exercise Condition Presets</label>
            <div className="preset-grid">
              {exercisePresets.map((preset) => (
                <button
                  key={preset.name}
                  onClick={() => handlePresetClick(preset)}
                  className="btn btn-preset"
                  title={preset.description}
                >
                  {preset.name}
                </button>
              ))}
            </div>
          </div>
          
          {/* Pressure */}
          <div className="form-group">
            <label className="form-label">Peak Systolic Pressure (mmHg)</label>
            <input
              type="number"
              value={formData.pressure_peak_mmHg}
              onChange={(e) => setFormData({...formData, pressure_peak_mmHg: parseFloat(e.target.value)})}
              className="form-input"
              min="80"
              max="350"
              step="10"
            />
            <p className="form-hint">Normal: 120 | Heavy lift: 250-300</p>
          </div>
          
          {/* Heart Rate */}
          <div className="form-group">
            <label className="form-label">Pulse Frequency (Hz)</label>
            <input
              type="number"
              value={formData.pulse_frequency_hz}
              onChange={(e) => setFormData({...formData, pulse_frequency_hz: parseFloat(e.target.value)})}
              className="form-input"
              min="0.5"
              max="2.0"
              step="0.1"
            />
            <p className="form-hint">1 Hz = 60 bpm</p>
          </div>
          
          {/* Wall Stiffness */}
          <div className="form-group">
            <label className="form-label">Wall Stiffness (MPa)</label>
            <input
              type="number"
              value={formData.wall_stiffness_mpa}
              onChange={(e) => setFormData({...formData, wall_stiffness_mpa: parseFloat(e.target.value)})}
              className="form-input"
              min="0.1"
              max="5.0"
              step="0.1"
            />
            <p className="form-hint">Higher = stiffer aorta</p>
          </div>
          
          {/* Valve Type */}
          <div className="form-group">
            <label className="form-label">Valve Type</label>
            <select
              value={formData.is_bav}
              onChange={(e) => setFormData({...formData, is_bav: parseInt(e.target.value)})}
              className="form-select"
            >
              <option value={0}>Normal Tricuspid Valve</option>
              <option value={1}>Bicuspid Aortic Valve (BAV)</option>
            </select>
          </div>
          
          {/* Aortic Diameter */}
          <div className="form-group">
            <label className="form-label">Aortic Diameter (mm)</label>
            <input
              type="number"
              value={formData.aortic_diameter_mm}
              onChange={(e) => setFormData({...formData, aortic_diameter_mm: parseFloat(e.target.value)})}
              className="form-input"
              min="20"
              max="60"
              step="1"
            />
            <p className="form-hint">Normal: 30-35mm | Dilated: &gt;40mm</p>
          </div>
          
          <button
            onClick={handlePredict}
            disabled={loading}
            className="btn btn-primary"
          >
            {loading ? 'Analyzing...' : 'Predict Aortic Response'}
          </button>
        </div>
        
        {/* Results Panel */}
        <div className="card">
          <div className="card-header">
            <TrendingUp size={24} />
            Prediction Results
          </div>
          
          {!prediction ? (
            <div className="empty-state">
              <Info size={64} />
              <p>Enter patient parameters and click predict to see results</p>
            </div>
          ) : (
            <div>
              {/* Risk Category */}
              <div className={`risk-card ${getRiskClass(prediction.risk_category)}`}>
                <div className="risk-header">
                  <AlertTriangle size={20} />
                  <span>{prediction.risk_category} Risk</span>
                </div>
                <div className="risk-probs">
                  {Object.entries(prediction.risk_probabilities).map(([risk, prob]) => (
                    <div key={risk} className="risk-prob-row">
                      <span>{risk}:</span>
                      <span style={{fontWeight: 600}}>{(prob * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </div>
              
              {/* Metrics */}
              <div className="metrics-grid">
                <div className="metric-card metric-stress">
                  <div className="metric-label">Max Wall Stress</div>
                  <div className="metric-value">
                    {(prediction.max_wall_stress_pa / 1000).toFixed(1)} kPa
                  </div>
                </div>
                
                <div className="metric-card metric-strain">
                  <div className="metric-label">Max Strain</div>
                  <div className="metric-value">
                    {prediction.max_strain_percent.toFixed(2)}%
                  </div>
                </div>
                
                <div className="metric-card metric-wss">
                  <div className="metric-label">Peak WSS</div>
                  <div className="metric-value">
                    {prediction.peak_wss_pa.toFixed(2)} Pa
                  </div>
                </div>
              </div>
              
              {/* Interpretation */}
              <div className="interpretation">
                <h3>Clinical Interpretation</h3>
                <p>{prediction.interpretation}</p>
              </div>
            </div>
          )}
        </div>
      </div>
      
      {/* Footer */}
      <div className="footer">
        <p>ML Model trained on CFD simulation data | For research purposes only</p>
      </div>

    </div>
  );
}

export default App;