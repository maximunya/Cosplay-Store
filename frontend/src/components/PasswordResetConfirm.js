import React, { useState } from "react";
import { Link, Navigate, useParams } from 'react-router-dom';
import { password_reset_confirm } from '../actions/auth'
import { connect } from "react-redux";

function PasswordResetConfirm({ password_reset_confirm }) {

    const [requestSent, setRequestSent] = useState(false);
    const [new_password, setNewPassword] = useState();
    const [re_new_password, setReNewPassword] = useState();
    const [showPassword, setShowPassword] = useState(false);
    const params = useParams();

    const toggleShowPassword = () => {
        setShowPassword(!showPassword)
    }


    const onSubmit = (e) => {
        e.preventDefault();

        const uid = params.uid;
        const token = params.token;

        password_reset_confirm(uid, token, new_password, re_new_password);
        setRequestSent(true)     
    };

    if (requestSent) {
        return <Navigate to='/' />
    }

    return (
        <div>
            <div className="container text-left mt-5 p-5 col-sm-4">
                <h1 className="mt-4 text-center">Password Reset</h1>
                <p className="mt-3 text-center">Create new password for your account.</p>
                <form onSubmit={e => onSubmit(e)}>
                    <div className="form-group mt-4">
                        <input
                            className="form-control"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="New password"
                            name="new_password"
                            value={new_password}
                            onChange={e => setNewPassword(e.target.value)}
                            required
                            minLength='8'
                        />
                    </div>
                    <div className="form-group mt-3">
                        <input
                            className="form-control"
                            type={showPassword ? 'text' : 'password'}
                            placeholder="Confirm new password"
                            name="re_new_password"
                            value={re_new_password}
                            onChange={e => setReNewPassword(e.target.value)}
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
                    <button className="btn btn-primary mt-3 col-sm-12" type='submit'>Reset Password</button>
                </form>
            </div>
        </div>
    );
}

export default connect(null, { password_reset_confirm })(PasswordResetConfirm);