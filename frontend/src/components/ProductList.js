import React, { useState, useEffect } from "react";
import { Link, Navigate } from 'react-router-dom';
import axios from 'axios';
import { connect } from "react-redux";
import Navbar from './Navbar'

function ProductList({ access }) {
	const [products, setProducts] = useState([]);
	const [isLoaded, setIsLoaded] = useState(false);
	
	useEffect(() => {
		axios.get(`http://127.0.0.1:8000/api/products/`, {
			headers: {
				'Content-Type': 'application/json',
				'Accept': 'application/json'
			},
			})
			.then(response => {
				console.log(response.data)
				setProducts(response.data.results);
				setIsLoaded(true);
			})
			.catch(error => {
				console.log(error)	
				setIsLoaded(false);
			})
	}, []);

	if (!isLoaded) {
		return <div></div>
	} else {
		return (
			<div className="container mt-5 mb-2">
			  <h2 className="mb-4">Список товаров</h2>
			  <div className="row">
				{products.map(product => (
				  <div key={product.id} className="col-lg-3 col-md-6 mb-4">
					<Link to={`/product/${product.slug}`} style={{ textDecoration: 'none', color: 'inherit' }}>
					  <div className="card h-100">
						{product.product_images.length > 0 ? (
						  <img className="card-img-top" src={product.product_images[0].image} alt={product.title} />
						) : (
						  <img className="card-img-top" src="/no-photo-available-icon.jpg" alt="No Photo Available" />
						)}
						<div className="card-body">
						  <h4 className="card-title">{product.title}</h4>
						  <p className="card-text">{product.product_type}</p>
						  <p className="card-text">Price: {product.price}</p>
						</div>
						<div className="card-footer">
						  <small className="text-muted">Seller: {product.seller.name}</small>
						</div>
					  </div>
					</Link>
				  </div>
				))}
			  </div>
			</div>
		  );
	}
}

const mapStateToProps = (state) => {
	return {
	  access: state.access,
	  isAuthenticated: state.isAuthenticated
	};
  };

export default connect(mapStateToProps)(ProductList);
