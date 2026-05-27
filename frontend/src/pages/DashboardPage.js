import React, { useEffect, useState, useCallback } from 'react';
import { useMsal } from '@azure/msal-react';
import { toast } from 'react-toastify';
import axios from 'axios';
import { apiRequest } from '../authConfig';
import ProductForm from '../components/ProductForm';
import ProductList from '../components/ProductList';
import './DashboardPage.css';

const API_BASE = process.env.REACT_APP_API_BASE_URL;

export default function DashboardPage() {
  const { instance, accounts } = useMsal();
  const [products, setProducts] = useState([]);
  const [loadingList, setLoadingList] = useState(true);
  const [adding, setAdding] = useState(false);

  const getToken = useCallback(async () => {
    const response = await instance.acquireTokenSilent({ ...apiRequest, account: accounts[0] });
    return response.accessToken;
  }, [instance, accounts]);

  const authHeaders = useCallback(async () => {
    const token = await getToken();
    return { Authorization: `Bearer ${token}` };
  }, [getToken]);

  const fetchProducts = useCallback(async () => {
    setLoadingList(true);
    try {
      const headers = await authHeaders();
      const { data } = await axios.get(`${API_BASE}/products`, { headers });
      setProducts(data);
    } catch (err) {
      toast.error('Failed to load products.');
    } finally {
      setLoadingList(false);
    }
  }, [authHeaders]);

  useEffect(() => { fetchProducts(); }, [fetchProducts]);

  const handleAdd = async (payload) => {
    setAdding(true);
    try {
      const headers = await authHeaders();
      const { data } = await axios.post(`${API_BASE}/products`, payload, { headers });
      setProducts(prev => [data, ...prev]);
      toast.success('Product added! We will notify you when it is available.');
    } catch (err) {
      toast.error(err.response?.data?.error || 'Failed to add product.');
    } finally {
      setAdding(false);
    }
  };

  const handleDelete = async (id) => {
    try {
      const headers = await authHeaders();
      await axios.delete(`${API_BASE}/products/${id}`, { headers });
      setProducts(prev => prev.filter(p => p.id !== id));
      toast.success('Product removed.');
    } catch {
      toast.error('Failed to remove product.');
    }
  };

  const handleUpdate = async (id, payload) => {
    try {
      const headers = await authHeaders();
      const { data } = await axios.patch(`${API_BASE}/products/${id}`, payload, { headers });
      setProducts(prev => prev.map(p => p.id === id ? data : p));
      toast.success('Product updated.');
    } catch {
      toast.error('Failed to update product.');
    }
  };

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h1>My Tracked Products</h1>
        <p className="dashboard-sub">Add product URLs below. We check every minute and email you when your size is available.</p>
      </div>
      <ProductForm onAdd={handleAdd} loading={adding} />
      <ProductList products={products} onDelete={handleDelete} onUpdate={handleUpdate} loading={loadingList} />
    </div>
  );
}
