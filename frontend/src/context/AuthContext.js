import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import jwtDecode from 'jwt-decode';
import api from '../utils/api';

// Create the context
const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);  // loading while we check if user is logged in

    const fetchCurrentUser = useCallback(async (token) => {
        try {
            const response = await api.get('/api/auth/me/');
            setUser(response.data);
        } catch (error) {
            console.error('Failed to fetch user:', error);
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshToken = useCallback(async () => {
        const refresh = localStorage.getItem('refresh_token');
        if (!refresh) {
            setLoading(false);
            return;
        }

        try {
            const response = await api.post('/api/auth/refresh/', { refresh });
            const newToken = response.data.access;
            localStorage.setItem('access_token', newToken);
            await fetchCurrentUser(newToken);
        } catch (error) {
            // Refresh failed, user needs to log in again
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            setUser(null);
            setLoading(false);
        }
    }, [fetchCurrentUser]);

    // Check if there's a token in localStorage on app load
    useEffect(() => {
        const token = localStorage.getItem('access_token');
        if (token) {
            try {
                const decoded = jwtDecode(token);
                // Check if token is expired
                const now = Date.now() / 1000;
                if (decoded.exp > now) {
                    fetchCurrentUser(token);
                } else {
                    // Token expired, try to refresh
                    refreshToken();
                }
            } catch (e) {
                // Invalid token, clear storage
                console.error('Invalid token:', e);
                localStorage.removeItem('access_token');
                localStorage.removeItem('refresh_token');
                setLoading(false);
            }
        } else {
            setLoading(false);
        }
    }, [fetchCurrentUser, refreshToken]);

    const login = async (username, password) => {
        const response = await api.post('/api/auth/login/', { username, password });
        const { access, refresh } = response.data;

        localStorage.setItem('access_token', access);
        localStorage.setItem('refresh_token', refresh);

        // Get the full user info
        await fetchCurrentUser(access);
        return response.data;
    };

    const logout = useCallback(() => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setUser(null);
    }, []);

    const updateUser = (updatedUser) => {
        setUser(updatedUser);
    };

    const value = {
        user,
        loading,
        login,
        logout,
        updateUser,
        isAuthenticated: !!user,
        isAdmin: user?.role === 'admin',
        isApproved: user?.is_approved,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

// Custom hook to use auth context
export function useAuth() {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}

export default AuthContext;
