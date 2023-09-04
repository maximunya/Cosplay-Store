import React, { useEffect, useState } from "react";
import Navbar from '../components/Navbar';
import { connect } from 'react-redux';
import { checkAuthenticated } from "../actions/auth";

function Layout(props) {

    useEffect(() => {
        props.checkAuthenticated();
    }, []);

    return (
    <div>
        <Navbar />
        {props.children}
    </div>
    );
}

export default connect(null, { checkAuthenticated })(Layout);
