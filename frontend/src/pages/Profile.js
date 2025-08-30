import React, { useState, useEffect, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import PostCard from '../components/PostCard';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    profileCard: {
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '30px',
        marginBottom: '24px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
    },
    profileHeader: {
        display: 'flex',
        alignItems: 'flex-start',
        gap: '20px',
        marginBottom: '20px',
    },
    avatar: {
        width: '80px',
        height: '80px',
        borderRadius: '50%',
        backgroundColor: '#e94560',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '32px',
        fontWeight: 'bold',
        flexShrink: 0,
    },
    profileInfo: {
        flex: 1,
    },
    displayName: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#1a1a2e',
        marginBottom: '4px',
    },
    username: {
        color: '#888',
        fontSize: '14px',
        marginBottom: '8px',
    },
    bio: {
        color: '#555',
        fontSize: '15px',
        lineHeight: '1.5',
    },
    stats: {
        display: 'flex',
        gap: '30px',
        marginTop: '16px',
    },
    stat: {
        textAlign: 'center',
    },
    statNumber: {
        fontSize: '20px',
        fontWeight: 'bold',
        color: '#1a1a2e',
    },
    statLabel: {
        fontSize: '12px',
        color: '#888',
    },
    followBtn: {
        padding: '10px 24px',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '14px',
        fontWeight: 'bold',
        border: 'none',
    },
    github: {
        color: '#e94560',
        textDecoration: 'none',
        fontSize: '14px',
        marginTop: '8px',
        display: 'block',
    }
};

function Profile() {
    const { authorId } = useParams();
    const { user, isAuthenticated } = useAuth();
    const [author, setAuthor] = useState(null);
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [postsLoading, setPostsLoading] = useState(true);
    const [isFollowing, setIsFollowing] = useState(false);
    const [followPending, setFollowPending] = useState(false);
    const [followLoading, setFollowLoading] = useState(false);
    const [pendingRequests, setPendingRequests] = useState([]);
    const [error, setError] = useState('');

    const isOwnProfile = user && user.id === authorId;

    const checkFollowStatus = useCallback(async () => {
        try {
            // Get our following list and check if this author is in it
            const response = await api.get(`/api/authors/${user.id}/following/`);
            const following = response.data.results || response.data;
            const match = following.find(f => String(f.following) === String(authorId));
            setIsFollowing(!!match);
            setFollowPending(match ? !match.is_accepted : false);
        } catch (err) {
            console.error('Failed to check follow status:', err);
        }
    }, [user, authorId]);

    const fetchPendingRequests = useCallback(async () => {
        try {
            const response = await api.get(`/api/authors/${authorId}/followers/`);
            const followers = response.data.results || response.data;
            setPendingRequests(followers.filter(f => !f.is_accepted));
        } catch (err) {
            console.error('Failed to load follow requests:', err);
        }
    }, [authorId]);

    const fetchAuthor = useCallback(async () => {
        try {
            const response = await api.get(`/api/authors/${authorId}/`);
            setAuthor(response.data);

            if (isAuthenticated && !isOwnProfile) {
                checkFollowStatus();
            }
            if (isAuthenticated && isOwnProfile) {
                fetchPendingRequests();
            }
        } catch (err) {
            console.error('Failed to load author:', err);
            setError('Author not found');
        } finally {
            setLoading(false);
        }
    }, [authorId, isAuthenticated, isOwnProfile, checkFollowStatus, fetchPendingRequests]);

    const fetchAuthorPosts = useCallback(async () => {
        try {
            const response = await api.get(`/api/authors/${authorId}/posts/`);
            const data = response.data;
            setPosts(Array.isArray(data) ? data : data.results || []);
        } catch (err) {
            console.error('Failed to load posts:', err);
        } finally {
            setPostsLoading(false);
        }
    }, [authorId]);

    useEffect(() => {
        fetchAuthor();
        fetchAuthorPosts();
    }, [fetchAuthor, fetchAuthorPosts]);

    const handleFollow = async () => {
        if (!isAuthenticated) return;
        setFollowLoading(true);

        try {
            if (isFollowing) {
                await api.delete(`/api/authors/${authorId}/follow/`);
                setIsFollowing(false);
                setFollowPending(false);
            } else {
                await api.post(`/api/authors/${authorId}/follow/`);
                setIsFollowing(true);
                setFollowPending(true);
            }
        } catch (err) {
            console.error('Failed to follow/unfollow:', err);
            alert(err.response?.data?.error || 'Failed to update follow status');
        } finally {
            setFollowLoading(false);
        }
    };

    const handleAcceptFollow = async (followerId) => {
        try {
            await api.post(`/api/authors/${authorId}/followers/${followerId}/accept/`);
            setPendingRequests(prev => prev.filter(f => String(f.follower) !== String(followerId)));
            setAuthor(prev => ({ ...prev, followers_count: prev.followers_count + 1 }));
        } catch (err) {
            alert(err.response?.data?.error || 'Failed to accept follow request');
        }
    };

    const handlePostDelete = (deletedId) => {
        setPosts(prev => prev.filter(p => p.id !== deletedId));
    };

    if (loading) {
        return <div style={{ textAlign: 'center', padding: '60px', color: '#aaa' }}>Loading profile...</div>;
    }

    if (error) {
        return (
            <div style={{ textAlign: 'center', padding: '60px' }}>
                <div style={{ color: '#e94560', marginBottom: '16px' }}>{error}</div>
                <Link to="/" style={{ color: '#e94560' }}>Go home</Link>
            </div>
        );
    }

    if (!author) return null;

    const displayName = author.display_name || author.username;

    return (
        <div>
            <div style={styles.profileCard}>
                <div style={styles.profileHeader}>
                    <div style={styles.avatar}>
                        {displayName.charAt(0).toUpperCase()}
                    </div>
                    <div style={styles.profileInfo}>
                        <div style={styles.displayName}>{displayName}</div>
                        <div style={styles.username}>@{author.username}</div>
                        {author.bio && <div style={styles.bio}>{author.bio}</div>}
                        {author.github && (
                            <a href={author.github} style={styles.github} target="_blank" rel="noreferrer">
                                GitHub Profile
                            </a>
                        )}
                    </div>

                    {isAuthenticated && !isOwnProfile && (
                        <button
                            style={{
                                ...styles.followBtn,
                                backgroundColor: isFollowing ? '#f0f0f0' : '#e94560',
                                color: isFollowing ? '#333' : 'white',
                            }}
                            onClick={handleFollow}
                            disabled={followLoading}
                        >
                            {followLoading ? '...' : isFollowing ? (followPending ? 'Requested' : 'Following') : 'Follow'}
                        </button>
                    )}

                    {isOwnProfile && (
                        <Link
                            to="/settings"
                            style={{
                                ...styles.followBtn,
                                backgroundColor: '#f0f0f0',
                                color: '#333',
                                textDecoration: 'none',
                            }}
                        >
                            Edit Profile
                        </Link>
                    )}
                </div>

                <div style={styles.stats}>
                    <div style={styles.stat}>
                        <div style={styles.statNumber}>{posts.length}</div>
                        <div style={styles.statLabel}>Posts</div>
                    </div>
                    <div style={styles.stat}>
                        <div style={styles.statNumber}>{author.followers_count || 0}</div>
                        <div style={styles.statLabel}>Followers</div>
                    </div>
                    <div style={styles.stat}>
                        <div style={styles.statNumber}>{author.following_count || 0}</div>
                        <div style={styles.statLabel}>Following</div>
                    </div>
                </div>
            </div>

            {isOwnProfile && pendingRequests.length > 0 && (
                <div style={{ backgroundColor: 'white', borderRadius: '8px', padding: '20px', marginBottom: '24px', boxShadow: '0 1px 3px rgba(0,0,0,0.1)' }}>
                    <h2 style={{ fontSize: '16px', fontWeight: 'bold', color: '#1a1a2e', marginBottom: '12px' }}>
                        Follow Requests ({pendingRequests.length})
                    </h2>
                    {pendingRequests.map(req => {
                        const name = req.follower_info?.display_name || req.follower_info?.username || 'Someone';
                        return (
                            <div key={req.id} style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', padding: '10px 0', borderBottom: '1px solid #f0f0f0' }}>
                                <span style={{ fontSize: '14px', color: '#444' }}>{name} wants to follow you</span>
                                <button
                                    onClick={() => handleAcceptFollow(req.follower)}
                                    style={{ backgroundColor: '#e94560', color: 'white', border: 'none', borderRadius: '6px', padding: '6px 16px', cursor: 'pointer', fontSize: '13px', fontWeight: 'bold' }}
                                >
                                    Accept
                                </button>
                            </div>
                        );
                    })}
                </div>
            )}

            <h2 style={{ fontSize: '18px', marginBottom: '16px', color: '#333' }}>
                Posts by {displayName}
            </h2>

            {postsLoading ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#aaa' }}>Loading posts...</div>
            ) : posts.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#aaa' }}>
                    {isOwnProfile
                        ? <><Link to="/create-post" style={{ color: '#e94560' }}>Create your first post!</Link></>
                        : 'No posts yet'
                    }
                </div>
            ) : (
                posts.map(post => (
                    <PostCard key={post.id} post={post} onDelete={handlePostDelete} />
                ))
            )}
        </div>
    );
}

export default Profile;
