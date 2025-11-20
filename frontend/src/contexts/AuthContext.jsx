import React, { createContext, useContext, useReducer, useEffect } from 'react';
import { api } from '../services/api';

const AuthContext = createContext();

const initialState = {
  user: null,
  token: localStorage.getItem('authToken'),
  isAuthenticated: false,
  loading: true,
  error: null,
};

const authReducer = (state, action) => {
  switch (action.type) {
    case 'LOGIN_START':
      return { ...state, loading: true, error: null };
    case 'LOGIN_SUCCESS':
      return {
        ...state,
        user: action.payload.user,
        token: action.payload.token,
        isAuthenticated: true,
        loading: false,
        error: null,
      };
    case 'LOGIN_FAILURE':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: action.payload,
      };
    case 'LOGOUT':
      return {
        ...state,
        user: null,
        token: null,
        isAuthenticated: false,
        loading: false,
        error: null,
      };
    case 'UPDATE_USER':
      return {
        ...state,
        user: { ...state.user, ...action.payload },
      };
    case 'SET_LOADING':
      return { ...state, loading: action.payload };
    default:
      return state;
  }
};

export const AuthProvider = ({ children }) => {
  const [state, dispatch] = useReducer(authReducer, initialState);

  // Check if user is authenticated on mount
  useEffect(() => {
    const checkAuth = async () => {
      const token = localStorage.getItem('authToken');
      if (token) {
        try {
          const response = await api.getProfile();
          dispatch({
            type: 'LOGIN_SUCCESS',
            payload: {
              user: response.data,
              token,
            },
          });
        } catch (error) {
          localStorage.removeItem('authToken');
          dispatch({ type: 'LOGOUT' });
        }
      } else {
        dispatch({ type: 'SET_LOADING', payload: false });
      }
    };

    checkAuth();
  }, []);

  const login = async (credentials) => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      const response = await api.login(credentials);
      const { user, access_token } = response.data;
      
      localStorage.setItem('authToken', access_token);
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user,
          token: access_token,
        },
      });
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erreur de connexion';
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: errorMessage,
      });
      
      return { success: false, error: errorMessage };
    }
  };

  const logout = async () => {
    try {
      await api.logout();
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('authToken');
      dispatch({ type: 'LOGOUT' });
    }
  };

  const register = async (userData) => {
    dispatch({ type: 'LOGIN_START' });
    
    try {
      const response = await api.register(userData);
      const { user, access_token } = response.data;
      
      localStorage.setItem('authToken', access_token);
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user,
          token: access_token,
        },
      });
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erreur d\'inscription';
      dispatch({
        type: 'LOGIN_FAILURE',
        payload: errorMessage,
      });
      
      return { success: false, error: errorMessage };
    }
  };

  const updateProfile = async (profileData) => {
    try {
      const response = await api.updateProfile(profileData);
      dispatch({
        type: 'UPDATE_USER',
        payload: response.data,
      });
      
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erreur de mise à jour';
      return { success: false, error: errorMessage };
    }
  };

  const changePassword = async (passwordData) => {
    try {
      await api.changePassword(passwordData);
      return { success: true };
    } catch (error) {
      const errorMessage = error.response?.data?.detail || 'Erreur de changement de mot de passe';
      return { success: false, error: errorMessage };
    }
  };

  const refreshToken = async () => {
    try {
      const response = await api.refreshToken();
      const { access_token } = response.data;
      
      localStorage.setItem('authToken', access_token);
      
      dispatch({
        type: 'LOGIN_SUCCESS',
        payload: {
          user: state.user,
          token: access_token,
        },
      });
      
      return { success: true };
    } catch (error) {
      localStorage.removeItem('authToken');
      dispatch({ type: 'LOGOUT' });
      return { success: false, error: 'Session expirée' };
    }
  };

  const value = {
    ...state,
    login,
    logout,
    register,
    updateProfile,
    changePassword,
    refreshToken,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}; 