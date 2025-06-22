import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import PostCard from '../components/PostCard';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    header: {
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        marginBottom: '24px',
    },
    heading: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#1a1a2e',
    },
    createBtn: {
        backgroundColor: '#e94560',
        color: 'white',
        textDecoration: 'none',
        padding: '10px 20px',
        borderRadius: '6px',
        fontSize: '14px',
        fontWeight: 'bold',
    },
    tabs: {
        display: 'flex',
        gap: '0',
        marginBottom: '20px',
        borderBottom: '2px solid #eee',
    },
    tab: {
        padding: '10px 20px',
        cursor: 'pointer',
        border: 'none',
        background: 'none',
        fontSize: '15px',
        color: '#888',
        borderBottom: '2px solid transparent',
        marginBottom: '-2px',
        transition: 'all 0.2s',
    },
    activeTab: {
        color: '#e94560',
        borderBottom: '2px solid #e94560',
        fontWeight: 'bold',
    },
    loading: {
        textAlign: 'center',
        padding: '60px',
        color: '#aaa',
    },
    empty: {
        textAlign: 'center',
        padding: '60px 20px',
        color: '#aaa',
    },
    emptyLink: {
        color: '#e94560',
        textDecoration: 'none',
    }
};

function Home() {
    const { isAuthenticated } = useAuth();
    const [posts, setPosts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [activeTab, setActiveTab] = useState('public');  // 'public' or 'feed'
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);

    useEffect(() => {
        loadPosts(1);
    }, [activeTab]);

    const loadPosts = async (pageNum = 1) => {
        setLoading(true);
        setError('');
        try {
            let url = activeTab === 'feed' && isAuthenticated
                ? '/api/feed/'
                : `/api/posts/?page=${pageNum}`;

            const response = await api.get(url);

            const data = response.data;
            const newPosts = Array.isArray(data) ? data : data.results || [];

            if (pageNum === 1) {
                setPosts(newPosts);
            } else {
                setPosts(prev => [...prev, ...newPosts]);
            }

            // Check if there are more pages
            if (data.next) {
                setHasMore(true);
            } else {
                setHasMore(false);
            }
            setPage(pageNum);
        } catch (err) {
            console.error('Failed to load posts:', err);
            setError('Failed to load posts. Please refresh the page.');
        } finally {
            setLoading(false);
        }
    };

    const handleLoadMore = () => {
        loadPosts(page + 1);
    };

    const handlePostDelete = (deletedPostId) => {
        setPosts(prev => prev.filter(p => p.id !== deletedPostId));
    };

    return (
        <div>
            <div style={styles.header}>
                <h1 style={styles.heading}>
                    {activeTab === 'feed' ? 'Your Feed' : 'Public Posts'}
                </h1>
                {isAuthenticated && (
                    <Link to="/create-post" style={styles.createBtn}>
                        + New Post
                    </Link>
                )}
            </div>

            {isAuthenticated && (
                <div style={styles.tabs}>
                    <button
                        style={{
                            ...styles.tab,
                            ...(activeTab === 'public' ? styles.activeTab : {})
                        }}
                        onClick={() => setActiveTab('public')}
                    >
                        Public
                    </button>
                    <button
                        style={{
                            ...styles.tab,
                            ...(activeTab === 'feed' ? styles.activeTab : {})
                        }}
                        onClick={() => setActiveTab('feed')}
                    >
                        Following
                    </button>
                </div>
            )}

            {error && (
                <div style={{ color: 'red', marginBottom: '16px' }}>{error}</div>
            )}

            {loading && posts.length === 0 ? (
                <div style={styles.loading}>Loading posts...</div>
            ) : posts.length === 0 ? (
                <div style={styles.empty}>
                    {activeTab === 'feed'
                        ? <>
                            No posts in your feed yet.{' '}
                            <Link to="/authors" style={styles.emptyLink}>Follow some people</Link>{' '}
                            to see their posts here!
                          </>
                        : <>
                            No public posts yet.{' '}
                            {isAuthenticated
                                ? <Link to="/create-post" style={styles.emptyLink}>Create the first one!</Link>
                                : <Link to="/register" style={styles.emptyLink}>Sign up to post!</Link>
                            }
                          </>
                    }
                </div>
            ) : (
                <>
                    {posts.map(post => (
                        <PostCard
                            key={post.id}
                            post={post}
                            onDelete={handlePostDelete}
                        />
                    ))}

                    {hasMore && !loading && activeTab !== 'feed' && (
                        <div style={{ textAlign: 'center', padding: '20px' }}>
                            <button
                                onClick={handleLoadMore}
                                style={{
                                    padding: '10px 30px',
                                    border: '1px solid #ddd',
                                    borderRadius: '6px',
                                    background: 'white',
                                    cursor: 'pointer',
                                    color: '#666',
                                }}
                            >
                                Load More
                            </button>
                        </div>
                    )}

                    {loading && posts.length > 0 && (
                        <div style={{ textAlign: 'center', padding: '20px', color: '#aaa' }}>
                            Loading...
                        </div>
                    )}
                </>
            )}
        </div>
    );
}

export default Home;
