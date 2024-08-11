import React, { useState, useEffect } from "react";
import { useParams } from "react-router-dom";
import axios from 'axios';
import { connect } from "react-redux";
import StarRatings from "react-star-ratings";

function ProductDetail({ access }) {
    const params = useParams();
    const [product, setProduct] = useState([]);
    const [reviews, setReviews] = useState([]);
    const [isLoaded, setIsLoaded] = useState(false);

    useEffect(() => {
        axios.get(`http://localhost:8000/api/products/${params.id}/`, {
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            },
        })
            .then(response => {
                setProduct(response.data);
                setReviews(response.data.reviews);
                setIsLoaded(true);
            })
            .catch(error => {
                console.log(error);
                setIsLoaded(false);
            })
    }, []);

    if (!isLoaded) {
        return <div>Loading...</div>;
    }

    return (
        <div className="container mt-5">
            <div className="row">
                <div className="col-lg-6">
				<img
					src={product.product_images.length > 0 ? product.product_images[0]?.image : "/no-photo-available-icon.jpg"}
					className="img-fluid mb-4"
					alt={product.title}
				/>
                    <div className="row">
                        {product.product_images.map(image => (
                            <div key={image.id} className="col-md-6 mb-3">
                                <img src={image.image} className="img-fluid" alt={product.title} />
                            </div>
                        ))}
                    </div>
                </div>
                <div className="col-lg-6">
                    <h2>{product.title}</h2>
                    <p><strong>Price:</strong> {product.price}</p>
                    {product.discount && (
                        <p><strong>Discount:</strong> {product.discount}%</p>
                    )}
                    <p><strong>Description:</strong> {product.description}</p>
                    <p><strong>Size:</strong> {product.size}</p>
                    {product.shoes_size && (
                        <p><strong>Shoes Size:</strong> {product.shoes_size}</p>
                    )}
                    <p><strong>In Stock:</strong> {product.in_stock}</p>
                    <p><strong>Seller:</strong> {product.seller.name}</p>
                    <button className="btn btn-primary">Add to Cart</button>
                </div>
            </div>
            <div className="mt-5">
                <h3>Reviews</h3>
                {reviews.length > 0 ? (
                    <ul className="list-unstyled">
                        {reviews.map((review, index) => (
                            <li key={review.id} className={`review-item ${index !== reviews.length - 1 ? 'mb-4' : ''}`}>
                                <div className="d-flex align-items-start">
                                    <div className="mr-3">
                                        <img
                                            src={review.customer.profile_pic || "/no-photo-available-icon.jpg"}
                                            alt="User Avatar"
                                            className="user-avatar rounded-circle"
                                            style={{ width: '40px', height: '40px', margin: '0 10px 0 0' }}
                                        />
                                    </div>
                                    <div className="flex-grow-1">
                                        <div>
                                            <strong>{review.customer.username}</strong>
                                            <StarRatings
                                                rating={review.score}
                                                starRatedColor="gold"
                                                numberOfStars={5}
                                                name="rating"
                                                starDimension="20px"
                                                starSpacing="2px"
                                            />
                                        </div>
                                        <p className="review-text">{review.text}</p>
                                    </div>
                                </div>
                                {review.answers.length > 0 && (
                                    <div className="review-answers">
                                        {review.answers.map((answer, answerIndex) => (
                                            <div key={answer.id} className={`answer-item d-flex align-items-start ${answerIndex !== review.answers.length - 1 ? 'mb-2' : ''}`}>
                                                <div className="mr-3">
                                                    <img
                                                        src={product.seller.profile_pic || "/no-photo-available-icon.jpg"}
                                                        alt="Seller Avatar"
                                                        className="user-avatar rounded-circle"
                                                        style={{ width: '30px', height: '30px', margin: '0 5px 0 0' }}
                                                    />
                                                </div>
                                                <div className="flex-grow-1">
                                                    <div>
                                                        <strong>{product.seller.username}</strong>
                                                        <p>{answer.text}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                )}
                            </li>
                        ))}
                    </ul>
                ) : (
                    <p>No reviews yet.</p>
                )}
            </div>
        </div>
    );
}

const mapStateToProps = (state) => {
    return {
        access: state.access
    };
};

export default connect(mapStateToProps)(ProductDetail);
