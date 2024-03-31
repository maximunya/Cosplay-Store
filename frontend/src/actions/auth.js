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
} from './types';

import axios from 'axios';

export const checkAuthenticated = () => async dispatch => {
    if (localStorage.getItem('access')) {
        console.log('В localStorage найден access токен')
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const body = JSON.stringify({token: localStorage.getItem('access')});
        
        try {
            console.log('Отправляю запрос на проверку имеющегося access токена')
            const res = await axios.post(`http://localhost:8000/api/auth/jwt/verify/`, body, config)
        
            if (res.data.code !== 'token_not_valid') {
                console.log('access токен валидный, юзер аутентифицирован')
                dispatch({
                    type: AUTHENTICATED_SUCCESS
                });
                dispatch(loadUser())
            } else {
                console.log('token_not_valid')
                dispatch(refreshTokens());
            }
        } catch (err) {
            console.log('Ошибка запроса проверки access токена')
            dispatch(refreshTokens());
        }
    } else {
        console.log('В localStorage нет access токена')
        dispatch(refreshTokens());
    }
};

export const refreshTokens = () => async dispatch => {
    console.log('Запустилась функция refreshTokens')

    if (localStorage.getItem('refresh')) {
        console.log('В localStorage найден refresh токен.')

        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };

        const body = JSON.stringify({refresh: localStorage.getItem('refresh')})

        try {
            console.log('Отправляю запрос на обновление токенов')

            const res = await axios.post(`http://localhost:8000/api/auth/jwt/refresh/`, body, config)

            if (res.data.code !== 'token_not_valid') {
                console.log('refresh токен сработал, новые токены получены')
                dispatch({
                    type: REFRESH_SUCCESS,
                    payload: res.data
                });
                window.location.reload()
            } else {
                console.log('refresh токен не валидный')
                dispatch({
                    type: REFRESH_FAIL
                });
                dispatch({
                    type: AUTHENTICATED_FAIL
                });
            }
        } catch (err) {
            console.log('Запрос на обновление токенов не прошёл')
            dispatch({
                type: REFRESH_FAIL
            });
            dispatch({
                type: AUTHENTICATED_FAIL
            });
        }
    } else {
        console.log('В localStorage нет refresh токена')
        dispatch({
            type: REFRESH_FAIL
        });
        dispatch({
            type: AUTHENTICATED_FAIL
        });
    }
}

export const loadUser = () => async dispatch => {
    if (localStorage.getItem('access')) {
        const config = {
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `JWT ${localStorage.getItem('access')}`,
                'Accept': 'application/json'
            }
        };

        try {
            const res = await axios.get(`http://localhost:8000/api/auth/users/me/`, config);

            dispatch({
                type: USER_LOADED_SUCCESS,
                payload: res.data
            });
        } catch (err) {
            dispatch({
                type: USER_LOADED_FAIL
            });
        };
    } else {
        dispatch({
            type: USER_LOADED_FAIL
        })
    };
};

export const login = (email, password) => async dispatch => {
    const config = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    try {
        const res = await axios.post(
            `http://localhost:8000/api/auth/jwt/create/`,
            {
                email: email,
                password: password,
            },
            config)

        dispatch({
            type: LOGIN_SUCCESS,
            payload: res.data
        });

        dispatch(loadUser());

    } catch (err) {
        dispatch({
            type: LOGIN_FAIL,
        });
    };
};

export const password_reset = (email) => async dispatch => {
    const config = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    const body = JSON.stringify({ email });
    try {
        await axios.post(`http://localhost:8000/api/auth/users/reset_password/`, body, config);
        dispatch({
            type: PASSWORD_RESET_SUCCESS
        });
    } catch (err) {
        dispatch({
            type: PASSWORD_RESET_FAIL
        });
    };
};

export const password_reset_confirm = (uid, token, new_password, re_new_password) => async dispatch => {
    const config = {
        headers: {
            'Content-Type': 'application/json',
        }
    };
    const body = JSON.stringify({ uid, token, new_password, re_new_password });
    console.log(body)
    try {
        await axios.post(`http://localhost:8000/api/auth/users/reset_password_confirm/`, body, config);
        dispatch({
            type: PASSWORD_RESET_CONFIRM_SUCCESS
        });
    } catch (err) {
        dispatch({
            type: PASSWORD_RESET_CONFIRM_FAIL
        });
    };
};

export const logout = () => async dispatch => {
    dispatch({
        type: LOGOUT
    });
};