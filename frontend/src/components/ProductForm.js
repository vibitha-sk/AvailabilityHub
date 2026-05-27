import React, { useState } from 'react';
import './ProductForm.css';

const SIZE_OPTIONS = ['XS', 'S', 'M', 'L', 'XL', 'XXL', '6', '7', '8', '9', '10', '11', '12'];

export default function ProductForm({ onAdd, loading }) {
  const [url, setUrl] = useState('');
  const [size, setSize] = useState('');
  const [customSize, setCustomSize] = useState('');
  const [error, setError] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    setError('');
    const finalSize = size === 'custom' ? customSize.trim() : size;
    if (!url.trim()) return setError('Product URL is required.');
    try { new URL(url.trim()); } catch { return setError('Please enter a valid URL.'); }
    if (!finalSize) return setError('Please select or enter a size.');
    onAdd({ url: url.trim(), desired_size: finalSize });
    setUrl('');
    setSize('');
    setCustomSize('');
  };

  return (
    <form className="product-form" onSubmit={handleSubmit}>
      <h2 className="form-title">Track a New Product</h2>
      {error && <div className="form-error">{error}</div>}
      <div className="form-group">
        <label htmlFor="url">Product URL</label>
        <input
          id="url"
          type="url"
          placeholder="https://example.com/product/shoes-blue"
          value={url}
          onChange={e => setUrl(e.target.value)}
          className="form-input"
        />
      </div>
      <div className="form-group">
        <label htmlFor="size">Desired Size</label>
        <select id="size" value={size} onChange={e => setSize(e.target.value)} className="form-input">
          <option value="">-- Select a size --</option>
          {SIZE_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
          <option value="custom">Other (type below)</option>
        </select>
      </div>
      {size === 'custom' && (
        <div className="form-group">
          <label htmlFor="customSize">Custom Size</label>
          <input
            id="customSize"
            type="text"
            placeholder="e.g. 42EU, 27W"
            value={customSize}
            onChange={e => setCustomSize(e.target.value)}
            className="form-input"
          />
        </div>
      )}
      <button type="submit" className="btn-submit" disabled={loading}>
        {loading ? 'Adding...' : '+ Add Product'}
      </button>
    </form>
  );
}
