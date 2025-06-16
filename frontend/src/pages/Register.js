import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import api from '../utils/api';

const styles = {
    container: {
        maxWidth: '420px',
        margin: '40px auto',
        padding: '40px',
        backgroundColor: 'white',
        borderRadius: '8px',
        boxShadow: '0 2px 10px rgba(0,0,0,0.1)',
    },
    heading: {
        fontSize: '26px',
        fontWeight: 'bold',
        marginBottom: '8px',
        color: '#1a1a2e',
    },
    subtitle: {
        color: '#888',
        marginBottom: '28px',
        fontSize: '14px',
    },
    formGroup: {
        marginBottom: '18px',
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
        padding: '11px',
        border: '1px solid #ddd',
        borderRadius: '6px',
        fontSize: '15px',
        outline: 'none',
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
        marginTop: '8px',
    },
    error: {
        backgroundColor: '#fee',
        border: '1px solid #fcc',
        color: '#c33',
        padding: '12px',
        borderRadius: '6px',
        marginBottom: '18px',
        fontSize: '14px',
    },
    success: {
        backgroundColor: '#efe',
        border: '1px solid #cfc',
        color: '#363',
        padding: '16px',
        borderRadius: '6px',
        marginBottom: '18px',
        fontSize: '14px',
        lineHeight: '1.5',
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
    },
    note: {
        fontSize: '12px',
        color: '#aaa',
        marginTop: '4px',
    }
};

function Register() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        display_name: '',
        password: '',
        password2: '',
    });
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [loading, setLoading] = useState(false);

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setSuccess('');

        // Basic client-side validation
        if (formData.password !== formData.password2) {
            setError("Passwords don't match");
            return;
        }
        if (formData.password.length < 6) {
            setError("Password must be at least 6 characters");
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/api/auth/register/', formData);
            setSuccess(
                `Account created! ${response.data.message || 'An admin will need to approve your account before you can log in.'}`
            );
            // Redirect to login after 3 seconds
            setTimeout(() => navigate('/login'), 3000);
        } catch (err) {
            console.error('Registration error:', err);
            if (err.response?.data) {
                // Django returns field-specific errors
                const errors = err.response.data;
                const errorMessages = Object.entries(errors)
                    .map(([field, msgs]) => `${field}: ${Array.isArray(msgs) ? msgs.join(', ') : msgs}`)
                    .join('\n');
                setError(errorMessages);
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    if (success) {
        return (
            <div style={styles.container}>
                <div style={styles.success}>
                    <strong>Account created!</strong>
                    <br /><br />
                    {success}
                    <br /><br />
                    Redirecting to login...
                </div>
            </div>
        );
    }

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>Create account</h1>
            <p style={styles.subtitle}>Join the Innkeeper network</p>

            {error && (
                <div style={styles.error}>
                    {error.split('\n').map((line, i) => (
                        <div key={i}>{line}</div>
                    ))}
                </div>
            )}

            <form onSubmit={handleSubmit}>
                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="username">Username *</label>
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
                    <label style={styles.label} htmlFor="display_name">Display Name</label>
                    <input
                        style={styles.input}
                        type="text"
                        id="display_name"
                        name="display_name"
                        value={formData.display_name}
                        onChange={handleChange}
                        placeholder="How should people see your name?"
                    />
                </div>

                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="email">Email *</label>
                    <input
                        style={styles.input}
                        type="email"
                        id="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="password">Password *</label>
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

                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="password2">Confirm Password *</label>
                    <input
                        style={styles.input}
                        type="password"
                        id="password2"
                        name="password2"
                        value={formData.password2}
                        onChange={handleChange}
                        required
                    />
                </div>

                <div style={styles.note}>
                    Note: New accounts need admin approval before you can post.
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
                    {loading ? 'Creating account...' : 'Create Account'}
                </button>
            </form>

            <div style={styles.footer}>
                Already have an account?{' '}
                <Link to="/login" style={styles.link}>Login</Link>
            </div>
        </div>
    );
}

export default Register;
