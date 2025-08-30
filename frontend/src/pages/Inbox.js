import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const styles = {
    heading: {
        fontSize: '24px',
        fontWeight: 'bold',
        color: '#1a1a2e',
        marginBottom: '20px',
    },
    item: {
        backgroundColor: 'white',
        borderRadius: '8px',
        padding: '16px 20px',
        marginBottom: '10px',
        boxShadow: '0 1px 3px rgba(0,0,0,0.08)',
        display: 'flex',
        alignItems: 'flex-start',
        gap: '12px',
    },
    unread: {
        borderLeft: '3px solid #e94560',
    },
    icon: {
        fontSize: '20px',
        flexShrink: 0,
        marginTop: '2px',
    },
    body: {
        flex: 1,
    },
    type: {
        fontSize: '11px',
        textTransform: 'uppercase',
        color: '#aaa',
        fontWeight: 'bold',
        marginBottom: '4px',
        letterSpacing: '0.5px',
    },
    text: {
        fontSize: '14px',
        color: '#444',
        lineHeight: '1.5',
    },
    time: {
        fontSize: '11px',
        color: '#bbb',
        marginTop: '4px',
    },
    clearBtn: {
        backgroundColor: 'white',
        border: '1px solid #ddd',
        padding: '8px 16px',
        borderRadius: '6px',
        cursor: 'pointer',
        fontSize: '13px',
        color: '#666',
        marginBottom: '16px',
    },
    empty: {
        textAlign: 'center',
        padding: '60px 20px',
        color: '#aaa',
    }
};

const typeIcons = {
    post: '📝',
    like: '♥',
    comment: '💬',
    follow: '👤',
};

function Inbox() {
    const { user } = useAuth();
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchInbox = useCallback(async () => {
        try {
            const response = await api.get(`/api/authors/${user.id}/inbox/`);
            setItems(response.data.items || []);
        } catch (err) {
            console.error('Failed to load inbox:', err);
        } finally {
            setLoading(false);
        }
    }, [user]);

    useEffect(() => {
        if (user) {
            fetchInbox();
        }
    }, [user, fetchInbox]);

    const clearInbox = async () => {
        if (!window.confirm('Clear all inbox notifications?')) return;
        try {
            await api.delete(`/api/authors/${user.id}/inbox/`);
            setItems([]);
        } catch (err) {
            console.error('Failed to clear inbox:', err);
        }
    };

    const formatTime = (dateStr) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = (now - date) / 1000;
        if (diff < 60) return 'just now';
        if (diff < 3600) return `${Math.floor(diff / 60)}m ago`;
        if (diff < 86400) return `${Math.floor(diff / 3600)}h ago`;
        return date.toLocaleDateString();
    };

    const getItemText = (item) => {
        const content = item.content || {};
        const authorName = content.author?.display_name || content.author?.username || 'Someone';

        switch (item.item_type) {
            case 'post':
                return `${authorName} posted: "${content.title || content.content?.substring(0, 60) || '...'}"`;
            case 'like':
                return `${authorName} liked your post`;
            case 'comment':
                return `${authorName} commented: "${content.content?.substring(0, 60) || '...'}"`;
            case 'follow':
                return `${authorName} sent you a follow request`;
            default:
                return 'New notification';
        }
    };

    if (loading) {
        return <div style={{ textAlign: 'center', padding: '60px', color: '#aaa' }}>Loading inbox...</div>;
    }

    return (
        <div>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                <h1 style={styles.heading}>Inbox</h1>
                {items.length > 0 && (
                    <button style={styles.clearBtn} onClick={clearInbox}>
                        Clear all
                    </button>
                )}
            </div>

            {items.length === 0 ? (
                <div style={styles.empty}>
                    <div style={{ fontSize: '40px', marginBottom: '12px' }}>📭</div>
                    <div>Your inbox is empty</div>
                </div>
            ) : (
                items.map(item => (
                    <div
                        key={item.id}
                        style={{
                            ...styles.item,
                            ...(item.is_read ? {} : styles.unread),
                        }}
                    >
                        <span style={styles.icon}>
                            {typeIcons[item.item_type] || '🔔'}
                        </span>
                        <div style={styles.body}>
                            <div style={styles.type}>{item.item_type}</div>
                            <div style={styles.text}>{getItemText(item)}</div>
                            <div style={styles.time}>{formatTime(item.created_at)}</div>
                        </div>
                    </div>
                ))
            )}
        </div>
    );
}

export default Inbox;
