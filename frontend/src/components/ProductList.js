import React from 'react';
import ProductCard from './ProductCard';
import './ProductList.css';

export default function ProductList({ products, onDelete, onUpdate, loading }) {
  if (loading) return <div className="list-state">Loading your tracked products...</div>;
  if (!products.length) return (
    <div className="list-state empty">
      <span>📦</span>
      <p>No products tracked yet. Add one above to get started!</p>
    </div>
  );

  return (
    <div className="product-list">
      <h2 className="list-title">Your Tracked Products ({products.length})</h2>
      <div className="product-grid">
        {products.map(p => (
          <ProductCard key={p.id} product={p} onDelete={onDelete} onUpdate={onUpdate} />
        ))}
      </div>
    </div>
  );
}
