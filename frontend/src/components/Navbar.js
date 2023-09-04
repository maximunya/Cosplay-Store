import React, { Fragment, useState, useEffect } from "react";
import { Link, Redirect } from 'react-router-dom';
import { logout } from '../actions/auth';
import { connect } from "react-redux";

function Navbar({ logout, isAuthenticated }) {
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        if (isAuthenticated) {
            setIsLoaded(true);
        } else if (isAuthenticated === false) {
            setIsLoaded(true);
        }
    }, [isAuthenticated]);

    const guestLinks = () => (
        <Fragment>
            <li className="nav-item">
                <Link to='/login' className="nav-link">Login</Link>
            </li>
            <li className="nav-item">
                <Link to='/signup' className="nav-link">Sign Up</Link>
            </li>
        </Fragment>
    );

    const authLinks = () => (
        <Fragment>
            <li className="nav-item">
                <a className="nav-link" href="" onClick={logoutHandler}>Logout</a>
            </li>
        </Fragment>
    );

    const logoutHandler = () => {
        logout();
        window.location.reload();
    }

    if (!isLoaded) {
        return (
            <div>
                <nav className="navbar navbar-expand-lg bg-dark border-bottom border-bottom-dark" data-bs-theme="dark">
                    <div className="container-fluid">
                        <Link to='/' className="navbar-brand">Cosplay Store</Link>
                        <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarTogglerDemo02" aria-controls="navbarTogglerDemo02" aria-expanded="false" aria-label="Toggle navigation">
                        <span className="navbar-toggler-icon"></span>
                        </button>
                        <div className="collapse navbar-collapse" id="navbarTogglerDemo02">
                        <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                            <li className="nav-item">
                                <Link to='/' className="nav-link active">Fandoms</Link>
                            </li>
                        </ul>
                        <form className="d-flex" role="search">
                            <input className="form-control me-2" type="search" placeholder="Search products" aria-label="Search"/>
                            <button className="btn btn-outline-success" type="submit">Search</button>
                        </form>
                        </div>
                    </div>
                </nav>
            </div>
        );
    }

    return (
        <div>
            <nav className="navbar navbar-expand-lg bg-dark border-bottom border-bottom-dark" data-bs-theme="dark">
                <div className="container-fluid">
                    <Link to='/' className="navbar-brand">Cosplay Store</Link>
                    <button className="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarTogglerDemo02" aria-controls="navbarTogglerDemo02" aria-expanded="false" aria-label="Toggle navigation">
                    <span className="navbar-toggler-icon"></span>
                    </button>
                    <div className="collapse navbar-collapse" id="navbarTogglerDemo02">
                    <ul className="navbar-nav me-auto mb-2 mb-lg-0">
                        <li className="nav-item">
                            <Link to='/' className="nav-link active">Fandoms</Link>
                        </li>
                        {isAuthenticated ? authLinks() : guestLinks()}
                    </ul>
                    <form className="d-flex" role="search">
                        <input className="form-control me-2" type="search" placeholder="Search products" aria-label="Search"/>
                        <button className="btn btn-outline-success" type="submit">Search</button>
                    </form>
                    </div>
                </div>
            </nav>
        </div>
    );
}

const mapStateToProps = state => ({
    isAuthenticated: state.isAuthenticated
});

export default connect(mapStateToProps, { logout })(Navbar);
