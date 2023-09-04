import React, { useState } from "react";
import { Link, Navigate } from 'react-router-dom';
import { login } from '../actions/auth'
import { connect } from "react-redux";

function Login({ login, isAuthenticated }) {

    const [email, setEmail] = useState()
    const [password, setPassword] = useState()
    const [showPassword, setShowPassword] = useState(false);

    const toggleShowPassword = () => {
        setShowPassword(!showPassword)
    }
 
    const onSubmit = (e) => {
        e.preventDefault();
        login(email, password);       
    };

    if (isAuthenticated) {
        return <Navigate to='/' />
    }

    return (
        <div>
            <div className="container text-left mt-5 p-5 col-sm-4">
                <h1 className="text-center">Sign In</h1>
                <p className="text-center">Sign into your Account</p>
                <form onSubmit={e => onSubmit(e)}>
                    <div className="form-group">
                        <input
                            className="form-control"
                            type="email"
                            placeholder="Email"
                            name="email"
                            value={email}
                            onChange={e => setEmail(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <input
                            className="form-control mt-3"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Password"
                            name="password"
                            value={password}
                            onChange={e => setPassword(e.target.value)}
                            required
                            minLength='8'
                        />
                    </div>
                    <div className="form-check mt-3">
                        <input
                            className="form-check-input"
                            type="checkbox"
                            name="show_password"
                            checked={showPassword}
                            onChange={toggleShowPassword}
                        />
                        <label className="form-check-label" for="flexCheckDefault">
                            Show password
                        </label>
                    </div>
                    <button className="btn btn-primary mt-3 col-sm-12" type='submit'>Login</button>
                </form>
                <p className="mt-3 text-center">Don't have an account? <Link to='/signup'>Sign Up</Link></p>
                <p className="mt-1 text-center">Forgot your password? <Link to='/password-reset'>Reset password</Link></p>
            </div>
        </div>
    );
}

const mapStateToProps = state => ({
    isAuthenticated: state.isAuthenticated
})

export default connect(mapStateToProps, { login })(Login);