import React from 'react';

function ProductGrid({ products, onProductClick, onAddToCart, onWishlist }) {
  if (!products || products.length === 0) {
    return <div className="empty-state">Loading recommendations...</div>;
  }

  return (
    <div className="product-grid">
      {products.map((product, index) => (
        <div key={product.id} className="product-card">
          {/* Score Badge */}
          <div className="score-badge">
            {product.final_score?.toFixed(2)}
          </div>

          {/* Product Image */}
          <div className="product-image" onClick={() => onProductClick(product.id)}>
            <img src={product.image} alt={product.name} />
            {product.is_evergreen && <span className="evergreen-tag">⭐ Evergreen</span>}
            {product.cf_boost_applied > 0 && <span className="cf-tag">👥 CF Boosted</span>}
          </div>

          {/* Product Info */}
          <div className="product-info">
            <h3 className="product-name" onClick={() => onProductClick(product.id)}>
              {product.name}
            </h3>
            <p className="product-price">₹{product.price}</p>
            <p className="product-category">{product.category}</p>

            {/* Reason Labels — "Why this is here?" */}
            {product.reason_labels && product.reason_labels.length > 0 && (
              <div className="reason-labels">
                {product.reason_labels.slice(0, 2).map((label, i) => (
                  <span key={i} className="reason-label">{label}</span>
                ))}
              </div>
            )}

            {/* Score Breakdown (mini) */}
            <div className="score-mini">
              <span title="Aesthetic">A:{product.s_aesthetic?.toFixed(1)}</span>
              <span title="Fabric">F:{product.s_fabric?.toFixed(1)}</span>
              <span title="Festivity">Fe:{product.s_festivity?.toFixed(1)}</span>
              <span title="Creator">C:{product.s_creator?.toFixed(1)}</span>
            </div>
          </div>

          {/* Actions */}
          <div className="product-actions">
            <button className="btn-cart" onClick={() => onAddToCart(product.id)}>
              🛒 Add to Cart
            </button>
            <button className="btn-wishlist" onClick={() => onWishlist(product.id)}>
              ❤️
            </button>
          </div>
        </div>
      ))}
    </div>
  );
}

export default ProductGrid;
