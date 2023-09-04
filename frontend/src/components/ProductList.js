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
				'Authorization': `JWT ${access}`,
				'Accept': 'application/json'
			},
			})
			.then(response => {
				setProducts(response.data);
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
			<div>
				<div className="container mt-5">	
					<ul>
						{Array.from(products).map(product => (
							<><li key={product.id} className="product_item">
								<h3>[{product.product_type}] &thinsp;<Link to={`/product/${product.id}`}>{product.title}</Link></h3>
								{(product.product_type !== "Shoes") ?
									<p>Seller: {product.seller} | Character: {product.cosplay_character} |
										Size: {product.size}</p> :
									<p>Seller: {product.seller} | Character: {product.cosplay_character} |
										Shoes Size: {product.shoes_size}</p>}
							</li><br></br></>
						))}
					</ul>
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
