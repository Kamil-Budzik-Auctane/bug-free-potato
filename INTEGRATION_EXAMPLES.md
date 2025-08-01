# Integration Examples for ShipStation Risk Assessment

## 🎯 Quick Integration Guide for Frontend Developers

### Setup & First Test

```bash
# 1. Clone and setup backend
git clone <repo>
cd bug-free-potato
pip install -r requirements.txt

# 2. Start server
python run_server.py

# 3. Initialize database (CRITICAL!)
curl -X POST http://localhost:8000/admin/initialize-database

# 4. Test basic connectivity
curl http://localhost:8000/health
```

---

## 🚀 JavaScript/React Integration

### Basic Risk Assessment Hook

```javascript
// useRiskAssessment.js
import { useState, useEffect } from 'react';

export const useRiskAssessment = (packageId) => {
  const [riskData, setRiskData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!packageId) return;

    const fetchRiskAssessment = async () => {
      setLoading(true);
      setError(null);
      
      try {
        const response = await fetch(`/packages/${packageId}/risk-assessment`);
        
        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.message || `HTTP ${response.status}`);
        }
        
        const data = await response.json();
        setRiskData(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRiskAssessment();
  }, [packageId]);

  return { riskData, loading, error };
};
```

### Risk Assessment Component

```jsx
// RiskAssessmentCard.jsx
import React from 'react';
import { useRiskAssessment } from './useRiskAssessment';

const RiskAssessmentCard = ({ packageId }) => {
  const { riskData, loading, error } = useRiskAssessment(packageId);

  if (loading) return <div>Loading risk assessment...</div>;
  if (error) return <div>Error: {error}</div>;
  if (!riskData) return null;

  const getRiskColor = (score) => {
    if (score >= 80) return '#dc3545'; // red
    if (score >= 50) return '#ffc107'; // yellow
    return '#28a745'; // green
  };

  const getRiskLabel = (score) => {
    if (score >= 80) return 'High Risk';
    if (score >= 50) return 'Medium Risk';
    return 'Low Risk';
  };

  return (
    <div className="risk-assessment-card">
      <div className="risk-header">
        <h3>Delivery Risk Assessment</h3>
        <div 
          className="risk-score"
          style={{ color: getRiskColor(riskData.score) }}
        >
          {riskData.score}/100 - {getRiskLabel(riskData.score)}
        </div>
      </div>

      <div className="confidence-level">
        AI Confidence: {riskData.confidenceLevel}%
      </div>

      {riskData.predictedDelayDays > 0 && (
        <div className="delay-prediction">
          ⚠️ Predicted Delay: {riskData.predictedDelayDays} days
          <div className="revised-date">
            Revised Delivery: {new Date(riskData.revisedDeliveryDate).toLocaleDateString()}
          </div>
        </div>
      )}

      <div className="risk-factors">
        <h4>Risk Factors:</h4>
        {Object.entries(riskData.factors).map(([factorName, factor]) => (
          <div key={factorName} className="factor">
            <div className="factor-header">
              <span className="factor-name">
                {factorName.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
              </span>
              <span className={`factor-level ${factor.level}`}>
                {factor.score}/100 ({factor.level})
              </span>
            </div>
            <div className="factor-status">{factor.status}</div>
            <div className="factor-weight">Weight: {factor.weight}%</div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default RiskAssessmentCard;
```

### CSS Styles

```css
/* RiskAssessment.css */
.risk-assessment-card {
  border: 1px solid #ddd;
  border-radius: 8px;
  padding: 20px;
  margin: 16px 0;
  background: white;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

.risk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.risk-score {
  font-size: 1.5em;
  font-weight: bold;
}

.confidence-level {
  color: #666;
  margin-bottom: 16px;
}

.delay-prediction {
  background: #fff3cd;
  padding: 12px;
  border-radius: 4px;
  margin-bottom: 16px;
  border-left: 4px solid #ffc107;
}

.revised-date {
  font-size: 0.9em;
  color: #666;
  margin-top: 4px;
}

.risk-factors h4 {
  margin-bottom: 12px;
  color: #333;
}

.factor {
  background: #f8f9fa;
  padding: 12px;
  margin-bottom: 8px;
  border-radius: 4px;
}

.factor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 4px;
}

.factor-name {
  font-weight: 500;
}

.factor-level.high { color: #dc3545; }
.factor-level.medium { color: #ffc107; }
.factor-level.low { color: #28a745; }

.factor-status {
  color: #666;
  font-size: 0.9em;
  margin-bottom: 4px;
}

.factor-weight {
  color: #999;
  font-size: 0.8em;
}
```

---

## 📦 Package List Integration

### Package List with Risk Indicators

```jsx
// PackageList.jsx
import React, { useState, useEffect } from 'react';

const PackageList = () => {
  const [packages, setPackages] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchPackages = async () => {
      try {
        const response = await fetch('/packages');
        const data = await response.json();
        setPackages(data);
      } catch (error) {
        console.error('Failed to fetch packages:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchPackages();
  }, []);

  const getRiskBadge = (score) => {
    if (score >= 80) return { label: 'HIGH', class: 'risk-high' };
    if (score >= 50) return { label: 'MED', class: 'risk-medium' };
    return { label: 'LOW', class: 'risk-low' };
  };

  if (loading) return <div>Loading packages...</div>;

  return (
    <div className="package-list">
      <h2>Shipments ({packages.length})</h2>
      {packages.map(pkg => {
        const risk = getRiskBadge(pkg.risk_score);
        return (
          <div key={pkg.package_id} className="package-item">
            <div className="package-header">
              <span className="package-id">{pkg.package_id}</span>
              <span className={`risk-badge ${risk.class}`}>
                {risk.label} {pkg.risk_score}
              </span>
            </div>
            <div className="package-details">
              <span>{pkg.destination_city} via {pkg.carrier}</span>
              <span>Due: {pkg.expected_delivery_date}</span>
            </div>
            {pkg.reasons.length > 0 && (
              <div className="risk-reasons">
                {pkg.reasons.slice(0, 2).map((reason, idx) => (
                  <span key={idx} className="reason-tag">{reason}</span>
                ))}
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default PackageList;
```

---

## 🚨 Customer Action Integration

### Customer Action Handler

```javascript
// customerActions.js
export const CustomerActions = {
  async logAction(packageId, action, customerId, notes = null) {
    try {
      const response = await fetch('/action', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          package_id: packageId,
          action: action,
          customer_id: customerId,
          notes: notes
        })
      });

      if (!response.ok) {
        throw new Error(`Failed to log action: ${response.status}`);
      }

      return await response.json();
    } catch (error) {
      console.error('Error logging customer action:', error);
      throw error;
    }
  },

  async sendAlert(packageId, customerEmail) {
    try {
      const response = await fetch('/send-alert', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          package_id: packageId,
          customer_email: customerEmail
        })
      });

      return await response.json();
    } catch (error) {
      console.error('Error sending alert:', error);
      throw error;
    }
  }
};
```

### Customer Action Buttons Component

```jsx
// CustomerActionButtons.jsx
import React, { useState } from 'react';
import { CustomerActions } from './customerActions';

const CustomerActionButtons = ({ packageId, customerId, onActionComplete }) => {
  const [loading, setLoading] = useState(null);

  const handleAction = async (action) => {
    setLoading(action);
    
    try {
      const result = await CustomerActions.logAction(packageId, action, customerId);
      console.log('Action logged:', result);
      onActionComplete && onActionComplete(action, result);
    } catch (error) {
      alert(`Failed to log action: ${error.message}`);
    } finally {
      setLoading(null);
    }
  };

  const actions = [
    { key: 'Accept Delay', label: 'Accept Delay', style: 'success' },
    { key: 'Request Refund', label: 'Request Refund', style: 'danger' },
    { key: 'Resend', label: 'Resend Package', style: 'primary' }
  ];

  return (
    <div className="customer-actions">
      <h4>Customer Options:</h4>
      <div className="action-buttons">
        {actions.map(action => (
          <button
            key={action.key}
            className={`btn btn-${action.style}`}
            onClick={() => handleAction(action.key)}
            disabled={loading === action.key}
          >
            {loading === action.key ? 'Processing...' : action.label}
          </button>
        ))}
      </div>
    </div>
  );
};

export default CustomerActionButtons;
```

---

## 📊 Admin Dashboard Integration

### Performance Stats Component

```jsx
// AdminDashboard.jsx
import React, { useState, useEffect } from 'react';

const AdminDashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await fetch('/admin/performance-stats');
        const data = await response.json();
        setStats(data.data);
      } catch (error) {
        console.error('Failed to fetch stats:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, []);

  if (loading) return <div>Loading dashboard...</div>;
  if (!stats) return <div>No data available</div>;

  return (
    <div className="admin-dashboard">
      <h2>Performance Dashboard</h2>
      
      {/* Carrier Performance */}
      <div className="stats-section">
        <h3>Carrier Performance</h3>
        <div className="stats-grid">
          {stats.carriers.map(carrier => (
            <div key={carrier.carrier} className="stat-card">
              <h4>{carrier.carrier}</h4>
              <div className="stat-value">{carrier.reliability}%</div>
              <div className="stat-label">Reliability</div>
              <div className="stat-detail">
                {carrier.on_time.toLocaleString()} / {carrier.deliveries.toLocaleString()} on time
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Recent Performance */}
      <div className="stats-section">
        <h3>Recent Performance (30 days)</h3>
        <div className="stats-grid">
          <div className="stat-card">
            <div className="stat-value">{stats.recent_performance.total_deliveries}</div>
            <div className="stat-label">Total Deliveries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.recent_performance.delayed_deliveries}</div>
            <div className="stat-label">Delayed Deliveries</div>
          </div>
          <div className="stat-card">
            <div className="stat-value">{stats.recent_performance.average_delay_hours.toFixed(1)}h</div>
            <div className="stat-label">Avg Delay</div>
          </div>
        </div>
      </div>

      {/* Customer Actions */}
      {stats.customer_actions && (
        <div className="stats-section">
          <h3>Customer Actions</h3>
          <div className="stats-grid">
            {stats.customer_actions.action_breakdown.map(action => (
              <div key={action.action} className="stat-card">
                <div className="stat-value">{action.count}</div>
                <div className="stat-label">{action.action}</div>
              </div>
            ))}
          </div>
          <div className="processing-stats">
            <span>Processing: {stats.customer_actions.processing_stats.pending} pending, </span>
            <span>{stats.customer_actions.processing_stats.processed} completed</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default AdminDashboard;
```

---

## 🔧 Error Handling & Loading States

### Error Boundary Component

```jsx
// ErrorBoundary.jsx
import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }

  componentDidCatch(error, errorInfo) {
    console.error('Risk Assessment Error:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="error-boundary">
          <h3>Risk Assessment Unavailable</h3>
          <p>Unable to load risk assessment data. Please try again later.</p>
          <details>
            <summary>Error Details</summary>
            <pre>{this.state.error?.toString()}</pre>
          </details>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
```

### API Error Handler

```javascript
// apiClient.js
class APIClient {
  constructor(baseURL = '') {
    this.baseURL = baseURL;
  }

  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    
    try {
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        // Handle specific error formats from backend
        const errorData = await response.json().catch(() => ({}));
        
        if (response.status === 404 && errorData.error === 'ORDER_NOT_FOUND') {
          throw new Error(`Package not found: ${errorData.message}`);
        }
        
        if (response.status === 503 && errorData.error === 'RISK_ASSESSMENT_UNAVAILABLE') {
          throw new Error('Risk assessment service is temporarily unavailable');
        }
        
        throw new Error(`API Error: ${response.status} - ${errorData.detail || response.statusText}`);
      }

      return await response.json();
    } catch (error) {
      if (error instanceof TypeError && error.message.includes('fetch')) {
        throw new Error('Unable to connect to risk assessment service');
      }
      throw error;
    }
  }

  async getRiskAssessment(packageId) {
    return this.request(`/packages/${packageId}/risk-assessment`);
  }

  async getPackages() {
    return this.request('/packages');
  }

  async logCustomerAction(packageId, action, customerId, notes) {
    return this.request('/action', {
      method: 'POST',
      body: JSON.stringify({
        package_id: packageId,
        action,
        customer_id: customerId,
        notes
      })
    });
  }
}

export const apiClient = new APIClient();
```

---

## 🧪 Testing Integration

### Unit Tests for Risk Assessment

```javascript
// riskAssessment.test.js
import { renderHook, waitFor } from '@testing-library/react';
import { useRiskAssessment } from './useRiskAssessment';

// Mock fetch
global.fetch = jest.fn();

describe('useRiskAssessment', () => {
  beforeEach(() => {
    fetch.mockClear();
  });

  test('fetches risk assessment successfully', async () => {
    const mockRiskData = {
      score: 75,
      confidenceLevel: 90,
      predictedDelayDays: 2,
      factors: {
        carrierPerformance: { score: 85, weight: 30, status: 'High risk', level: 'high' }
      },
      originalDeliveryDate: '2025-01-15T00:00:00Z',
      revisedDeliveryDate: '2025-01-17T00:00:00Z'
    };

    fetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockRiskData,
    });

    const { result } = renderHook(() => useRiskAssessment('PKG0001'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.riskData).toEqual(mockRiskData);
    expect(result.current.error).toBeNull();
    expect(fetch).toHaveBeenCalledWith('/packages/PKG0001/risk-assessment');
  });

  test('handles package not found error', async () => {
    fetch.mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({
        error: 'ORDER_NOT_FOUND',
        message: 'Order with ID PKG9999 not found'
      }),
    });

    const { result } = renderHook(() => useRiskAssessment('PKG9999'));

    await waitFor(() => {
      expect(result.current.loading).toBe(false);
    });

    expect(result.current.error).toBe('Order with ID PKG9999 not found');
    expect(result.current.riskData).toBeNull();
  });
});
```

---

## 🚀 Quick Start Template

### Complete Example App

```jsx
// App.jsx
import React, { useState } from 'react';
import RiskAssessmentCard from './components/RiskAssessmentCard';
import PackageList from './components/PackageList';
import AdminDashboard from './components/AdminDashboard';
import ErrorBoundary from './components/ErrorBoundary';
import './App.css';

function App() {
  const [selectedPackage, setSelectedPackage] = useState('PKG0001');
  const [activeTab, setActiveTab] = useState('packages');

  return (
    <div className="App">
      <header className="App-header">
        <h1>ShipStation Risk Assessment</h1>
        <nav>
          <button 
            className={activeTab === 'packages' ? 'active' : ''}
            onClick={() => setActiveTab('packages')}
          >
            Packages
          </button>
          <button 
            className={activeTab === 'admin' ? 'active' : ''}
            onClick={() => setActiveTab('admin')}
          >
            Dashboard
          </button>
        </nav>
      </header>

      <main>
        <ErrorBoundary>
          {activeTab === 'packages' && (
            <div className="packages-view">
              <div className="packages-sidebar">
                <PackageList onSelectPackage={setSelectedPackage} />
              </div>
              <div className="risk-assessment-main">
                {selectedPackage && (
                  <RiskAssessmentCard packageId={selectedPackage} />
                )}
              </div>
            </div>
          )}

          {activeTab === 'admin' && <AdminDashboard />}
        </ErrorBoundary>
      </main>
    </div>
  );
}

export default App;
```

---

## 📝 Integration Checklist

- [ ] **Backend Setup**: Server running on localhost:8000
- [ ] **Database Init**: POST /admin/initialize-database called
- [ ] **Health Check**: GET /health returns "healthy"
- [ ] **Risk Assessment**: GET /packages/PKG0001/risk-assessment works
- [ ] **Package List**: GET /packages returns 75 packages
- [ ] **Error Handling**: 404/503 errors handled gracefully
- [ ] **Loading States**: UI shows loading indicators
- [ ] **Customer Actions**: POST /action functionality working
- [ ] **Performance**: Response times under 500ms
- [ ] **Caching**: Repeated requests use cache (check logs)

**Need help?** Check the interactive docs at http://localhost:8000/docs