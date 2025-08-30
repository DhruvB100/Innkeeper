import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    container: {
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '30px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    },
    heading: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#1a1a2e',
        marginBottom: '24px',
    },
    formGroup: {
        marginBottom: '20px',
    },
    label: {
        display: 'block',
        marginBottom: '8px',
        fontSize: '14px',
        fontWeight: '600',
        color: '#444',
    },
    input: {
        width: '100%',
        padding: '12px',
        border: '1px solid #ddd',
        borderRadius: '6px',
        fontSize: '15px',
        outline: 'none',
    },
    textarea: {
        width: '100%',
        padding: '12px',
        border: '1px solid #ddd',
        borderRadius: '6px',
        fontSize: '15px',
        outline: 'none',
        resize: 'vertical',
        minHeight: '200px',
        fontFamily: 'inherit',
        lineHeight: '1.6',
    },
    select: {
        padding: '11px',
        border: '1px solid #ddd',
        borderRadius: '6px',
        fontSize: '14px',
        outline: 'none',
        backgroundColor: 'white',
    },
    row: {
        display: 'flex',
        gap: '16px',
    },
    submitBtn: {
        backgroundColor: '#e94560',
        color: 'white',
        border: 'none',
        padding: '13px 30px',
        borderRadius: '6px',
        fontSize: '16px',
        fontWeight: 'bold',
        cursor: 'pointer',
    },
    cancelBtn: {
        backgroundColor: 'white',
        color: '#666',
        border: '1px solid #ddd',
        padding: '13px 24px',
        borderRadius: '6px',
        fontSize: '16px',
        cursor: 'pointer',
        marginLeft: '12px',
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
    hint: {
        fontSize: '12px',
        color: '#aaa',
        marginTop: '4px',
    }
};

function CreatePost() {
    const navigate = useNavigate();
    const { isApproved } = useAuth();
    const [formData, setFormData] = useState({
        title: '',
        content: '',
        content_type: 'text/plain',
        visibility: 'PUBLIC',
        categories: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    // If account isn't approved yet, show message
    if (!isApproved) {
        return (
            <div style={{ ...styles.container, textAlign: 'center', padding: '60px' }}>
                <h2 style={{ color: '#1a1a2e', marginBottom: '16px' }}>Account Pending Approval</h2>
                <p style={{ color: '#888' }}>
                    Your account is waiting for admin approval. Once approved, you'll be able to create posts.
                </p>
            </div>
        );
    }

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (!formData.content.trim()) {
            setError('Content is required');
            return;
        }

        setLoading(true);
        try {
            const response = await api.post('/api/posts/', formData);
            // Redirect to the new post
            navigate(`/posts/${response.data.id}`);
        } catch (err) {
            console.error('Failed to create post:', err);
            if (err.response?.data) {
                const errors = err.response.data;
                if (typeof errors === 'object') {
                    setError(Object.values(errors).flat().join(', '));
                } else {
                    setError(String(errors));
                }
            } else {
                setError('Failed to create post. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={styles.container}>
            <h1 style={styles.heading}>Create New Post</h1>

            {error && <div style={styles.error}>{error}</div>}

            <form onSubmit={handleSubmit}>
                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="title">Title (optional)</label>
                    <input
                        style={styles.input}
                        type="text"
                        id="title"
                        name="title"
                        value={formData.title}
                        onChange={handleChange}
                        placeholder="Give your post a title..."
                    />
                </div>

                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="content">Content *</label>
                    <textarea
                        style={styles.textarea}
                        id="content"
                        name="content"
                        value={formData.content}
                        onChange={handleChange}
                        placeholder="What's on your mind?"
                        required
                    />
                </div>

                <div style={{ ...styles.row, marginBottom: '20px' }}>
                    <div style={styles.formGroup}>
                        <label style={styles.label}>Format</label>
                        <select
                            style={styles.select}
                            name="content_type"
                            value={formData.content_type}
                            onChange={handleChange}
                        >
                            <option value="text/plain">Plain Text</option>
                            <option value="text/markdown">Markdown</option>
                        </select>
                    </div>

                    <div style={styles.formGroup}>
                        <label style={styles.label}>Who can see this?</label>
                        <select
                            style={styles.select}
                            name="visibility"
                            value={formData.visibility}
                            onChange={handleChange}
                        >
                            <option value="PUBLIC">Public (everyone)</option>
                            <option value="FRIENDS">Friends only</option>
                            <option value="PRIVATE">Private (only me)</option>
                        </select>
                    </div>
                </div>

                <div style={styles.formGroup}>
                    <label style={styles.label} htmlFor="categories">Tags</label>
                    <input
                        style={styles.input}
                        type="text"
                        id="categories"
                        name="categories"
                        value={formData.categories}
                        onChange={handleChange}
                        placeholder="tech, programming, life (comma separated)"
                    />
                    <div style={styles.hint}>Separate tags with commas</div>
                </div>

                <div>
                    <button
                        type="submit"
                        style={{
                            ...styles.submitBtn,
                            opacity: loading ? 0.7 : 1,
                            cursor: loading ? 'not-allowed' : 'pointer',
                        }}
                        disabled={loading}
                    >
                        {loading ? 'Publishing...' : 'Publish Post'}
                    </button>
                    <button
                        type="button"
                        style={styles.cancelBtn}
                        onClick={() => navigate('/')}
                    >
                        Cancel
                    </button>
                </div>
            </form>
        </div>
    );
}

export default CreatePost;
