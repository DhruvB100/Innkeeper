import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    card: {
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '16px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    },
    header: {
        display: 'flex',
        alignItems: 'center',
        marginBottom: '12px',
        gap: '10px',
    },
    avatar: {
        width: '40px',
        height: '40px',
        borderRadius: '50%',
        backgroundColor: '#e94560',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontWeight: 'bold',
        fontSize: '16px',
        flexShrink: 0,
    },
    authorName: {
        fontWeight: 'bold',
        color: '#333',
        textDecoration: 'none',
    },
    timestamp: {
        color: '#888',
        fontSize: '12px',
    },
    title: {
        fontSize: '18px',
        fontWeight: 'bold',
        marginBottom: '8px',
        color: '#222',
    },
    content: {
        color: '#555',
        lineHeight: '1.6',
        marginBottom: '16px',
    },
    footer: {
        display: 'flex',
        gap: '16px',
        alignItems: 'center',
        borderTop: '1px solid #eee',
        paddingTop: '12px',
    },
    actionBtn: {
        background: 'none',
        border: 'none',
        cursor: 'pointer',
        color: '#666',
        fontSize: '14px',
        display: 'flex',
        alignItems: 'center',
        gap: '4px',
        padding: '4px 8px',
        borderRadius: '4px',
        transition: 'background-color 0.2s',
    },
    likedBtn: {
        color: '#e94560',
        fontWeight: 'bold',
    },
    visibility: {
        marginLeft: 'auto',
        fontSize: '11px',
        color: '#aaa',
        backgroundColor: '#f5f5f5',
        padding: '2px 8px',
        borderRadius: '10px',
    }
};

function PostCard({ post, onDelete }) {
    const { user, isAuthenticated } = useAuth();
    const [liked, setLiked] = useState(post.user_has_liked || false);
    const [likeCount, setLikeCount] = useState(post.likes_count || 0);
    const [isLiking, setIsLiking] = useState(false);

    const handleLike = async () => {
        if (!isAuthenticated || isLiking) return;

        setIsLiking(true);
        try {
            await api.post(`/api/posts/${post.id}/like/`);
            if (liked) {
                setLiked(false);
                setLikeCount(prev => prev - 1);
            } else {
                setLiked(true);
                setLikeCount(prev => prev + 1);
            }
        } catch (error) {
            console.error('Failed to like post:', error);
            if (error.response?.status === 403) {
                alert('Your account needs to be approved before you can like posts');
            }
        } finally {
            setIsLiking(false);
        }
    };

    const handleDelete = async () => {
        if (!window.confirm('Are you sure you want to delete this post?')) return;
        try {
            await api.delete(`/api/posts/${post.id}/`);
            if (onDelete) onDelete(post.id);
        } catch (error) {
            console.error('Failed to delete post:', error);
            alert('Failed to delete post');
        }
    };

    // Format date nicely
    const formatDate = (dateString) => {
        const date = new Date(dateString);
        const now = new Date();
        const diff = (now - date) / 1000; // seconds

        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return date.toLocaleDateString();
    };

    const authorName = post.author_info?.display_name || post.author_info?.username || 'Unknown';
    const authorInitial = authorName.charAt(0).toUpperCase();

    return (
        <div style={styles.card}>
            <div style={styles.header}>
                <div style={styles.avatar}>{authorInitial}</div>
                <div>
                    <div>
                        <Link
                            to={`/profile/${post.author}`}
                            style={styles.authorName}
                        >
                            {authorName}
                        </Link>
                    </div>
                    <div style={styles.timestamp}>{formatDate(post.created_at)}</div>
                </div>
            </div>

            {post.title && <div style={styles.title}>{post.title}</div>}

            <div style={styles.content}>
                {post.content.length > 300
                    ? `${post.content.substring(0, 300)}...`
                    : post.content
                }
            </div>

            <div style={styles.footer}>
                <button
                    style={{
                        ...styles.actionBtn,
                        ...(liked ? styles.likedBtn : {})
                    }}
                    onClick={handleLike}
                    disabled={!isAuthenticated}
                    title={!isAuthenticated ? 'Login to like' : ''}
                >
                    {liked ? '♥' : '♡'} {likeCount}
                </button>

                <Link to={`/posts/${post.id}`} style={{ textDecoration: 'none' }}>
                    <button style={styles.actionBtn}>
                        💬 {post.comments_count}
                    </button>
                </Link>

                {/* Show delete button only if it's the user's post */}
                {user && user.id === post.author && (
                    <button
                        style={{ ...styles.actionBtn, color: '#e94560' }}
                        onClick={handleDelete}
                    >
                        Delete
                    </button>
                )}

                <span style={styles.visibility}>{post.visibility}</span>
            </div>
        </div>
    );
}

export default PostCard;
