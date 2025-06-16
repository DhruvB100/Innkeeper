import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const styles = {
    container: {
        maxWidth: '400px',
        margin: '60px auto',
        padding: '40px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    },
    heading: {
        fontSize: '28px',
        fontWeight: 'bold',
        marginBottom: '8px',
        color: '#1a1a2e',
    },
    subtitle: {
        color: '#888',
        marginBottom: '30px',
        fontSize: '14px',
    },
    formGroup: {
        marginBottom: '20px',
    },
    label: {
        display: 'block',
        marginBottom: '6px',
        fontSize: '14px',
        fontWeight: '500',
        color: '#444',
    },
    input: {
        width: '100%',
        padding: '12px',
        border: '1px solid #ddd',
        borderRadius: '6px',
        fontSize: '15px',
        outline: 'none',
        transition: 'border-color 0.2s',
    },
    button: {
        width: '100%',
        padding: '13px',
        backgroundColor: '#e94560',
        color: 'white',
        border: 'none',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: 'bold',
        cursor: 'pointer',
        marginTop: '10px',
    },
    error: {
        backgroundColor: '#fee',
        border: '1px solid #fcc',
        color: '#c33',
        padding: '12px',
        borderRadius: '6px',
        marginBottom: '20px',
        fontSize: '14px',
    },
    footer: {
        textAlign: 'center',
        marginTop: '24px',
        fontSize: '14px',
        color: '#666',
    },
    link: {
        color: '#e94560',
        textDecoration: 'none',
    }
};

function Login() {
    const navigate = useNavigate();
    const { login } = useAuth();
    const [formData, setFormData] = useState({ username: '', password: '' });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await login(formData.username, formData.password);
            navigate('/');
        } catch (err) {
            console.error('Login error:', err);
            if (err.response?.status === 401) {
                setError('Invalid username or password');
            } else if (err.response?.data?.detail) {
                setError(err.response.data.detail);
            } else {
                setError('Something went wrong. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>Welcome back</h1>
            <p style={styles.subtitle}>Log in to your Innkeeper account</p>

            {error && <div style={styles.error}>{error}</div>}

            <form onSubmit={handleSubmit}>
                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="username">Username</label>
                    <input
                        style={styles.input}
                        type="text"
                        id="username"
                        name="username"
                        value={formData.username}
                        onChange={handleChange}
                        required
                        autoFocus
                    />
                </div>

                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="password">Password</label>
                    <input
                        style={styles.input}
                        type="password"
                        id="password"
                        name="password"
                        value={formData.password}
                        onChange={handleChange}
                        required
                    />
                </div>

                <button
                    type="submit"
                    style={{
                        ...styles.button,
                        opacity: loading ? 0.7 : 1,
                        cursor: loading ? 'not-allowed' : 'pointer',
                    }}
                    disabled={loading}
                >
                    {loading ? 'Logging in...' : 'Login'}
                </button>
            </form>

            <div style={styles.footer}>
                Don't have an account?{' '}
                <Link to="/register" style={styles.link}>Sign up</Link>
            </div>
        </div>
    );
}

export default Login;
