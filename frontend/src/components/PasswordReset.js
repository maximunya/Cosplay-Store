import React, { useState } from "react";
import { Link, Navigate } from 'react-router-dom';
import { password_reset } from '../actions/auth'
import { connect } from "react-redux";

function PasswordReset({ password_reset }) {

    const [requestSent, setRequestSent] = useState(false);
    const [email, setEmail] = useState();

    const onSubmit = (e) => {
        e.preventDefault();
        password_reset(email);
        setRequestSent(true)     
    };

    if (requestSent) {
        return <Navigate to='/' />
    }

    return (
        <div>
            <div className="container text-center mt-5 p-5 col-sm-4">
                <h1 className="mt-4">Password Reset</h1>
                <p className="mt-3">Enter your user account's verified email address and we will send you a password reset link.</p>
                <form onSubmit={e => onSubmit(e)}>
                    <div className="form-group mt-4">
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
                    <button className="btn btn-primary mt-3 col-sm-12" type='submit'>Send password reset email</button>
                </form>
            </div>
        </div>
    );
}

export default connect(null, { password_reset })(PasswordReset);