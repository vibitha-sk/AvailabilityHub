import React, { useState } from 'react';
import './ProductCard.css';

const STATUS_LABELS = {
  available: { label: 'Available', color: '#107c10', bg: '#dff6dd' },
  unavailable: { label: 'Unavailable', color: '#a4262c', bg: '#fde7e9' },
  pending: { label: 'Checking...', color: '#605e5c', bg: '#f3f2f1' },
};

export default function ProductCard({ product, onDelete, onUpdate }) {
  const [editing, setEditing] = useState(false);
  const [newSize, setNewSize] = useState(product.desired_size);
  const status = STATUS_LABELS[product.status] || STATUS_LABELS.pending;

  const handleUpdate = () => {
    if (newSize.trim() && newSize !== product.desired_size) {
      onUpdate(product.id, { desired_size: newSize.trim() });
    }
    setEditing(false);
  };

  const hostname = (() => { try { return new URL(product.url).hostname; } catch { return product.url; } })();

  return (
    <div className="product-card">
      <div className="card-header">
        <span className="card-hostname" title={product.url}>{hostname}</span>
        <span className="card-status" style={{ color: status.color, background: status.bg }}>
          {status.label}
        </span>
      </div>
      <a href={product.url} target="_blank" rel="noopener noreferrer" className="card-url">
        {product.url.length > 60 ? product.url.slice(0, 60) + '...' : product.url}
      </a>
      <div className="card-size-row">
        <span className="card-label">Desired Size:</span>
        {editing ? (
          <>
            <input
              className="size-input"
              value={newSize}
              onChange={e => setNewSize(e.target.value)}
              autoFocus
            />
            <button className="card-btn save" onClick={handleUpdate}>Save</button>
            <button className="card-btn cancel" onClick={() => { setEditing(false); setNewSize(product.desired_size); }}>Cancel</button>
          </>
        ) : (
          <>
            <span className="card-size-value">{product.desired_size}</span>
            <button className="card-btn edit" onClick={() => setEditing(true)}>Edit</button>
          </>
        )}
      </div>
      {product.last_checked && (
        <div className="card-meta">Last checked: {new Date(product.last_checked).toLocaleString()}</div>
      )}
      <button className="card-delete" onClick={() => onDelete(product.id)}>🗑 Remove</button>
    </div>
  );
}
