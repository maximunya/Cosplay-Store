import { password_reset } from './actions/auth';
import {
    LOGIN_SUCCESS,
    LOGIN_FAIL,
    USER_LOADED_SUCCESS,
    USER_LOADED_FAIL,
    AUTHENTICATED_SUCCESS,
    AUTHENTICATED_FAIL,
    LOGOUT,
    PASSWORD_RESET_SUCCESS,
    PASSWORD_RESET_FAIL,
    PASSWORD_RESET_CONFIRM_SUCCESS,
    PASSWORD_RESET_CONFIRM_FAIL,
    REFRESH_SUCCESS,
    REFRESH_FAIL,
} from './actions/types';

const initialState = {
    access: localStorage.getItem('access'),
    refresh: localStorage.getItem('refresh'),
    isAuthenticated: null,
    user: null
}

export default function(state = initialState, action) {
    const { type, payload } = action;

    switch (type) {
        case AUTHENTICATED_SUCCESS:
            return {
                ...state,
                isAuthenticated: true,
            }
        case REFRESH_SUCCESS:
            localStorage.setItem('access', payload.access);
            localStorage.setItem('refresh', payload.refresh);

            return {
                ...state, 
                access: payload.access,
                access: payload.refresh,
            }
        case REFRESH_FAIL:
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            return {
                ...state, 
                access: null,
                refresh: null,
                isAuthenticated: false,
                user: null
            }
        case AUTHENTICATED_FAIL:
            return {
                ...state,
                isAuthenticated: false
            }
        case LOGIN_SUCCESS:
            localStorage.setItem('access', payload.access);
            localStorage.setItem('refresh', payload.refresh);
            return {
                ...state, 
                access: payload.access,
                refresh: payload.refresh,
                isAuthenticated: true,
                user: payload
            }
        case LOGIN_FAIL:
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            return {
                ...state, 
                access: null,
                refresh: null,
                isAuthenticated: false,
                user: null
            }
        case LOGOUT:
            localStorage.removeItem('access');
            localStorage.removeItem('refresh');
            return {
                ...state, 
                access: null,
                refresh: null,
                isAuthenticated: false,
                user: null
            }
        case USER_LOADED_SUCCESS:
            return {
                ...state,
                user: payload
            }
        case USER_LOADED_FAIL:
            return {
                ...state,
                user: null
            }

        case PASSWORD_RESET_SUCCESS:
        case PASSWORD_RESET_FAIL:
        case PASSWORD_RESET_CONFIRM_SUCCESS:
        case PASSWORD_RESET_CONFIRM_FAIL:
            return {
                ...state
            }
        default: 
            return state
    }
}
