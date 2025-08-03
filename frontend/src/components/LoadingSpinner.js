import React from 'react';

// Simple loading spinner component
// Not the fanciest but it works
function LoadingSpinner({ message = 'Loading...' }) {
    return (
        <div style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            padding: '60px 20px',
            color: '#aaa',
        }}>
            <div style={{
                width: '36px',
                height: '36px',
                border: '3px solid #eee',
                borderTop: '3px solid #e94560',
                borderRadius: '50%',
                animation: 'spin 0.8s linear infinite',
                marginBottom: '12px',
            }} />
            <style>{`
                @keyframes spin {
                    0% { transform: rotate(0deg); }
                    100% { transform: rotate(360deg); }
                }
            `}</style>
            <span style={{ fontSize: '14px' }}>{message}</span>
        </div>
    );
}

export default LoadingSpinner;
