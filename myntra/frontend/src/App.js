import React, { useState, useEffect } from 'react';
import ProductGrid from './components/ProductGrid';
import DevPanel from './components/DevPanel';
import ProductDetail from './components/ProductDetail';
import VelocityTab from './components/VelocityTab';
import Toast from './components/Toast';
import './App.css';

const API_BASE = 'http://localhost:5000/api';

function App() {
  const [feed, setFeed] = useState([]);
  const [state, setState] = useState('discovery');
  const [zipCode, setZipCode] = useState('800008');
  const [cart, setCart] = useState([]);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [showDevPanel, setShowDevPanel] = useState(false);
  const [velocityData, setVelocityData] = useState(null);
  const [activeTab, setActiveTab] = useState('home');
  const [toast, setToast] = useState(null);
  const [devLog, setDevLog] = useState([]);

  useEffect(() => {
    fetchFeed();
  }, []);

  const fetchFeed = async () => {
    try {
      const res = await fetch(`${API_BASE}/feed`);
      const data = await res.json();
      setFeed(data.products);
      setState(data.state);
      setZipCode(data.zip_code);
    } catch (err) {
      console.error('Failed to fetch feed:', err);
    }
  };

  const addToCart = async (itemId) => {
    const res = await fetch(`${API_BASE}/cart/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId }),
    });
    const data = await res.json();
    setCart(data.cart);
    setState(data.state);
    setToast({ message: '🛒 Added to cart! Feed re-ranked.', type: 'success' });
    fetchFeed(); // Re-rank feed
  };

  const addToWishlist = async (itemId) => {
    await fetch(`${API_BASE}/wishlist/add`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ item_id: itemId }),
    });
    setToast({ message: '❤️ Wishlisted! Score boost applied.', type: 'info' });
    fetchFeed();
  };

  const openProduct = async (productId) => {
    const res = await fetch(`${API_BASE}/product/${productId}`);
    const data = await res.json();
    setSelectedProduct(data);
  };

  // Dev Panel Actions
  const devSetState = async (newState) => {
    const res = await fetch(`${API_BASE}/dev/set-state`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ state: newState }),
    });
    const data = await res.json();
    setState(data.state);
    addLog(`[STATE] Switched to: ${data.state}`);
    fetchFeed();
  };

  const devSetZip = async (zip) => {
    const res = await fetch(`${API_BASE}/dev/set-zip`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ zip_code: zip }),
    });
    const data = await res.json();
    setZipCode(data.zip_code);
    addLog(`[ZIP] Changed to: ${data.city} (${data.zip_code}). Festival: ${data.festival || 'None'}`);
    fetchFeed();
  };

  const devTimeWarp = async (hours) => {
    const res = await fetch(`${API_BASE}/dev/time-warp`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ hours }),
    });
    const data = await res.json();
    addLog(`[TIME] ${data.message}`);
    fetchFeed();
  };

  const devVelocitySurge = async () => {
    const res = await fetch(`${API_BASE}/dev/velocity-surge`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
    });
    const data = await res.json();
    setVelocityData(data);
    setActiveTab('velocity');
    addLog(data.log);
    setToast({ 
      message: `✨ Trending near you: ${data.theme}. Tap to explore.`, 
      type: 'trending' 
    });
  };

  const devSetFestival = async (festival) => {
    const res = await fetch(`${API_BASE}/dev/set-festival`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ festival }),
    });
    const data = await res.json();
    setState(data.state);
    addLog(`[FESTIVAL] ${festival ? `Activated: ${festival}` : 'Deactivated'}`);
    fetchFeed();
  };

  const devReset = async () => {
    await fetch(`${API_BASE}/dev/reset`, { method: 'POST' });
    setCart([]);
    setState('discovery');
    setVelocityData(null);
    setActiveTab('home');
    setDevLog([]);
    addLog('[SYSTEM] Session reset to fresh state');
    fetchFeed();
  };

  const addLog = (message) => {
    setDevLog(prev => [`${new Date().toLocaleTimeString()} ${message}`, ...prev]);
  };

  return (
    <div className="app">
      {/* Header */}
      <header className="header">
        <div className="header-left">
          <h1 className="logo">PinPulse</h1>
          <span className="subtitle">Myntra for Bharat</span>
        </div>
        <div className="header-center">
          <button 
            className={`tab-btn ${activeTab === 'home' ? 'active' : ''}`}
            onClick={() => setActiveTab('home')}
          >
            Home
          </button>
          {velocityData && (
            <button 
              className={`tab-btn velocity-tab ${activeTab === 'velocity' ? 'active' : ''}`}
              onClick={() => setActiveTab('velocity')}
            >
              🔥 {velocityData.theme.split(' ').slice(0, 3).join(' ')}
              <span className="pulse-dot"></span>
            </button>
          )}
        </div>
        <div className="header-right">
          <span className="state-badge">{state.replace('_', ' ')}</span>
          <span className="zip-badge">📍 {zipCode}</span>
          <span className="cart-badge">🛒 {cart.length}</span>
          <button 
            className="dev-toggle"
            onClick={() => setShowDevPanel(!showDevPanel)}
          >
            ⚙️ Dev Panel
          </button>
        </div>
      </header>

      <div className="main-content">
        {/* Dev Panel (Judge-facing) */}
        {showDevPanel && (
          <DevPanel
            state={state}
            zipCode={zipCode}
            devLog={devLog}
            onSetState={devSetState}
            onSetZip={devSetZip}
            onTimeWarp={devTimeWarp}
            onVelocitySurge={devVelocitySurge}
            onSetFestival={devSetFestival}
            onReset={devReset}
          />
        )}

        {/* Main Content Area */}
        <div className="feed-area">
          {selectedProduct ? (
            <ProductDetail
              data={selectedProduct}
              onBack={() => setSelectedProduct(null)}
              onAddToCart={addToCart}
            />
          ) : activeTab === 'velocity' && velocityData ? (
            <VelocityTab
              data={velocityData}
              onProductClick={openProduct}
              onAddToCart={addToCart}
            />
          ) : (
            <ProductGrid
              products={feed}
              onProductClick={openProduct}
              onAddToCart={addToCart}
              onWishlist={addToWishlist}
            />
          )}
        </div>
      </div>

      {/* Toast Notification */}
      {toast && (
        <Toast 
          message={toast.message} 
          type={toast.type}
          onClose={() => setToast(null)} 
        />
      )}
    </div>
  );
}

export default App;
