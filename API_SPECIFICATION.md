# ShipStation Risk Assessment API Specification

## 🎯 For Frontend Integration

This document provides complete API specifications for integrating with the ShipStation Risk Prediction Engine backend.

## Base URL
```
http://localhost:8000
```

## Authentication
Currently **no authentication required** for demo purposes.

---

## 🚀 Enhanced Risk Assessment API

### Primary Endpoint for Frontend

#### `GET /packages/{package_id}/risk-assessment`

**Purpose**: Get detailed risk assessment with factor breakdown for frontend display.

**URL Parameters**:
- `package_id` (string): Package identifier (e.g., "PKG0001")

**Response** (200 OK):
```json
{
  "score": 75,
  "confidenceLevel": 92,
  "predictedDelayDays": 2,
  "factors": {
    "carrierPerformance": {
      "score": 85,
      "weight": 30,
      "status": "Poor performance history with this carrier",
      "level": "high"
    },
    "routeDistance": {
      "score": 70,
      "weight": 25,
      "status": "Long distance route with multiple stops", 
      "level": "medium"
    },
    "weather": {
      "score": 60,
      "weight": 25,
      "status": "Minor weather concerns along route",
      "level": "medium"
    },
    "currentDelays": {
      "score": 80,
      "weight": 20,
      "status": "Carrier experiencing network-wide delays",
      "level": "high"
    }
  },
  "originalDeliveryDate": "2025-01-15T00:00:00Z",
  "revisedDeliveryDate": "2025-01-17T00:00:00Z"
}
```

**Error Responses**:

404 - Package Not Found:
```json
{
  "error": "ORDER_NOT_FOUND",
  "message": "Order with ID PKG9999 not found"
}
```

503 - Service Unavailable:
```json
{
  "error": "RISK_ASSESSMENT_UNAVAILABLE",
  "message": "Risk assessment service temporarily unavailable"
}
```

**Field Descriptions**:

| Field | Type | Range | Description |
|-------|------|-------|-------------|
| `score` | integer | 0-100 | Overall risk score (higher = more risk) |
| `confidenceLevel` | integer | 0-100 | AI confidence percentage |
| `predictedDelayDays` | integer | 0+ | Days of predicted delay |
| `factors.*.score` | integer | 0-100 | Individual factor risk score |
| `factors.*.weight` | integer | 0-100 | Weight percentage in calculation |
| `factors.*.level` | string | "low", "medium", "high" | Risk level |
| `factors.*.status` | string | - | Human-readable explanation |
| `originalDeliveryDate` | string | ISO 8601 | Original expected delivery |
| `revisedDeliveryDate` | string | ISO 8601 | Adjusted delivery date |

**Risk Level Thresholds**:
- **High Risk**: score >= 80 (2-3 days delay)
- **Medium Risk**: score >= 50 && score < 80 (1-2 days delay)  
- **Low Risk**: score < 50 (no delay predicted)

**Factor Weights** (always total 100%):
- Carrier Performance: 30%
- Route Distance: 25%
- Weather: 25%
- Current Delays: 20%

---

## 📦 Package Management

### `GET /packages`
Get all packages with basic risk scores.

**Response**:
```json
[
  {
    "package_id": "PKG0001",
    "destination_zip": "90001",
    "destination_city": "Los Angeles",
    "carrier": "USPS",
    "expected_delivery_date": "2025-08-02",
    "risk_score": 24,
    "reasons": ["Carrier USPS reliability based on historical data"]
  }
]
```

### `GET /packages/{package_id}`
Get single package with basic risk assessment.

**Response**: Same format as array item above.

---

## 📧 Customer Communication

### `POST /send-alert`
Send delay alert email to customer.

**Request Body**:
```json
{
  "package_id": "PKG0001",
  "customer_email": "customer@example.com"
}
```

**Response**:
```json
{
  "success": true,
  "message": "Email sent successfully",
  "email_sent": true
}
```

---

## 📊 Customer Actions

### `POST /action`
Log customer response to delay alert.

**Request Body**:
```json
{
  "package_id": "PKG0001",
  "action": "Accept Delay",
  "customer_id": "CUST123",
  "notes": "Customer prefers delay over cancel"
}
```

**Valid Actions**:
- "Accept Delay"
- "Request Refund"  
- "Resend"

**Response**:
```json
{
  "success": true,
  "message": "Action 'Accept Delay' logged successfully for package PKG0001",
  "action_logged": true
}
```

### `GET /actions`
Get customer actions with analytics.

**Query Parameters**:
- `limit` (integer, optional): Number of actions to return (default: 20)

**Response**:
```json
{
  "total_actions": 156,
  "recent_actions": [
    {
      "id": 1,
      "package_id": "PKG0001",
      "action": "Accept Delay",
      "customer_id": "CUST123",
      "notes": "Customer prefers delay",
      "timestamp": "2025-08-01T10:30:00",
      "processed": false,
      "processing_notes": null
    }
  ],
  "statistics": {
    "action_breakdown": [
      {"action": "Accept Delay", "count": 89},
      {"action": "Request Refund", "count": 45},
      {"action": "Resend", "count": 22}
    ],
    "recent_activity": 23,
    "processing_stats": {
      "total": 156,
      "processed": 134,
      "pending": 22
    }
  }
}
```

---

## 🏥 Health & Monitoring

### `GET /health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "timestamp": "2025-08-01T12:00:00.000Z",
  "version": "1.0.0",
  "services": {
    "risk_engine": "operational",
    "weather_service": "operational", 
    "email_service": "operational"
  }
}
```

---

## 🔧 Admin/Analytics APIs

### `GET /admin/performance-stats`
Get comprehensive performance dashboard data.

**Response**:
```json
{
  "success": true,
  "data": {
    "carriers": [
      {
        "carrier": "FedEx",
        "deliveries": 800000,
        "on_time": 760000,
        "reliability": 88
      }
    ],
    "locations": [
      {
        "zip": "33101",
        "city": "Miami",
        "risk": 25,
        "traffic": 20
      }
    ],
    "recent_performance": {
      "total_deliveries": 1245,
      "delayed_deliveries": 89,
      "average_delay_hours": 4.2
    },
    "customer_actions": {
      "action_breakdown": [
        {"action": "Accept Delay", "count": 89}
      ],
      "recent_activity": 23,
      "processing_stats": {
        "total": 156,
        "processed": 134,
        "pending": 22
      }
    }
  }
}
```

### `POST /admin/initialize-database`
Initialize database with sample data. **Run this first!**

**Response**:
```json
{
  "success": true,
  "message": "Database initialized successfully"
}
```

### `GET /admin/database-status`
Check database health and statistics.

**Response**:
```json
{
  "database_exists": true,
  "database_path": "risk_data.db",
  "database_size_bytes": 245760,
  "table_counts": {
    "carrier_performance": 4,
    "geographic_risk": 5,
    "delivery_performance": 20,
    "temporal_risk": 6,
    "delivery_outcomes": 0,
    "customer_actions": 156
  },
  "status": "healthy"
}
```

### `POST /admin/record-delivery`
Record actual delivery outcome for ML learning.

**Request Body**:
```json
{
  "package_id": "PKG0001",
  "carrier": "UPS",
  "origin_zip": "10001",
  "destination_zip": "90210", 
  "scheduled_date": "2025-08-01",
  "actual_date": "2025-08-03",
  "delay_reasons": ["weather", "traffic"]
}
```

**Response**:
```json
{
  "success": true,
  "message": "Delivery outcome recorded for package PKG0001",
  "recorded_data": {
    "package_id": "PKG0001",
    "carrier": "UPS",
    "destination_zip": "90210",
    "scheduled_date": "2025-08-01", 
    "actual_date": "2025-08-03",
    "delay_reasons": ["weather", "traffic"]
  }
}
```

---

## 📊 Sample Data

### Available Package IDs for Testing:
- `PKG0001` through `PKG0075` (75 realistic packages)
- Mix of carriers: UPS, FedEx, USPS, DHL
- Various US cities and zip codes
- Different delivery dates and risk levels

### High-Risk Test Cases:
- `PKG0001` - Los Angeles via USPS
- `PKG0043` - Seattle via USPS (weather risk)
- Any Miami packages (hurricane season)

### Low-Risk Test Cases:
- `PKG0025` - Portland via FedEx  
- Any Beverly Hills packages (good infrastructure)

---

## 🚨 Error Handling

All endpoints return consistent error format:

**400 Bad Request**:
```json
{
  "detail": "Validation error message"
}
```

**404 Not Found**:
```json
{
  "detail": "Resource not found message"
}
```

**500 Internal Server Error**:
```json
{
  "detail": "Internal server error message"
}
```

---

## ⚡ Performance & Caching

- **Response Time**: <500ms target
- **Caching**: 1-hour TTL on risk assessments
- **Cache Key**: `package_id + delivery_date`
- **Concurrent Requests**: Supported
- **Rate Limiting**: Not implemented (add in production)

---

## 🔒 Production Considerations

### Security (TODO for production):
- Add API key authentication
- Implement rate limiting
- Add input validation middleware
- Use HTTPS only

### Monitoring:
- Health check endpoint available
- Structured logging enabled
- Performance metrics in admin endpoints
- Database health monitoring

---

## 🧪 Testing Examples

### JavaScript/Frontend Integration:

```javascript
// Get enhanced risk assessment
const getRiskAssessment = async (packageId) => {
  const response = await fetch(`/packages/${packageId}/risk-assessment`);
  if (!response.ok) {
    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
  }
  return await response.json();
};

// Usage
try {
  const risk = await getRiskAssessment('PKG0001');
  console.log(`Risk Score: ${risk.score}/100`);
  console.log(`Confidence: ${risk.confidenceLevel}%`);
  console.log(`Predicted Delay: ${risk.predictedDelayDays} days`);
  
  // Display factors
  Object.entries(risk.factors).forEach(([name, factor]) => {
    console.log(`${name}: ${factor.score} (${factor.level}) - ${factor.status}`);
  });
} catch (error) {
  console.error('Risk assessment failed:', error);
}
```

### cURL Testing:

```bash
# Test enhanced risk assessment
curl -X GET "http://localhost:8000/packages/PKG0001/risk-assessment" \
     -H "Accept: application/json"

# Log customer action
curl -X POST "http://localhost:8000/action" \
     -H "Content-Type: application/json" \
     -d '{
       "package_id": "PKG0001",
       "action": "Accept Delay",
       "customer_id": "CUST123"
     }'

# Get performance stats
curl -X GET "http://localhost:8000/admin/performance-stats" \
     -H "Accept: application/json"
```

---

## 📝 Integration Checklist

For your friend to integrate successfully:

- [ ] **1. Start Backend**: `python run_server.py`
- [ ] **2. Initialize DB**: `POST /admin/initialize-database`
- [ ] **3. Test Health**: `GET /health`
- [ ] **4. Test Risk API**: `GET /packages/PKG0001/risk-assessment`
- [ ] **5. Check Available Packages**: `GET /packages`
- [ ] **6. Implement Frontend**: Use enhanced risk assessment endpoint
- [ ] **7. Add Error Handling**: Handle 404/503 responses
- [ ] **8. Test Customer Actions**: `POST /action`

**Questions? Check the interactive docs at**: http://localhost:8000/docs