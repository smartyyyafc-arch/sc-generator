import React, { useState, useEffect } from 'react';

export default function Toast({ message, type = 'info', onClose, autoClose = true, autoCloseDelay = 5000 }) {
  const [isVisible, setIsVisible] = useState(true);

  useEffect(() => {
    if (!autoClose) return;

    const timer = setTimeout(() => {
      setIsVisible(false);
      onClose?.();
    }, autoCloseDelay);

    return () => clearTimeout(timer);
  }, [autoClose, autoCloseDelay, onClose]);

  if (!isVisible) return null;

  const getStyles = () => {
    const baseStyle = {
      position: 'fixed',
      bottom: '2rem',
      right: '2rem',
      minWidth: '300px',
      maxWidth: '400px',
      padding: '1rem 1.5rem',
      borderRadius: '8px',
      fontSize: '0.95rem',
      fontWeight: '500',
      zIndex: 10000,
      boxShadow: '0 8px 32px rgba(0, 0, 0, 0.4)',
      animation: 'slideIn 0.3s ease-out',
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      gap: '1rem',
      backdropFilter: 'blur(10px)',
    };

    const typeStyles = {
      success: {
        background: 'linear-gradient(135deg, rgba(76, 175, 80, 0.9) 0%, rgba(56, 142, 60, 0.9) 100%)',
        border: '1px solid rgba(76, 175, 80, 0.6)',
        color: '#e8f5e9',
      },
      error: {
        background: 'linear-gradient(135deg, rgba(244, 67, 54, 0.9) 0%, rgba(211, 47, 47, 0.9) 100%)',
        border: '1px solid rgba(244, 67, 54, 0.6)',
        color: '#ffebee',
      },
      warning: {
        background: 'linear-gradient(135deg, rgba(255, 152, 0, 0.9) 0%, rgba(245, 127, 23, 0.9) 100%)',
        border: '1px solid rgba(255, 152, 0, 0.6)',
        color: '#fff3e0',
      },
      info: {
        background: 'linear-gradient(135deg, rgba(33, 150, 243, 0.9) 0%, rgba(21, 101, 192, 0.9) 100%)',
        border: '1px solid rgba(33, 150, 243, 0.6)',
        color: '#e3f2fd',
      },
    };

    return { ...baseStyle, ...typeStyles[type] };
  };

  const getIcon = () => {
    switch (type) {
      case 'success':
        return '✓';
      case 'error':
        return '✕';
      case 'warning':
        return '!';
      case 'info':
      default:
        return 'ℹ';
    }
  };

  return (
    <>
      <style>
        {`
          @keyframes slideIn {
            from {
              transform: translateX(400px);
              opacity: 0;
            }
            to {
              transform: translateX(0);
              opacity: 1;
            }
          }
        `}
      </style>
      <div style={getStyles()}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.8rem', flex: 1 }}>
          <span style={{ fontSize: '1.2rem', fontWeight: 'bold' }}>{getIcon()}</span>
          <span>{message}</span>
        </div>
        <button
          onClick={() => {
            setIsVisible(false);
            onClose?.();
          }}
          style={{
            background: 'rgba(255, 255, 255, 0.2)',
            border: 'none',
            color: 'inherit',
            cursor: 'pointer',
            fontSize: '1.2rem',
            padding: '0.25rem 0.5rem',
            borderRadius: '4px',
            transition: 'background 0.2s ease',
          }}
          onMouseEnter={(e) => (e.target.style.background = 'rgba(255, 255, 255, 0.3)')}
          onMouseLeave={(e) => (e.target.style.background = 'rgba(255, 255, 255, 0.2)')}
        >
          ×
        </button>
      </div>
    </>
  );
}
