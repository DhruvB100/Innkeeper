import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const styles = {
    nav: {
        backgroundColor: '#1a1a2e',
        color: 'white',
        padding: '0 20px',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        height: '60px',
        boxShadow: '0 2px 4px rgba(0,0,0,0.3)',
    },
    logo: {
        color: 'white',
        textDecoration: 'none',
        fontSize: '22px',
        fontWeight: 'bold',
        letterSpacing: '1px',
    },
    navLinks: {
        display: 'flex',
        alignItems: 'center',
        gap: '20px',
        listStyle: 'none',
    },
    link: {
        color: '#ccc',
        textDecoration: 'none',
        fontSize: '14px',
        transition: 'color 0.2s',
    },
    button: {
        backgroundColor: '#e94560',
        color: 'white',
        border: 'none',
        padding: '8px 16px',
        borderRadius: '4px',
        cursor: 'pointer',
        fontSize: '14px',
    },
    username: {
        color: '#e94560',
        fontWeight: 'bold',
    }
};

function Navbar() {
    const { user, isAuthenticated, logout } = useAuth();
    const navigate = useNavigate();

    const handleLogout = () => {
        logout();
        navigate('/login');
    };

    return (
        <nav style={styles.nav}>
            <Link to="/" style={styles.logo}>Innkeeper</Link>

            <ul style={styles.navLinks}>
                <li>
                    <Link to="/" style={styles.link}>Home</Link>
                </li>
                <li>
                    <Link to="/authors" style={styles.link}>People</Link>
                </li>

                {isAuthenticated ? (
                    <>
                        <li>
                            <Link to="/inbox" style={styles.link}>Inbox</Link>
                        </li>
                        <li>
                            <Link to="/create-post" style={styles.link}>+ Post</Link>
                        </li>
                        <li>
                            <Link
                                to={`/profile/${user.id}`}
                                style={{ ...styles.link, ...styles.username }}
                            >
                                {user.display_name || user.username}
                            </Link>
                        </li>
                        <li>
                            <button style={styles.button} onClick={handleLogout}>
                                Logout
                            </button>
                        </li>
                    </>
                ) : (
                    <>
                        <li>
                            <Link to="/login" style={styles.link}>Login</Link>
                        </li>
                        <li>
                            <Link to="/register">
                                <button style={styles.button}>Sign Up</button>
                            </Link>
                        </li>
                    </>
                )}
            </ul>
        </nav>
    );
}

export default Navbar;
