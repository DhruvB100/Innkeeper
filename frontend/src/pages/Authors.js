import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    heading: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#1a1a2e',
        marginBottom: '20px',
    },
    grid: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
        gap: '16px',
    },
    card: {
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '20px',
        textAlign: 'center',
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
        textDecoration: 'none',
        color: 'inherit',
        display: 'block',
        transition: 'transform 0.1s',
    },
    avatar: {
        width: '60px',
        height: '60px',
        borderRadius: '50%',
        backgroundColor: '#e94560',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        color: 'white',
        fontSize: '24px',
        fontWeight: 'bold',
        margin: '0 auto 12px',
    },
    name: {
        fontWeight: 'bold',
        fontSize: '15px',
        color: '#1a1a2e',
        marginBottom: '4px',
    },
    username: {
        color: '#888',
        fontSize: '13px',
        marginBottom: '8px',
    },
    bio: {
        color: '#666',
        fontSize: '13px',
        lineHeight: '1.4',
        maxHeight: '40px',
        overflow: 'hidden',
    },
    loading: {
        textAlign: 'center',
        padding: '60px',
        color: '#aaa',
    },
    search: {
        width: '100%',
        padding: '12px 16px',
        border: '1px solid #ddd',
        borderRadius: '8px',
        fontSize: '15px',
        outline: 'none',
        marginBottom: '20px',
    }
};

function Authors() {
    const { user } = useAuth();
    const [authors, setAuthors] = useState([]);
    const [loading, setLoading] = useState(true);
    const [search, setSearch] = useState('');

    useEffect(() => {
        fetchAuthors();
    }, []);

    const fetchAuthors = async () => {
        try {
            const response = await api.get('/api/authors/');
            const data = response.data;
            setAuthors(Array.isArray(data) ? data : data.results || []);
        } catch (err) {
            console.error('Failed to load authors:', err);
        } finally {
            setLoading(false);
        }
    };

    // Simple client-side filtering
    const filteredAuthors = authors.filter(author => {
        if (!search) return true;
        const s = search.toLowerCase();
        const name = (author.display_name || author.username || '').toLowerCase();
        return name.includes(s) || author.username.toLowerCase().includes(s);
    });

    if (loading) {
        return <div style={styles.loading}>Loading authors...</div>;
    }

    return (
        <div>
            <h1 style={styles.heading}>People on Innkeeper</h1>

            <input
                style={styles.search}
                type="text"
                placeholder="Search by name or username..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
            />

            {filteredAuthors.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px', color: '#aaa' }}>
                    {search ? 'No authors matching your search' : 'No authors yet'}
                </div>
            ) : (
                <div style={styles.grid}>
                    {filteredAuthors.map(author => {
                        const displayName = author.display_name || author.username;
                        const isMe = user && user.id === author.id;
                        return (
                            <Link
                                key={author.id}
                                to={`/profile/${author.id}`}
                                style={styles.card}
                            >
                                <div style={{
                                    ...styles.avatar,
                                    backgroundColor: isMe ? '#1a1a2e' : '#e94560'
                                }}>
                                    {displayName.charAt(0).toUpperCase()}
                                </div>
                                <div style={styles.name}>{displayName}</div>
                                <div style={styles.username}>@{author.username}</div>
                                {author.bio && (
                                    <div style={styles.bio}>{author.bio}</div>
                                )}
                            </Link>
                        );
                    })}
                </div>
            )}
        </div>
    );
}

export default Authors;
