# Smart Shipment Risk Prediction Engine

A FastAPI-based microservice that uses **machine learning principles** and **SQLite database intelligence** to predict delivery risk scores and provide customer alerting capabilities.

## 🚀 Features

- **Enhanced Risk Assessment**: Detailed factor breakdown for frontend integration
- **Smart Risk Scoring**: Database-driven risk scoring (0-100) using historical performance data
- **Multi-factor Analysis**: Weather, carrier reliability, geographic risks, temporal patterns
- **Continuous Learning**: System improves predictions from actual delivery outcomes
- **Customer Alerts**: Email notifications via SendGrid for high-risk shipments  
- **Action Logging**: Track customer responses (Accept Delay/Refund/Resend)
- **Admin Dashboard**: Performance analytics and risk factor management
- **RESTful API**: Clean, documented endpoints for frontend integration
- **Performance Optimized**: 1-hour caching with <500ms response times

## 📋 API Endpoints

### Core Endpoints

- `GET /packages` - List all packages with smart risk scores
- `GET /packages/{id}` - Get single package risk assessment  
- **`GET /packages/{id}/risk-assessment`** - **Enhanced risk assessment for frontend** 🎯
- `POST /send-alert` - Send delay alert email to customer
- `POST /action` - Log customer action choice
- `GET /actions` - Get customer actions with statistics
- `GET /health` - Health check endpoint

### Admin/Analytics Endpoints

- `GET /admin/performance-stats` - Get performance statistics from database
- `POST /admin/record-delivery` - Record actual delivery outcome for learning
- `GET /admin/risk-factors/{zip_code}` - Get risk factors for specific zip code
- `GET /admin/carrier-analysis/{carrier}` - Get detailed carrier performance analysis
- `POST /admin/initialize-database` - Initialize database (run this first!)
- `GET /admin/database-status` - Get database health and statistics

## 🎯 Enhanced Risk Assessment API (NEW!)

The **main endpoint for frontend integration**:

### Endpoint: `GET /packages/{id}/risk-assessment`

**Perfect for ShipStation Risk Delivery Assessment feature!**

### Response Format:
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
  "originalDeliveryDate": "2024-01-15T00:00:00Z",
  "revisedDeliveryDate": "2024-01-17T00:00:00Z"
}
```

### Legacy Response Format (Simple):
```json
{
  "package_id": "PKG001",
  "destination_zip": "98101", 
  "destination_city": "Seattle",
  "carrier": "UPS",
  "expected_delivery_date": "2025-08-03",
  "risk_score": 45,
  "reasons": ["UPS has historical delivery challenges", "destination 98101 has delivery complexity"]
}
```

## 🛠️ Setup & Installation

### Prerequisites
- Python 3.8+
- pip

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd hackyeah-2025

# Install dependencies
pip install -r requirements.txt

# Set up environment variables (optional)
cp .env.example .env
# Edit .env with your API keys
```

### Environment Variables

```bash
# Server config
PORT=8000
HOST=0.0.0.0

# APIs (optional - will use mock mode if not provided)
OPENWEATHER_API_KEY=your_key_here
SENDGRID_API_KEY=your_key_here
FROM_EMAIL=noreply@yourcompany.com
```

## 🚀 Running the Service

### Quick Start (for your friend):
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start server
python run_server.py

# 3. Initialize database (IMPORTANT!)
curl -X POST http://localhost:8000/admin/initialize-database

# 4. Test the enhanced risk assessment
curl http://localhost:8000/packages/PKG0001/risk-assessment
```

### Development Server
```bash
python run_server.py
```

### Direct uvicorn
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Access Points
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

### Available Package IDs for Testing:
- `PKG0001` through `PKG0075` (75 realistic packages)
- Each has different risk scenarios (carriers, locations, dates)

## 🧪 Testing

```bash
# Run basic API tests
python test_api.py

# Test enhanced risk assessment
python test_risk_api.py

# Run unit tests
python -m pytest test_main.py -v

# Test with coverage
python -m pytest test_main.py --cov=. --cov-report=html
```

## 📁 Project Structure

```
├── main.py              # FastAPI application and endpoints
├── models.py            # Pydantic data models
├── risk_engine.py       # Smart risk scoring logic
├── database.py          # SQLite database and analytics
├── weather_service.py   # OpenWeatherMap integration
├── email_service.py     # SendGrid email service
├── mock_data.py         # Sample shipment data
├── test_main.py         # Unit tests
├── run_server.py        # Server startup script
├── requirements.txt     # Python dependencies
├── .env.example         # Environment variables template
├── risk_data.db         # SQLite database (auto-created)
└── README.md           # This file
```

## 🧠 Smart Risk Scoring with SQLite Database

The risk engine uses a **data-driven approach** with SQLite database storing historical performance:

### 🚚 Carrier Risk (Dynamic)
- Based on **actual delivery performance data**
- Reliability scores calculated from historical success rates
- Peak season performance adjustments
- Continuously updated from real outcomes

### 📍 Geographic Risk (Database-Driven)
- **Urban vs Rural** complexity factors
- **Traffic congestion** analysis by zip code
- **Regional weather** risk multipliers
- Historical delivery challenges by area

### 📊 Carrier-Zip Performance (Historical Data)
- **Specific combination** risk (e.g., UPS to Seattle)
- Delay rates and average delay times
- Success rate tracking per route
- Learning from actual delivery outcomes

### 🌤️ Weather Risk (Real-time + Historical)
- Live weather API integration
- Historical weather pattern analysis
- Severe weather (storms, snow): +30 points
- Rain/drizzle: +15 points
- High winds: +10 points

### 📅 Temporal Risk (Pattern Recognition)
- **Day of week** patterns (Monday package backlog)
- **Seasonal trends** (December holiday rush)
- **Holiday period** identification
- Historical temporal delay analysis

### ⏰ Delivery Timeline (Urgency Factor)
- Same day: +25 points
- Next day: +20 points
- Within 3 days: +10 points

## 🎯 Continuous Learning System

The system **learns and improves** from every delivery:
- Records actual delivery outcomes
- Updates performance metrics automatically
- Adjusts risk calculations based on real data
- Identifies new risk patterns over time

## 📧 Email Alerts

Sample email includes:
- Package details and risk score
- Specific delay reasons
- Customer action buttons (Accept/Refund/Resend)
- Professional HTML formatting

## 🔌 Frontend Integration

### Sample JavaScript Usage

```javascript
// Get all packages with smart risk scores
const packages = await fetch('/packages').then(r => r.json());

// Send alert for high-risk package
await fetch('/send-alert', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    package_id: 'PKG001',
    customer_email: 'customer@example.com'
  })
});

// Log customer action
await fetch('/action', {
  method: 'POST', 
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    package_id: 'PKG001',
    action: 'Accept Delay',
    customer_id: 'CUST123'
  })
});

// Record actual delivery outcome for learning
await fetch('/admin/record-delivery', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    package_id: 'PKG001',
    carrier: 'UPS',
    scheduled_date: '2025-08-01',
    actual_date: '2025-08-03',
    delay_reasons: ['weather', 'traffic']
  })
});

// Get performance analytics
const stats = await fetch('/admin/performance-stats').then(r => r.json());
console.log('Carrier performance:', stats.data.carriers);
```

## 📊 Admin Dashboard Features

### Performance Analytics
```bash
# Get overall performance statistics
GET /admin/performance-stats

# Analyze specific zip code risks
GET /admin/risk-factors/98101

# Analyze carrier performance
GET /admin/carrier-analysis/UPS

# Check database health
GET /admin/database-status
```

### Learning from Outcomes
```bash
# Record delivery outcome to improve predictions
POST /admin/record-delivery
{
  "package_id": "PKG001",
  "carrier": "UPS", 
  "actual_date": "2025-08-03",
  "delay_reasons": ["weather", "traffic"]
}
```

## 📈 Sample Data & Database Schema

The system includes:
- **5 realistic sample packages** covering different risk scenarios
- **Historical performance data** for 4 major carriers
- **Geographic risk profiles** for major US cities
- **Temporal patterns** (holidays, day-of-week effects)
- **Delivery outcome tracking** for continuous learning

### Database Tables:
- `carrier_performance` - Historical carrier metrics
- `geographic_risk` - Zip code risk factors  
- `delivery_performance` - Carrier-zip specific data
- `temporal_risk` - Time-based risk patterns
- `delivery_outcomes` - Actual delivery results for learning

## 🚦 Production Considerations

### Security
- Add authentication/authorization for admin endpoints
- Implement rate limiting
- Validate all inputs thoroughly
- Use HTTPS in production

### Scalability  
- Database is already optimized with indexes
- Add caching layer (Redis) for high-traffic endpoints
- Implement proper logging and monitoring
- Add circuit breakers for external APIs

### Monitoring
- Health checks implemented
- Performance statistics endpoints
- Database health monitoring
- Structured logging with detailed debugging

## 🤝 API Examples

### Get Smart Risk Score
```bash
curl http://localhost:8000/packages/PKG001
```

### Send Alert
```bash
curl -X POST http://localhost:8000/send-alert \
  -H "Content-Type: application/json" \
  -d '{"package_id": "PKG001", "customer_email": "test@example.com"}'
```

### Record Delivery Outcome (Learning)
```bash
curl -X POST http://localhost:8000/admin/record-delivery \
  -H "Content-Type: application/json" \
  -d '{"package_id": "PKG001", "carrier": "UPS", "actual_date": "2025-08-03"}'
```

### Get Performance Analytics
```bash
curl http://localhost:8000/admin/performance-stats
```

## 🎯 Hackathon Focus

This implementation prioritizes:
- ✅ **Smart, data-driven** risk calculation
- ✅ **Continuous learning** from delivery outcomes
- ✅ **Comprehensive analytics** and admin tools
- ✅ **Production-ready** database architecture
- ✅ **Easy frontend integration** with rich APIs
- ✅ **Detailed logging** for debugging and monitoring

Perfect for demonstrating **real AI/ML principles** in a hackathon setting while being production-scalable!