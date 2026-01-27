import React, { useEffect, useState } from 'react';

const SplashScreen = ({ onFinish, duration = 3000 }) => {
  const [progress, setProgress] = useState(0);
  const [fadeOut, setFadeOut] = useState(false);

  useEffect(() => {
    // Progress animation
    const progressInterval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(progressInterval);
          return 100;
        }
        return prev + 2;
      });
    }, duration / 50);

    // Fade out and finish
    const fadeTimer = setTimeout(() => {
      setFadeOut(true);
    }, duration - 500);

    const finishTimer = setTimeout(() => {
      onFinish();
    }, duration);

    return () => {
      clearInterval(progressInterval);
      clearTimeout(fadeTimer);
      clearTimeout(finishTimer);
    };
  }, [duration, onFinish]);

  return (
    <div style={{
      ...styles.container,
      opacity: fadeOut ? 0 : 1,
      transition: 'opacity 0.5s ease-out'
    }}>
      {/* Animated circuit board background */}
      <div style={styles.circuitBackground}>
        {/* Circuit lines - animated */}
        <svg style={styles.circuitSvg} viewBox="0 0 1000 1000" xmlns="http://www.w3.org/2000/svg">
          {/* Horizontal lines */}
          <line x1="0" y1="200" x2="1000" y2="200" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" fill="freeze" />
          </line>
          <line x1="0" y1="400" x2="1000" y2="400" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" begin="0.2s" fill="freeze" />
          </line>
          <line x1="0" y1="600" x2="1000" y2="600" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" begin="0.4s" fill="freeze" />
          </line>
          <line x1="0" y1="800" x2="1000" y2="800" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" begin="0.6s" fill="freeze" />
          </line>
          
          {/* Vertical lines */}
          <line x1="250" y1="0" x2="250" y2="1000" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" begin="0.3s" fill="freeze" />
          </line>
          <line x1="500" y1="0" x2="500" y2="1000" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" begin="0.5s" fill="freeze" />
          </line>
          <line x1="750" y1="0" x2="750" y2="1000" style={styles.circuitLine} strokeDasharray="1000" strokeDashoffset="1000">
            <animate attributeName="stroke-dashoffset" from="1000" to="0" dur="2s" begin="0.7s" fill="freeze" />
          </line>

          {/* Circuit nodes */}
          <circle cx="250" cy="200" r="5" style={styles.circuitNode}>
            <animate attributeName="r" from="0" to="5" dur="0.5s" begin="0.5s" fill="freeze" />
          </circle>
          <circle cx="500" cy="400" r="5" style={styles.circuitNode}>
            <animate attributeName="r" from="0" to="5" dur="0.5s" begin="0.7s" fill="freeze" />
          </circle>
          <circle cx="750" cy="600" r="5" style={styles.circuitNode}>
            <animate attributeName="r" from="0" to="5" dur="0.5s" begin="0.9s" fill="freeze" />
          </circle>
          <circle cx="500" cy="800" r="5" style={styles.circuitNode}>
            <animate attributeName="r" from="0" to="5" dur="0.5s" begin="1.1s" fill="freeze" />
          </circle>
        </svg>
      </div>

      {/* Central logo area */}
      <div style={styles.logoContainer}>
        {/* Outer glowing ring */}
        <div style={{
          ...styles.outerRing,
          animation: 'pulse 2s ease-in-out infinite'
        }}></div>

        {/* Logo badge */}
        <div style={styles.logoBadge}>
          {/* Icon symbols */}
          <div style={styles.iconGroup}>
            {/* Gear */}
            <svg style={styles.icon} viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
              <path d="M 30,10 L 34,12 L 34,16 L 30,18 L 26,16 L 26,12 Z
                       M 42,16 L 46,18 L 44,22 L 40,20 L 38,18 L 40,14 Z
                       M 48,30 L 48,34 L 44,34 L 42,30 L 44,26 L 48,26 Z
                       M 42,44 L 40,46 L 38,42 L 40,40 L 44,38 L 46,42 Z
                       M 30,50 L 26,48 L 26,44 L 30,42 L 34,44 L 34,48 Z
                       M 18,44 L 14,42 L 16,38 L 20,40 L 22,42 L 20,46 Z
                       M 12,30 L 12,26 L 16,26 L 18,30 L 16,34 L 12,34 Z
                       M 18,16 L 20,14 L 22,18 L 20,20 L 16,22 L 14,18 Z"
                    fill="#ffffff" stroke="#00bfea" strokeWidth="2"/>
              <circle cx="30" cy="30" r="10" fill="none" stroke="#ffffff" strokeWidth="3"/>
            </svg>

            {/* Wrench */}
            <svg style={styles.iconSmall} viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
              <g transform="translate(20, 20) rotate(45)">
                <rect x="-2" y="-15" width="4" height="30" fill="#ffffff" stroke="#00bfea" strokeWidth="1.5" rx="1"/>
                <circle cx="0" cy="-15" r="5" fill="#ffffff" stroke="#00bfea" strokeWidth="1.5"/>
                <rect x="-1.5" y="-18" width="3" height="4" fill="#ffffff" stroke="#00bfea" strokeWidth="1"/>
              </g>
            </svg>

            {/* Shield */}
            <svg style={styles.iconSmall} viewBox="0 0 40 40" xmlns="http://www.w3.org/2000/svg">
              <path d="M 20,5 L 32,10 L 32,18 Q 32,26, 20,32 Q 8,26, 8,18 L 8,10 Z" 
                    fill="#ffffff" stroke="#00bfea" strokeWidth="1.5"/>
              <path d="M 14,18 L 18,22 L 26,14" 
                    fill="none" stroke="#00bfea" strokeWidth="2.5" strokeLinecap="round"/>
            </svg>
          </div>

          {/* Company name */}
          <h1 style={styles.companyName}>Blistex</h1>
          <p style={styles.subtitle}>PRODUCTION MAINTENANCE ASSESSMENT</p>
        </div>
      </div>

      {/* Loading bar */}
      <div style={styles.loadingContainer}>
        <div style={styles.loadingBarBg}>
          <div style={{
            ...styles.loadingBarFill,
            width: `${progress}%`
          }}></div>
        </div>
        <p style={styles.loadingText}>Loading... {Math.round(progress)}%</p>
      </div>

      {/* Footer */}
      <div style={styles.footer}>
        <p style={styles.footerText}>Powered by AI-Enhanced Assessment Technology</p>
      </div>

      {/* Keyframe animations */}
      <style>
        {`
          @keyframes pulse {
            0%, 100% {
              transform: scale(1);
              opacity: 0.6;
            }
            50% {
              transform: scale(1.05);
              opacity: 0.8;
            }
          }
          @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
          }
        `}
      </style>
    </div>
  );
};

const styles = {
  container: {
    position: 'fixed',
    top: 0,
    left: 0,
    width: '100vw',
    height: '100vh',
    background: 'linear-gradient(135deg, #0a1929 0%, #1a2332 50%, #0d1b2a 100%)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    zIndex: 9999,
    overflow: 'hidden',
  },
  circuitBackground: {
    position: 'absolute',
    top: 0,
    left: 0,
    width: '100%',
    height: '100%',
    opacity: 0.3,
    pointerEvents: 'none',
  },
  circuitSvg: {
    width: '100%',
    height: '100%',
  },
  circuitLine: {
    stroke: '#00d4ff',
    strokeWidth: '1',
    fill: 'none',
    opacity: 0.5,
  },
  circuitNode: {
    fill: '#00d4ff',
    opacity: 0.8,
  },
  logoContainer: {
    position: 'relative',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    marginBottom: '3rem',
    animation: 'fadeIn 1s ease-out',
  },
  outerRing: {
    position: 'absolute',
    width: '320px',
    height: '320px',
    borderRadius: '50%',
    border: '4px solid #00bfea',
    boxShadow: '0 0 30px rgba(0, 191, 234, 0.5), inset 0 0 30px rgba(0, 191, 234, 0.3)',
  },
  logoBadge: {
    position: 'relative',
    width: '300px',
    height: '300px',
    borderRadius: '50%',
    background: 'radial-gradient(circle at 30% 30%, #3a3a3a 0%, #1a1a1a 100%)',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    justifyContent: 'center',
    boxShadow: '0 10px 50px rgba(0, 0, 0, 0.5)',
    border: '2px solid #2a2a2a',
  },
  iconGroup: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    gap: '1rem',
    marginBottom: '1rem',
  },
  icon: {
    width: '60px',
    height: '60px',
  },
  iconSmall: {
    width: '40px',
    height: '40px',
  },
  companyName: {
    fontFamily: 'Orbitron, Arial, sans-serif',
    fontSize: '3rem',
    fontWeight: '900',
    color: '#ffffff',
    margin: '0.5rem 0',
    textShadow: '0 0 20px rgba(0, 191, 234, 0.8)',
    letterSpacing: '2px',
  },
  subtitle: {
    fontFamily: 'Arial, sans-serif',
    fontSize: '0.7rem',
    fontWeight: '600',
    color: '#b0bec5',
    margin: 0,
    letterSpacing: '3px',
    textTransform: 'uppercase',
  },
  loadingContainer: {
    width: '400px',
    textAlign: 'center',
    animation: 'fadeIn 1s ease-out 0.5s backwards',
  },
  loadingBarBg: {
    width: '100%',
    height: '4px',
    background: 'rgba(255, 255, 255, 0.1)',
    borderRadius: '2px',
    overflow: 'hidden',
    marginBottom: '0.5rem',
  },
  loadingBarFill: {
    height: '100%',
    background: 'linear-gradient(90deg, #00bfea 0%, #00d4ff 100%)',
    borderRadius: '2px',
    transition: 'width 0.3s ease',
    boxShadow: '0 0 10px rgba(0, 191, 234, 0.8)',
  },
  loadingText: {
    fontFamily: 'Arial, sans-serif',
    fontSize: '0.9rem',
    color: '#90caf9',
    margin: 0,
    fontWeight: '500',
  },
  footer: {
    position: 'absolute',
    bottom: '2rem',
    textAlign: 'center',
    animation: 'fadeIn 1s ease-out 1s backwards',
  },
  footerText: {
    fontFamily: 'Arial, sans-serif',
    fontSize: '0.75rem',
    color: '#546e7a',
    margin: 0,
    letterSpacing: '1px',
  },
};

export default SplashScreen;
