import React, { useState, useEffect } from "react";
import { Link, Redirect } from 'react-router-dom';
import axios from 'axios';
import { Formik } from 'formik';
import * as yup from 'yup';

function SignUp() {
    
    const [showPassword, setShowPassword] = useState(false);

    const toggleShowPassword = () => {
        setShowPassword(!showPassword)
    }

    const validationSchema = yup.object().shape({
        username: yup.string().required('Required.').matches(/^(?!\.)(?!.*\.$)[a-zA-Z0-9_.]+$/, 'Invalid username format.').min(3, "Username must be at least 3 characters long."),
        email: yup.string().email("Invalid email format.").required('Required.'),
        password: yup.string().required('Required.').min(8, 'Password must be at least 8 characters long.')
        .matches(
          /^(?=.*[a-zA-Z])(?=.*\d)[a-zA-Z\d\w\W]{8,}$/,
          'Password must contain letters and digits.'
        ),
        re_password: yup.string().oneOf([yup.ref('password')], "Passwords must match.").required('Required.')
    })

    const handleSubmit = (values) => {
        console.log(values);
        axios
            .post('http://localhost:8000/auth/users/', {
            username: values.username,
            email: values.email,
            password: values.password,
            re_password: values.re_password,
            })
            .then((response) => {
            console.log(response.data);
            })
            .catch((error) => {
            console.error(error);
            })
      };

    return (
        <div>
            <div className="container text-left mt-5 p-5 col-sm-4">
                <h1 className="text-center">Sign Up</h1>
                <p className="text-center">Create your Account.</p>
                <Formik
                    initialValues={{
                        username: "",
                        email: "",
                        password: "",
                        re_password: ""
                    }}
                    validateOnBlur
                    onSubmit={(values) => handleSubmit(values)}
                    validationSchema={validationSchema}
                >
                    {({ values, errors, touched, handleChange, handleBlur, isValid, dirty, handleSubmit, isSubmitting}) => (
                        <form onSubmit={(values) => handleSubmit(values)}>
                            <div className="form-group">
                                <input
                                    className={(errors.username && touched.username) ?
                                        "form-control is-invalid" : 
                                        (!errors.username && touched.username) ? 
                                        "form-control is-valid" : "form-control"}
                                    type="text"
                                    placeholder="Username"
                                    name="username"
                                    value={values.username}
                                    onChange={handleChange}
                                    onBlur={handleBlur}
                                />
                            </div>
                            { touched.username && errors.username && (<p className="error-message">{errors.username}</p>)}
                            <div className="form-group">
                                <input
                                    className={(errors.email && touched.email) ? "form-control is-invalid mt-3" : "form-control mt-3"}
                                    type="email"
                                    placeholder="Email"
                                    name="email"
                                    value={values.email}
                                    onChange={handleChange}
                                    onBlur={handleBlur}
                                />
                            </div>
                            { touched.email && errors.email && <p className="error-message">{errors.email}</p>}
                            <div className="form-group">
                                <input
                                    className={(errors.password && touched.password) ? "form-control is-invalid mt-3" : "form-control mt-3"}
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Password"
                                    name="password"
                                    value={values.password}
                                    onChange={handleChange}
                                    onBlur={handleBlur}
                                />
                            </div>
                            { touched.password && errors.password && <p className="error-message">{errors.password}</p>}
                            <div className="form-group">
                                <input
                                    className={(errors.re_password && touched.re_password) ? "form-control is-invalid mt-3" : "form-control mt-3"}
                                    type={showPassword ? 'text' : 'password'}
                                    placeholder="Confirm password"
                                    name="re_password"
                                    value={values.re_password}
                                    onChange={handleChange}
                                    onBlur={handleBlur}
                                />
                            </div>
                            { touched.re_password && errors.re_password && <p className="error-message">{errors.re_password}</p>}
                            <div className="form-check mt-3">
                                <input
                                    className="form-check-input"
                                    type="checkbox"
                                    name="show_password"
                                    checked={showPassword}
                                    onChange={toggleShowPassword}
                                />
                                <label className="form-check-label" htmlFor="flexCheckDefault">
                                    Show password
                                </label>
                            </div>
                            <button 
                                disabled={isSubmitting}
                                className="btn btn-primary mt-3 col-sm-12"
                                type="submit"
                            >Create an Account
                            </button>
                        </form>
                    )}
                </Formik>
                <p className="mt-3 text-center">Already have an account? <Link to='/login'>Sign In</Link></p>
            </div>
        </div>
    );
}

export default SignUp;