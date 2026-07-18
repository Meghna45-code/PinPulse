import React from 'react';

function ProductDetail({ data, onBack, onAddToCart }) {
  const { product, also_bought } = data;

  return (
    <div className="product-detail">
      <button className="btn-back" onClick={onBack}>← Back to Feed</button>

      <div className="pdp-container">
        {/* Main Product */}
        <div className="pdp-main">
          <div className="pdp-image">
            <img src={product.image} alt={product.name} />
          </div>
          <div className="pdp-info">
            <h1>{product.name}</h1>
            <p className="pdp-price">₹{product.price}</p>
            <p className="pdp-description">{product.description}</p>
            <div className="pdp-meta">
              <span>Category: {product.category}</span>
              <span>Material: {product.material}</span>
              <span>Color: {product.color}</span>
              <span>Stock: {product.stock_level} units</span>
            </div>
            <button className="btn-cart-large" onClick={() => onAddToCart(product.id)}>
              🛒 Add to Cart
            </button>
          </div>
        </div>

        {/* People Also Bought — CF Shelf */}
        {also_bought && also_bought.length > 0 && (
          <div className="pdp-also-bought">
            <h2>👥 People Also Bought This With...</h2>
            <div className="also-bought-scroll">
              {also_bought.map(item => (
                <div key={item.id} className="also-bought-card">
                  <img src={item.image} alt={item.name} />
                  <p className="ab-name">{item.name}</p>
                  <p className="ab-price">₹{item.price}</p>
                  <button className="btn-cart-small" onClick={() => onAddToCart(item.id)}>
                    + Cart
                  </button>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default ProductDetail;
