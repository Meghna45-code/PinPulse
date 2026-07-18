import React from 'react';

function VelocityTab({ data, onProductClick, onAddToCart }) {
  if (!data) return null;

  return (
    <div className="velocity-tab-content">
      <div className="velocity-header">
        <h2>🔥 {data.theme}</h2>
        <p className="velocity-subtitle">Trending in your locality right now</p>
      </div>

      <div className="velocity-grid">
        {data.products.map(product => (
          <div key={product.id} className="product-card velocity-card">
            <div className="product-image" onClick={() => onProductClick(product.id)}>
              <img src={product.image} alt={product.name} />
              <span className="velocity-badge">📈 Trending</span>
            </div>
            <div className="product-info">
              <h3 className="product-name">{product.name}</h3>
              <p className="product-price">₹{product.price}</p>
              <p className="product-category">{product.category}</p>
            </div>
            <div className="product-actions">
              <button className="btn-cart" onClick={() => onAddToCart(product.id)}>
                🛒 Add to Cart
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default VelocityTab;
