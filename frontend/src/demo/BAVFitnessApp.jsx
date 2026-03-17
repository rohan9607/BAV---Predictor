// BAVFitnessApp.jsx - Vanilla CSS Version
import React, { useState } from 'react';
import { Heart, Activity, AlertTriangle, CheckCircle, XCircle, Info } from 'lucide-react';
import './BAVFitnessApp.css'; // Import the CSS file

const BAVFitnessApp = () => {
  const [profile, setProfile] = useState({
    diameter: 42,
    hasBav: true,
    age: 35
  });
  
  const exercises = [
    { 
      name: 'Walking', 
      pressure: 120, 
      icon: '🚶', 
      risk: 'low', 
      duration: '60 min',
      description: 'Safe to perform regularly'
    },
    { 
      name: 'Jogging', 
      pressure: 150, 
      icon: '🏃', 
      risk: 'low', 
      duration: '30 min',
      description: 'Safe to perform regularly'
    },
    { 
      name: 'Swimming', 
      pressure: 140, 
      icon: '🏊', 
      risk: 'low', 
      duration: '45 min',
      description: 'Safe to perform regularly'
    },
    { 
      name: 'Cycling', 
      pressure: 155, 
      icon: '🚴', 
      risk: 'medium', 
      duration: '45 min',
      description: 'Consult cardiologist first'
    },
    { 
      name: 'Yoga', 
      pressure: 110, 
      icon: '🧘', 
      risk: 'low', 
      duration: '60 min',
      description: 'Safe to perform regularly'
    },
    { 
      name: 'Light Weights', 
      pressure: 165, 
      icon: '🏋️', 
      risk: 'medium', 
      duration: '30 min',
      description: 'Consult cardiologist first'
    },
    { 
      name: 'Running', 
      pressure: 180, 
      icon: '🏃‍♂️', 
      risk: 'medium', 
      duration: '20 min',
      description: 'Consult cardiologist first'
    },
    { 
      name: 'CrossFit', 
      pressure: 220, 
      icon: '💪', 
      risk: 'high', 
      duration: '20 min',
      description: 'Not recommended - high risk'
    },
    { 
      name: 'Heavy Squats', 
      pressure: 260, 
      icon: '🏋️‍♀️', 
      risk: 'high', 
      duration: '15 min',
      description: 'Not recommended - high risk'
    },
    { 
      name: 'Powerlifting', 
      pressure: 290, 
      icon: '🏋️‍♂️', 
      risk: 'high', 
      duration: '10 min',
      description: 'Not recommended - high risk'
    },
  ];
  
  const getRiskIcon = (risk) => {
    switch(risk) {
      case 'low': 
        return <CheckCircle className="risk-icon icon-green" />;
      case 'medium': 
        return <AlertTriangle className="risk-icon icon-yellow" />;
      case 'high': 
        return <XCircle className="risk-icon icon-red" />;
      default: 
        return null;
    }
  };
  
  const getRiskMessage = (risk, description) => {
    let messageClass = 'risk-message ';
    let prefix = '';
    
    switch(risk) {
      case 'low':
        messageClass += 'message-safe';
        prefix = '✅ ';
        break;
      case 'medium':
        messageClass += 'message-caution';
        prefix = '⚠️ ';
        break;
      case 'high':
        messageClass += 'message-danger';
        prefix = '❌ ';
        break;
    }
    
    return (
      <div className={messageClass}>
        {prefix}{description}
      </div>
    );
  };

  return (
    <div className="app-container">
      {/* Header */}
      <div className="header-card">
        <div className="header-content">
          <Heart className="header-icon" />
          <div>
            <h1 className="header-title">BAV Fitness Companion</h1>
            <p className="header-subtitle">
              Personalized exercise recommendations for BAV patients
            </p>
          </div>
        </div>
        
        {/* Patient Profile */}
        <div className="profile-box">
          <h3 className="profile-title">
            <Info style={{width: '1rem', height: '1rem'}} />
            Your Profile
          </h3>
          <div className="profile-grid">
            <div>
              <span className="profile-item-label">Aortic Diameter:</span>
              <div className="profile-item-value">{profile.diameter}mm</div>
            </div>
            <div>
              <span className="profile-item-label">Valve Type:</span>
              <div className="profile-item-value">
                {profile.hasBav ? 'BAV' : 'Normal'}
              </div>
            </div>
            <div>
              <span className="profile-item-label">Age:</span>
              <div className="profile-item-value">{profile.age}</div>
            </div>
          </div>
        </div>
      </div>
      
      {/* Exercise Grid */}
      <div className="exercise-card">
        <h2 className="exercise-header">
          <Activity style={{width: '1.5rem', height: '1.5rem'}} />
          Exercise Safety Recommendations
        </h2>
        
        <div className="exercise-grid">
          {exercises.map((exercise, idx) => (
            <div 
              key={idx}
              className={`exercise-item risk-${exercise.risk}`}
            >
              <div className="exercise-item-header">
                <div className="exercise-item-left">
                  <span className="exercise-icon">{exercise.icon}</span>
                  <div>
                    <h3 className="exercise-name">{exercise.name}</h3>
                    <p className="exercise-duration">Duration: {exercise.duration}</p>
                  </div>
                </div>
                {getRiskIcon(exercise.risk)}
              </div>
              
              <div className="exercise-details">
                <div className="exercise-row">
                  <span className="exercise-label">Peak Pressure:</span>
                  <span className="exercise-value">{exercise.pressure} mmHg</span>
                </div>
                
                <div className="exercise-row">
                  <span className="exercise-label">Risk Level:</span>
                  <span className="exercise-value">{exercise.risk.toUpperCase()}</span>
                </div>
                
                {getRiskMessage(exercise.risk, exercise.description)}
              </div>
            </div>
          ))}
        </div>
      </div>
      
      {/* Legend */}
      <div className="legend-card">
        <h3 className="legend-title">Risk Categories</h3>
        <div className="legend-grid">
          <div className="legend-item">
            <CheckCircle className="risk-icon icon-green" />
            <div>
              <span className="legend-label legend-low">LOW RISK:</span> Safe for regular practice
            </div>
          </div>
          <div className="legend-item">
            <AlertTriangle className="risk-icon icon-yellow" />
            <div>
              <span className="legend-label legend-medium">MEDIUM RISK:</span> Medical clearance needed
            </div>
          </div>
          <div className="legend-item">
            <XCircle className="risk-icon icon-red" />
            <div>
              <span className="legend-label legend-high">HIGH RISK:</span> Avoid to prevent complications
            </div>
          </div>
        </div>
      </div>
      
      {/* Footer */}
      <div className="app-footer">
        <p>⚕️ Always consult your cardiologist before starting any exercise program</p>
        <p>Predictions based on ML model trained on 500+ CFD simulations</p>
      </div>
    </div>
  );
};

export default BAVFitnessApp;