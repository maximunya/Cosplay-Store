import React, { useState, useEffect } from "react";
import { Link, Redirect } from 'react-router-dom';
import axios from 'axios';

function SignUp() {

    const [username, setUsername] = useState()
    const [email, setEmail] = useState()
    const [password, setPassword] = useState()
    const [re_password, setRePassword] = useState()
    const [showPassword, setShowPassword] = useState(false);

    const toggleShowPassword = () => {
        setShowPassword(!showPassword)
    }

    const signIn = (e) => {
        e.preventDefault();
        axios.post(`http://localhost:8000/auth/users/`, {
                username: username,
                email: email,
                password: password,
                re_password: re_password,
                }).then((response) => {
                    console.log(response.data)
                    });
    };

    return (
        <div>
            <div className="container text-left mt-5 p-5 col-sm-4">
                <h1 className="text-center">Sign Up</h1>
                <p className="text-center">Create your Account.</p>
                <form onSubmit={signIn}>
                    <div className="form-group">
                        <input
                            className="form-control"
                            type="text"
                            placeholder="Username"
                            name="username"
                            value={username}
                            onChange={e => setUsername(e.target.value)}
                            required
                        />
                    </div>
                    <div className="form-group">
                        <input
                            className="form-control mt-3"
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
                    <div className="form-group">
                        <input
                            className="form-control mt-3"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Confirm password"
                            name="password-retype"
                            value={re_password}
                            onChange={e => setRePassword(e.target.value)}
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
                    <button className="btn btn-primary mt-3 col-sm-12" type='submit'>Create an Account</button>
                </form>
                <p className="mt-3 text-center">Already have an account? <Link to='/login'>Sign In</Link></p>
            </div>
        </div>
    );
}

export default SignUp;