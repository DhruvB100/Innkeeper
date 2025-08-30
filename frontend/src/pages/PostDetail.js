import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import CommentSection from '../components/CommentSection';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    post: {
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '30px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        marginBottom: '20px',
    },
    header: {
        display: 'flex',
        alignItems: 'center',
        gap: '12px',
        marginBottom: '20px',
    },
    avatar: {
        width: '48px',
        height: '48px',
        borderRadius: '50%',
        backgroundColor: '#e94560',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '20px',
        fontWeight: 'bold',
    },
    authorName: {
        fontWeight: 'bold',
        color: '#333',
        textDecoration: 'none',
        fontSize: '16px',
    },
    timestamp: {
        color: '#aaa',
        fontSize: '13px',
    },
    title: {
        fontSize: '26px',
        fontWeight: 'bold',
        color: '#1a1a2e',
        marginBottom: '16px',
        lineHeight: '1.3',
    },
    content: {
        color: '#444',
        lineHeight: '1.8',
        fontSize: '16px',
        whiteSpace: 'pre-wrap',
    },
    actions: {
        display: 'flex',
        gap: '16px',
        marginTop: '24px',
        paddingTop: '16px',
        borderTop: '1px solid #eee',
    },
    actionBtn: {
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        color: '#666',
        fontSize: '16px',
        display: 'flex',
        alignItems: 'center',
        gap: '6px',
        padding: '6px 12px',
        borderRadius: '6px',
    },
    categories: {
        display: 'flex',
        flexWrap: 'wrap',
        gap: '8px',
        marginTop: '16px',
    },
    tag: {
        backgroundColor: '#f0f0f0',
        padding: '4px 12px',
        borderRadius: '14px',
        fontSize: '12px',
        color: '#666',
    },
    deleteBtn: {
        marginLeft: 'auto',
        color: '#e94560',
        background: 'none',
        border: '1px solid #e94560',
        padding: '6px 14px',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '13px',
    }
};

function PostDetail() {
    const { postId } = useParams();
    const navigate = useNavigate();
    const { user, isAuthenticated } = useAuth();
    const [post, setPost] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [liked, setLiked] = useState(false);
    const [likeCount, setLikeCount] = useState(0);

    const fetchPost = useCallback(async () => {
        try {
            const response = await api.get(`/api/posts/${postId}/`);
            setPost(response.data);
            setLiked(response.data.user_has_liked);
            setLikeCount(response.data.likes_count);
        } catch (err) {
            console.error('Failed to load post:', err);
            if (err.response?.status === 404) {
                setError('Post not found');
            } else {
                setError('Failed to load post');
            }
        } finally {
            setLoading(false);
        }
    }, [postId]);

    useEffect(() => {
        fetchPost();
    }, [fetchPost]);

    const handleLike = async () => {
        if (!isAuthenticated) {
            navigate('/login');
            return;
        }
        try {
            await api.post(`/api/posts/${postId}/like/`);
            if (liked) {
                setLiked(false);
                setLikeCount(prev => prev - 1);
            } else {
                setLiked(true);
                setLikeCount(prev => prev + 1);
            }
        } catch (err) {
            console.error('Failed to like:', err);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Delete this post? This cannot be undone.')) return;
        try {
            await api.delete(`/api/posts/${postId}/`);
            navigate('/');
        } catch (err) {
            console.error('Failed to delete:', err);
            alert('Failed to delete post');
        }
    };

    if (loading) {
        return <div style={{ textAlign: 'center', padding: '60px', color: '#aaa' }}>Loading...</div>;
    }

    if (error) {
        return (
            <div style={{ textAlign: 'center', padding: '60px' }}>
                <div style={{ color: '#e94560', marginBottom: '16px', fontSize: '20px' }}>{error}</div>
                <Link to="/" style={{ color: '#e94560' }}>← Go back home</Link>
            </div>
        );
    }

    if (!post) return null;

    const authorName = post.author_info?.display_name || post.author_info?.username || 'Unknown';
    const isMyPost = user && user.id === post.author;

    const formatDate = (dateStr) => {
        return new Date(dateStr).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    };

    return (
        <div>
            <div style={{ marginBottom: '16px' }}>
                <Link to="/" style={{ color: '#e94560', textDecoration: 'none', fontSize: '14px' }}>
                    ← Back to posts
                </Link>
            </div>

            <div style={styles.post}>
                <div style={styles.header}>
                    <div style={styles.avatar}>{authorName.charAt(0).toUpperCase()}</div>
                    <div>
                        <Link to={`/profile/${post.author}`} style={styles.authorName}>
                            {authorName}
                        </Link>
                        <div style={styles.timestamp}>{formatDate(post.created_at)}</div>
                    </div>
                </div>

                {post.title && <h1 style={styles.title}>{post.title}</h1>}

                <div style={styles.content}>{post.content}</div>

                {post.categories_list && post.categories_list.length > 0 && (
                    <div style={styles.categories}>
                        {post.categories_list.map(tag => (
                            <span key={tag} style={styles.tag}>#{tag}</span>
                        ))}
                    </div>
                )}

                <div style={styles.actions}>
                    <button
                        style={{
                            ...styles.actionBtn,
                            color: liked ? '#e94560' : '#666',
                        }}
                        onClick={handleLike}
                    >
                        {liked ? '♥' : '♡'} {likeCount} {likeCount === 1 ? 'Like' : 'Likes'}
                    </button>

                    {isMyPost && (
                        <button style={styles.deleteBtn} onClick={handleDelete}>
                            Delete Post
                        </button>
                    )}
                </div>
            </div>

            <div style={{
                backgroundColor: 'white',
                borderRadius: '8px',
                padding: '24px',
                boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
            }}>
                <CommentSection
                    postId={postId}
                    initialComments={post.comments || []}
                />
            </div>
        </div>
    );
}

export default PostDetail;
