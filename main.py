from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from models import (
    EnrichedPackage, AlertRequest, AlertResponse, 
    ActionRequest, ActionResponse, Package
)
from mock_data import MOCK_PACKAGES
from risk_engine import RiskScoringEngine
from email_service import EmailService
from database import risk_db
from typing import List, Optional
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging with detailed format
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Shipment Risk Prediction Engine",
    description="Microservice for predicting delivery risk scores and managing shipment alerts",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
logger.info("Initializing Shipment Risk Prediction Engine")
logger.info(f"Environment variables:")
logger.info(f"   OPENWEATHER_API_KEY: {'SET' if os.getenv('OPENWEATHER_API_KEY') else 'NOT SET (will use mock)'}")
logger.info(f"   SENDGRID_API_KEY: {'SET' if os.getenv('SENDGRID_API_KEY') else 'NOT SET (will use mock)'}")
logger.info(f"   FROM_EMAIL: {os.getenv('FROM_EMAIL', 'noreply@shipstation.com')}")

risk_engine = RiskScoringEngine()
email_service = EmailService()

# In-memory storage for customer actions (replace with database in production)
customer_actions = []

logger.info("All services initialized successfully")


# Commented out automatic startup - use manual endpoint instead
# @app.on_event("startup")
# async def startup_event():
#     """Initialize database on startup"""
#     try:
#         logger.info("Initializing smart risk database...")
#         await risk_db.initialize()
#         logger.info("Database initialization completed")
#     except Exception as e:
#         logger.error(f"Database initialization failed: {e}")
#         import traceback
#         traceback.print_exc()
#         # Don't raise - let server start even if DB fails
#         logger.warning("Server starting without database initialization")


async def get_enriched_package(package: Package) -> EnrichedPackage:
    """Convert a Package to an EnrichedPackage with risk assessment"""
    risk_assessment = await risk_engine.calculate_risk_score(package)
    
    return EnrichedPackage(
        package_id=package.package_id,
        destination_zip=package.destination_zip,
        destination_city=package.destination_city,
        carrier=package.carrier,
        expected_delivery_date=package.expected_delivery_date,
        risk_score=risk_assessment.risk_score,
        reasons=risk_assessment.reasons
    )


@app.get("/", summary="Root endpoint")
async def root():
    """Root endpoint with basic service information"""
    return {
        "service": "Shipment Risk Prediction Engine",
        "version": "1.0.0",
        "status": "running",
        "endpoints": [
            "/packages",
            "/packages/{id}",
            "/send-alert",
            "/action",
            "/health"
        ]
    }


@app.get("/packages", response_model=List[EnrichedPackage], summary="Get all packages with risk scores")
async def get_packages() -> List[EnrichedPackage]:
    """
    Returns mocked shipment list enriched with:
    - risk_score (0–100)
    - list of reasons (e.g., ["storm", "known UPS delays"])
    """
    logger.info("GET /packages - Fetching all packages with risk assessments")
    logger.info(f"Processing {len(MOCK_PACKAGES)} packages")
    
    enriched_packages = []
    
    for i, package in enumerate(MOCK_PACKAGES, 1):
        try:
            logger.info(f"Processing package {i}/{len(MOCK_PACKAGES)}: {package.package_id}")
            enriched_package = await get_enriched_package(package)
            enriched_packages.append(enriched_package)
            logger.info(f"Package {package.package_id} processed successfully (risk: {enriched_package.risk_score})")
        except Exception as e:
            logger.error(f"Error enriching package {package.package_id}: {str(e)}")
            # Add package with default risk if enrichment fails
            enriched_packages.append(EnrichedPackage(
                **package.dict(),
                risk_score=25,
                reasons=["assessment unavailable"]
            ))
    
    logger.info(f"GET /packages completed - returning {len(enriched_packages)} enriched packages")
    return enriched_packages


@app.get("/packages/{package_id}", response_model=EnrichedPackage, summary="Get single package risk assessment")
async def get_package(package_id: str) -> EnrichedPackage:
    """
    Returns risk score + reasons for a single shipment
    """
    logger.info(f"GET /packages/{package_id} - Fetching single package risk assessment")
    
    # Find package in mock data
    package = next((p for p in MOCK_PACKAGES if p.package_id == package_id), None)
    
    if not package:
        logger.warning(f"Package {package_id} not found in mock data")
        raise HTTPException(status_code=404, detail=f"Package {package_id} not found")
    
    logger.info(f"Found package {package_id}: {package.destination_city}, {package.carrier}")
    
    try:
        enriched_package = await get_enriched_package(package)
        logger.info(f"GET /packages/{package_id} completed - risk score: {enriched_package.risk_score}")
        return enriched_package
    except Exception as e:
        logger.error(f"Error assessing risk for package {package_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error calculating risk assessment")


@app.post("/send-alert", response_model=AlertResponse, summary="Send delay alert email")
async def send_alert(alert_request: AlertRequest) -> AlertResponse:
    """
    Sends an email warning for a high-risk shipment
    Accepts package_id and optional customer_email
    """
    logger.info(f"POST /send-alert - Sending alert for package {alert_request.package_id}")
    logger.info(f"Customer email: {alert_request.customer_email or 'Not provided (will use default)'}")
    
    # Find the package
    package = next((p for p in MOCK_PACKAGES if p.package_id == alert_request.package_id), None)
    
    if not package:
        logger.warning(f"Package {alert_request.package_id} not found for alert")
        raise HTTPException(status_code=404, detail=f"Package {alert_request.package_id} not found")
    
    try:
        # Get enriched package data
        logger.info(f"Getting enriched data for package {alert_request.package_id}")
        enriched_package = await get_enriched_package(package)
        
        # Send alert email
        logger.info(f"Sending delay alert email (risk score: {enriched_package.risk_score})")
        email_result = await email_service.send_delay_alert(
            enriched_package, 
            alert_request.customer_email
        )
        
        # Log the alert
        logger.info(f"Alert processing completed for package {alert_request.package_id}: {email_result}")
        
        return AlertResponse(
            success=email_result["success"],
            message=email_result["message"],
            email_sent=email_result["email_sent"]
        )
        
    except Exception as e:
        logger.error(f"Error sending alert for package {alert_request.package_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error sending alert")


@app.post("/action", response_model=ActionResponse, summary="Log customer action")
async def log_customer_action(action_request: ActionRequest) -> ActionResponse:
    """
    Accepts customer action (Accept Delay / Request Refund / Resend) and logs it
    """
    logger.info(f"POST /action - Logging customer action for package {action_request.package_id}")
    logger.info(f"Action: {action_request.action.value}, Customer: {action_request.customer_id or 'Anonymous'}")
    
    # Verify package exists
    package = next((p for p in MOCK_PACKAGES if p.package_id == action_request.package_id), None)
    
    if not package:
        logger.warning(f"Package {action_request.package_id} not found for action logging")
        raise HTTPException(status_code=404, detail=f"Package {action_request.package_id} not found")
    
    try:
        # Create action record
        action_record = {
            "timestamp": datetime.now().isoformat(),
            "package_id": action_request.package_id,
            "action": action_request.action.value,
            "customer_id": action_request.customer_id,
            "notes": action_request.notes
        }
        
        # Store action (in production, save to database)
        customer_actions.append(action_record)
        logger.info(f"Action stored in memory (total actions: {len(customer_actions)})")
        
        # Log the action
        logger.info(f"Customer action logged successfully: {action_record}")
        
        return ActionResponse(
            success=True,
            message=f"Action '{action_request.action.value}' logged successfully for package {action_request.package_id}",
            action_logged=True
        )
        
    except Exception as e:
        logger.error(f"Error logging action for package {action_request.package_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error logging customer action")


@app.get("/health", summary="Health check endpoint")
async def health_check():
    """Health check endpoint for service monitoring"""
    try:
        # Test basic functionality
        test_package = MOCK_PACKAGES[0]
        await get_enriched_package(test_package)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0",
            "services": {
                "risk_engine": "operational",
                "weather_service": "operational",
                "email_service": "operational" if email_service else "unavailable"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")


@app.get("/actions", summary="Get logged customer actions (debug endpoint)")
async def get_customer_actions():
    """Debug endpoint to view logged customer actions"""
    return {
        "total_actions": len(customer_actions),
        "actions": customer_actions[-10:]  # Return last 10 actions
    }


@app.get("/admin/performance-stats", summary="Get performance statistics from database")
async def get_performance_stats():
    """Get comprehensive performance statistics for dashboard"""
    try:
        stats = await risk_db.get_performance_stats()
        return {
            "success": True,
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error fetching performance stats: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching performance statistics")


@app.post("/admin/record-delivery", summary="Record actual delivery outcome for learning")
async def record_delivery_outcome(
    package_id: str,
    carrier: str,
    origin_zip: str = "00000",
    destination_zip: str = None,
    scheduled_date: str = None,
    actual_date: str = None,
    delay_reasons: Optional[List[str]] = None
):
    """Record actual delivery outcome to improve risk predictions"""
    try:
        # Find package details if not provided
        if not destination_zip or not scheduled_date:
            package = next((p for p in MOCK_PACKAGES if p.package_id == package_id), None)
            if package:
                destination_zip = destination_zip or package.destination_zip
                scheduled_date = scheduled_date or package.expected_delivery_date
            else:
                raise HTTPException(status_code=404, detail=f"Package {package_id} not found")
        
        if not actual_date:
            actual_date = datetime.now().strftime("%Y-%m-%d")
        
        await risk_engine.record_delivery_outcome(
            package_id, carrier, origin_zip, destination_zip,
            scheduled_date, actual_date, delay_reasons or []
        )
        
        logger.info(f"Recorded delivery outcome for package {package_id}")
        
        return {
            "success": True,
            "message": f"Delivery outcome recorded for package {package_id}",
            "recorded_data": {
                "package_id": package_id,
                "carrier": carrier,
                "destination_zip": destination_zip,
                "scheduled_date": scheduled_date,
                "actual_date": actual_date,
                "delay_reasons": delay_reasons
            }
        }
        
    except Exception as e:
        logger.error(f"Error recording delivery outcome: {str(e)}")
        raise HTTPException(status_code=500, detail="Error recording delivery outcome")


@app.get("/admin/risk-factors/{zip_code}", summary="Get risk factors for specific zip code")
async def get_zip_risk_factors(zip_code: str):
    """Get detailed risk analysis for a specific zip code"""
    try:
        geographic_risk = await risk_db.get_geographic_risk(zip_code)
        
        # Get carrier-specific performance for this zip
        carrier_performance = {}
        for carrier in ["UPS", "FedEx", "USPS", "DHL"]:
            performance_risk = await risk_db.get_delivery_performance_risk(carrier, zip_code)
            carrier_performance[carrier] = performance_risk
        
        return {
            "zip_code": zip_code,
            "geographic_risk": geographic_risk,
            "carrier_performance": carrier_performance,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing zip {zip_code}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing zip code")


@app.get("/admin/carrier-analysis/{carrier}", summary="Get detailed carrier performance analysis")
async def get_carrier_analysis(carrier: str):
    """Get comprehensive analysis of carrier performance"""
    try:
        carrier_risk = await risk_db.get_carrier_risk(carrier)
        
        # Get performance across different zip codes
        zip_performance = {}
        for zip_code in ["98101", "10001", "90210", "33101", "60601"]:
            performance_risk = await risk_db.get_delivery_performance_risk(carrier, zip_code)
            zip_performance[zip_code] = performance_risk
        
        return {
            "carrier": carrier,
            "overall_risk": carrier_risk,
            "zip_code_performance": zip_performance,
            "analysis_timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error analyzing carrier {carrier}: {str(e)}")
        raise HTTPException(status_code=500, detail="Error analyzing carrier")


@app.post("/admin/initialize-database", summary="Manually initialize database")
async def initialize_database():
    """Manually initialize the database if startup failed"""
    try:
        logger.info("Manual database initialization requested")
        await risk_db.initialize()
        logger.info("Manual database initialization completed")
        return {
            "success": True,
            "message": "Database initialized successfully"
        }
    except Exception as e:
        logger.error(f"Manual database initialization failed: {e}")
        return {
            "success": False,
            "error": str(e)
        }


@app.get("/admin/database-status", summary="Get database health and statistics")
async def get_database_status():
    """Get database health check and basic statistics"""
    try:
        import aiosqlite
        import os
        
        db_exists = os.path.exists(risk_db.db_path)
        db_size = os.path.getsize(risk_db.db_path) if db_exists else 0
        
        if db_exists:
            async with aiosqlite.connect(risk_db.db_path) as db:
                # Get table counts
                tables = {}
                table_names = ["carrier_performance", "geographic_risk", "delivery_performance", 
                             "temporal_risk", "delivery_outcomes"]
                
                for table in table_names:
                    cursor = await db.execute(f"SELECT COUNT(*) FROM {table}")
                    count = await cursor.fetchone()
                    tables[table] = count[0] if count else 0
        else:
            tables = {}
        
        return {
            "database_exists": db_exists,
            "database_path": risk_db.db_path,
            "database_size_bytes": db_size,
            "table_counts": tables,
            "status": "healthy" if db_exists else "not_initialized"
        }
        
    except Exception as e:
        logger.error(f"Error checking database status: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )