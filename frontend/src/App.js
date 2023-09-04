import React from "react";
import "./styles/App.css"
import { BrowserRouter as Router, Routes, Route, Link, Redirect } from "react-router-dom";

import { Provider } from 'react-redux';
import store from './store';

import Layout from './hocs/Layout'
import ProductList from "./components/ProductList";
import ProductDetail from "./components/ProductDetail";
import SignUp from "./components/SignUp2";
import Login from "./components/Login";
import ActivateAccount from "./components/ActivateAccount";
import PasswordReset from "./components/PasswordReset";
import PasswordResetConfirm from "./components/PasswordResetConfirm";
import UsernameReset from "./components/UsernameReset";
import UsernameResetConfirm from "./components/UsernameResetConfirm";


function App() {
  return (
    <Provider store={store}>
      <div className="App">
        <Router>
          <Layout>
            <Routes>
              <Route path="/" element={<ProductList />} exact />
              <Route path="/signup" element={<SignUp />} exact />
              <Route path="/login" element={<Login />} exact />
              <Route path="/activate/:uid/:token" element={<ActivateAccount />} />
              <Route path="/password-reset" element={<PasswordReset />} exact />
              <Route path="/username-reset" element={<UsernameReset />} exact />
              <Route path="/password/reset/confirm/:uid/:token" element={<PasswordResetConfirm />} />
              <Route path="/username/reset/confirm/:uid/:token" element={<UsernameResetConfirm />} />
              <Route path="/product/:id" element={<ProductDetail />} />
            </Routes>
          </Layout>
        </Router>
      </div>
    </Provider>
  );
}

export default App;
