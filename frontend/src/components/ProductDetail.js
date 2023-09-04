import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from 'axios';
import { connect } from "react-redux";

function ProductDetail({ access }) {
    const params = useParams() 
	const [product, setProduct] = useState([]);
	const [reviews, setReviews] = useState([]);
	const [isLoaded, setIsLoaded] = useState(false);


	useEffect(() => {
		axios.get(`http://127.0.0.1:8000/api/products/${params.id}/`, {
		  headers: {
			'Content-Type': 'application/json',
            'Authorization': `JWT ${access}`,
            'Accept': 'application/json'
		  },
		})
		  .then(response => {
			setProduct(response.data);
			setReviews(response.data.reviews);
			setIsLoaded(true)
		  })
		  .catch(error => {
			console.log(error)	
			setIsLoaded(false);
		})
	  }, []);


	if (!isLoaded) {
		return <div></div>
	}
	
	return (
		<div>
			<div key={product.id} className="container mt-5">
				<h3>[{product.product_type}] &thinsp;{product.title}</h3>
				{(product.product_type !== "Shoes") ?
					<p>Seller: {product.seller} | Character: {product.cosplay_character} |
					Size: {product.size}</p> :
					<p>Seller: {product.seller} | Character: {product.cosplay_character} |
					Shoes Size: {product.shoes_size}</p>
				}
				<h4>Product Description:</h4>
				<p className="product_description">{product.description}</p>							
				<div className="div_price_buy">
					<h3>{product.price}₽</h3>
					<button className="buy_button">Buy</button>
				</div>
				<hr></hr>
				<h3>Reviews:</h3>
				<br></br>
				<div className="review_list">
					{reviews.length > 0 ?
					reviews.map(review => (
						<><h5 key={review.id}>{review.customer}:</h5>
						<h5>{"★".repeat(review.score)}</h5>
						<h5>{review.text}</h5>
						<br></br></>
					))
					: <h5>There's no any reviews yet!</h5>
					}
				</div>
			</div>
		</div>
    );
};

const mapStateToProps = (state) => {
	return {
	  access: state.access
	};
  };

export default connect(mapStateToProps)(ProductDetail);