import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    container: {
        marginTop: '20px',
    },
    heading: {
        fontSize: '16px',
        fontWeight: 'bold',
        marginBottom: '16px',
        color: '#333',
    },
    comment: {
        display: 'flex',
        gap: '10px',
        marginBottom: '16px',
        padding: '12px',
        backgroundColor: '#f8f9fa',
        borderRadius: '8px',
    },
    avatar: {
        width: '32px',
        height: '32px',
        borderRadius: '50%',
        backgroundColor: '#1a1a2e',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '13px',
        fontWeight: 'bold',
        flexShrink: 0,
    },
    commentBody: {
        flex: 1,
    },
    commentAuthor: {
        fontWeight: 'bold',
        fontSize: '13px',
        color: '#333',
        textDecoration: 'none',
        marginRight: '8px',
    },
    commentTime: {
        fontSize: '11px',
        color: '#aaa',
    },
    commentText: {
        fontSize: '14px',
        color: '#555',
        marginTop: '4px',
        lineHeight: '1.5',
    },
    form: {
        display: 'flex',
        gap: '10px',
        marginTop: '16px',
    },
    input: {
        flex: 1,
        padding: '10px 14px',
        border: '1px solid #ddd',
        borderRadius: '20px',
        fontSize: '14px',
        outline: 'none',
    },
    submitBtn: {
        backgroundColor: '#e94560',
        color: 'white',
        border: 'none',
        padding: '10px 20px',
        borderRadius: '20px',
        cursor: 'pointer',
        fontSize: '14px',
        whiteSpace: 'nowrap',
    },
    noComments: {
        color: '#aaa',
        fontSize: '14px',
        fontStyle: 'italic',
        textAlign: 'center',
        padding: '20px',
    }
};

function CommentSection({ postId, initialComments = [] }) {
    const { isAuthenticated } = useAuth();
    const [comments, setComments] = useState(initialComments);
    const [newComment, setNewComment] = useState('');
    const [submitting, setSubmitting] = useState(false);
    const [error, setError] = useState('');

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!newComment.trim()) return;

        setSubmitting(true);
        setError('');

        try {
            const response = await api.post(`/api/posts/${postId}/comments/`, {
                content: newComment,
                content_type: 'text/plain'
            });
            setComments(prev => [...prev, response.data]);
            setNewComment('');
        } catch (err) {
            console.error('Failed to post comment:', err);
            if (err.response?.status === 403) {
                setError('Your account needs to be approved before you can comment');
            } else {
                setError('Failed to post comment. Try again.');
            }
        } finally {
            setSubmitting(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString();
    };

    return (
        <div style={styles.container}>
            <div style={styles.heading}>
                Comments ({comments.length})
            </div>

            {comments.length === 0 ? (
                <div style={styles.noComments}>No comments yet. Be the first!</div>
            ) : (
                comments.map(comment => {
                    const authorName = comment.author_info?.display_name || comment.author_info?.username || 'Unknown';
                    return (
                        <div key={comment.id} style={styles.comment}>
                            <div style={styles.avatar}>
                                {authorName.charAt(0).toUpperCase()}
                            </div>
                            <div style={styles.commentBody}>
                                <div>
                                    <Link
                                        to={`/profile/${comment.author}`}
                                        style={styles.commentAuthor}
                                    >
                                        {authorName}
                                    </Link>
                                    <span style={styles.commentTime}>{formatDate(comment.created_at)}</span>
                                </div>
                                <div style={styles.commentText}>{comment.content}</div>
                            </div>
                        </div>
                    );
                })
            )}

            {isAuthenticated ? (
                <form onSubmit={handleSubmit} style={styles.form}>
                    <input
                        style={styles.input}
                        type="text"
                        placeholder="Write a comment..."
                        value={newComment}
                        onChange={(e) => setNewComment(e.target.value)}
                        disabled={submitting}
                    />
                    <button
                        type="submit"
                        style={styles.submitBtn}
                        disabled={submitting || !newComment.trim()}
                    >
                        {submitting ? 'Posting...' : 'Post'}
                    </button>
                </form>
            ) : (
                <div style={{ ...styles.noComments, marginTop: '16px' }}>
                    <Link to="/login" style={{ color: '#e94560' }}>Login</Link> to comment
                </div>
            )}

            {error && <div style={{ color: 'red', fontSize: '13px', marginTop: '8px' }}>{error}</div>}
        </div>
    );
}

export default CommentSection;
