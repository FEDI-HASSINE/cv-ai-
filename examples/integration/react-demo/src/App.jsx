import React, { useState } from 'react';
import './App.css';

export default function App() {
  const [file, setFile] = useState(null);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);

  const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://localhost:4000';

  const onFileChange = (e) => {
    const selectedFile = e.target.files?.[0] || null;
    setFile(selectedFile);
    setError(null);
    setResult(null);
  };

  const analyzeResume = async () => {
    if (!file) {
      setError('Veuillez sélectionner un fichier (.pdf, .docx, .doc, .txt)');
      return;
    }

    setError(null);
    setLoading(true);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', file);

      const response = await fetch(`${BACKEND_URL}/api/resume/analyze`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data?.detail || data?.error || JSON.stringify(data));
      }

      setResult(data);
    } catch (e) {
      setError(`Erreur: ${e.message}`);
    } finally {
      setLoading(false);
    }
  };

  const getScoreColor = (score) => {
    if (score >= 80) return '#10b981'; // green
    if (score >= 60) return '#f59e0b'; // orange
    return '#ef4444'; // red
  };

  const getScoreLabel = (score) => {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Bon';
    if (score >= 40) return 'Moyen';
    return 'Faible';
  };

  return (
    <div className="app">
      <div className="container">
        <header className="header">
          <h1>🎯 Analyseur de CV Intelligent</h1>
          <p className="subtitle">
            Uploadez votre CV pour obtenir une analyse détaillée et des suggestions d'amélioration
          </p>
        </header>

        <div className="upload-section">
          <div className="file-input-wrapper">
            <label htmlFor="file-upload" className="file-label">
              {file ? (
                <>
                  <span className="file-icon">📄</span>
                  <span className="file-name">{file.name}</span>
                  <span className="file-size">
                    ({(file.size / 1024).toFixed(1)} KB)
                  </span>
                </>
              ) : (
                <>
                  <span className="upload-icon">📤</span>
                  <span>Choisir un fichier CV</span>
                  <span className="file-hint">PDF, DOCX, DOC ou TXT</span>
                </>
              )}
            </label>
            <input
              id="file-upload"
              type="file"
              onChange={onFileChange}
              accept=".pdf,.docx,.doc,.txt"
              className="file-input"
            />
          </div>

          <button
            onClick={analyzeResume}
            disabled={loading || !file}
            className="analyze-button"
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Analyse en cours...
              </>
            ) : (
              <>
                <span>🔍</span>
                Analyser le CV
              </>
            )}
          </button>
        </div>

        {error && (
          <div className="alert alert-error">
            <span className="alert-icon">⚠️</span>
            <div>
              <strong>Erreur</strong>
              <p>{error}</p>
            </div>
          </div>
        )}

        {result && (
          <div className="results">
            {/* Scores Section */}
            <div className="scores-grid">
              <div className="score-card">
                <div className="score-header">
                  <h3>Score Global</h3>
                  <span className="score-badge">
                    {getScoreLabel(result.overall_score)}
                  </span>
                </div>
                <div className="score-circle" style={{ '--score-color': getScoreColor(result.overall_score) }}>
                  <svg viewBox="0 0 100 100">
                    <circle className="score-bg" cx="50" cy="50" r="45" />
                    <circle
                      className="score-fill"
                      cx="50"
                      cy="50"
                      r="45"
                      style={{
                        strokeDasharray: `${result.overall_score * 2.83} 283`,
                        stroke: getScoreColor(result.overall_score)
                      }}
                    />
                  </svg>
                  <div className="score-value">
                    <span className="score-number">{result.overall_score}</span>
                    <span className="score-max">/100</span>
                  </div>
                </div>
              </div>

              <div className="score-card">
                <div className="score-header">
                  <h3>Score ATS</h3>
                  <span className="score-badge">
                    {getScoreLabel(result.ats_score)}
                  </span>
                </div>
                <div className="score-circle" style={{ '--score-color': getScoreColor(result.ats_score) }}>
                  <svg viewBox="0 0 100 100">
                    <circle className="score-bg" cx="50" cy="50" r="45" />
                    <circle
                      className="score-fill"
                      cx="50"
                      cy="50"
                      r="45"
                      style={{
                        strokeDasharray: `${result.ats_score * 2.83} 283`,
                        stroke: getScoreColor(result.ats_score)
                      }}
                    />
                  </svg>
                  <div className="score-value">
                    <span className="score-number">{result.ats_score}</span>
                    <span className="score-max">/100</span>
                  </div>
                </div>
              </div>

              <div className="info-card">
                <div className="info-icon">💼</div>
                <div className="info-content">
                  <span className="info-label">Expérience</span>
                  <span className="info-value">
                    {result.experience_years} {result.experience_years > 1 ? 'ans' : 'an'}
                  </span>
                </div>
              </div>
            </div>

            {/* Skills Section */}
            <div className="section">
              <h2 className="section-title">
                <span className="section-icon">🛠️</span>
                Compétences Techniques
              </h2>
              <div className="skills-container">
                {result.technical_skills && result.technical_skills.length > 0 ? (
                  result.technical_skills.map((skill, idx) => (
                    <span key={idx} className="skill-tag technical">
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="empty-message">Aucune compétence technique détectée</p>
                )}
              </div>
            </div>

            <div className="section">
              <h2 className="section-title">
                <span className="section-icon">🤝</span>
                Soft Skills
              </h2>
              <div className="skills-container">
                {result.soft_skills && result.soft_skills.length > 0 ? (
                  result.soft_skills.map((skill, idx) => (
                    <span key={idx} className="skill-tag soft">
                      {skill}
                    </span>
                  ))
                ) : (
                  <p className="empty-message">Aucune soft skill détectée</p>
                )}
              </div>
            </div>

            {/* Strengths */}
            {result.strengths && result.strengths.length > 0 && (
              <div className="section">
                <h2 className="section-title">
                  <span className="section-icon">✅</span>
                  Points Forts
                </h2>
                <ul className="list strengths-list">
                  {result.strengths.map((strength, idx) => (
                    <li key={idx} className="list-item">
                      <span className="list-bullet">•</span>
                      {strength}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Weaknesses */}
            {result.weaknesses && result.weaknesses.length > 0 && (
              <div className="section">
                <h2 className="section-title">
                  <span className="section-icon">⚠️</span>
                  Points à Améliorer
                </h2>
                <ul className="list weaknesses-list">
                  {result.weaknesses.map((weakness, idx) => (
                    <li key={idx} className="list-item">
                      <span className="list-bullet">•</span>
                      {weakness}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Suggestions */}
            {result.suggestions && result.suggestions.length > 0 && (
              <div className="section">
                <h2 className="section-title">
                  <span className="section-icon">💡</span>
                  Suggestions d'Amélioration
                </h2>
                <ul className="list suggestions-list">
                  {result.suggestions.map((suggestion, idx) => (
                    <li key={idx} className="list-item">
                      <span className="list-bullet">•</span>
                      {suggestion}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Raw JSON (debug) */}
            <details className="json-details">
              <summary className="json-summary">
                <span>📋 Voir les données JSON brutes</span>
              </summary>
              <pre className="json-content">
                {JSON.stringify(result, null, 2)}
              </pre>
            </details>
          </div>
        )}
      </div>

      <footer className="footer">
        <p>
          Propulsé par FastAPI + Node.js + React
          <span className="version">v1.0</span>
        </p>
      </footer>
    </div>
  );
}
