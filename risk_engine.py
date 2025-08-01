from models import Package, RiskAssessment, CarrierType
from weather_service import WeatherService
from database import risk_db
from datetime import datetime, date
from typing import List
import calendar
import logging

logger = logging.getLogger(__name__)


class RiskScoringEngine:
    def __init__(self):
        self.weather_service = WeatherService()
        self.db = risk_db
        logger.info("RiskScoringEngine initialized with smart database backend")
    
    async def calculate_risk_score(self, package: Package) -> RiskAssessment:
        """Calculate comprehensive risk score using smart database-driven analysis"""
        logger.info(f"Calculating smart risk score for package {package.package_id}")
        logger.info(f"Package details: {package.destination_city}, {package.destination_zip}, {package.carrier}, delivery: {package.expected_delivery_date}")
        
        total_risk = 0
        reasons = []
        
        # 1. Carrier-based risk (from historical performance data)
        carrier_risk = await self.db.get_carrier_risk(package.carrier.value)
        total_risk += carrier_risk
        logger.info(f"Database carrier risk ({package.carrier}): +{carrier_risk} points")
        if carrier_risk > 15:
            reasons.append(f"{package.carrier} has historical delivery challenges")
            logger.info(f"High carrier risk detected for {package.carrier}")
        
        # 2. Geographic risk (from database analysis)
        geographic_risk = await self.db.get_geographic_risk(package.destination_zip)
        total_risk += geographic_risk
        logger.info(f"Database geographic risk ({package.destination_zip}): +{geographic_risk} points")
        if geographic_risk > 15:
            reasons.append(f"destination {package.destination_zip} has delivery complexity")
            logger.info(f"High geographic risk for zip {package.destination_zip}")
        
        # 3. Carrier-Zip specific performance (historical combination data)
        performance_risk = await self.db.get_delivery_performance_risk(package.carrier.value, package.destination_zip)
        total_risk += performance_risk
        logger.info(f"Historical performance risk ({package.carrier} to {package.destination_zip}): +{performance_risk} points")
        if performance_risk > 10:
            reasons.append(f"{package.carrier} has specific issues delivering to {package.destination_zip}")
        
        # 4. Weather-based risk (real-time data)
        try:
            logger.info(f"Fetching weather risk for {package.destination_city}...")
            weather_risk_data = await self.weather_service.get_weather_risk(package.destination_city)
            weather_risk = weather_risk_data.get("risk_score", 0)
            weather_reasons = weather_risk_data.get("reasons", [])
            
            total_risk += weather_risk
            reasons.extend(weather_reasons)
            logger.info(f"Weather risk: +{weather_risk} points, reasons: {weather_reasons}")
        except Exception as e:
            # If weather service fails, add moderate risk
            total_risk += 10
            reasons.append("weather data unavailable")
            logger.error(f"Weather service failed: {str(e)} - adding default risk (+10 points)")
        
        # 5. Temporal/seasonal patterns (from database)
        temporal_risk, temporal_reasons = await self.db.get_temporal_risk(package.expected_delivery_date)
        total_risk += temporal_risk
        reasons.extend(temporal_reasons)
        logger.info(f"Database temporal risk: +{temporal_risk} points, reasons: {temporal_reasons}")
        
        # 6. Delivery date proximity (immediate timeline risk)
        date_risk = self._calculate_date_proximity_risk(package.expected_delivery_date)
        total_risk += date_risk
        logger.info(f"Delivery timeline risk: +{date_risk} points")
        if date_risk > 15:
            reasons.append("tight delivery timeline")
            logger.info(f"Tight delivery timeline detected")
        
        # Cap the risk score at 100
        final_risk_score = min(total_risk, 100)
        logger.info(f"SMART RISK CALCULATION for {package.package_id}:")
        logger.info(f"   Carrier: {carrier_risk} + Geographic: {geographic_risk} + Performance: {performance_risk}")
        logger.info(f"   Weather: {weather_risk_data.get('risk_score', 10) if 'weather_risk_data' in locals() else 10} + Temporal: {temporal_risk} + Timeline: {date_risk}")
        logger.info(f"   Total: {total_risk} -> Final (capped): {final_risk_score}")
        logger.info(f"   Risk reasons: {reasons}")
        
        return RiskAssessment(
            risk_score=final_risk_score,
            reasons=reasons if reasons else ["low risk delivery"]
        )
    
    async def record_delivery_outcome(self, package_id: str, carrier: str, 
                                     origin_zip: str, destination_zip: str,
                                     scheduled_date: str, actual_date: str,
                                     delay_reasons: List[str] = None):
        """Record actual delivery outcome for continuous learning"""
        await self.db.record_delivery_outcome(
            package_id, carrier, origin_zip, destination_zip,
            scheduled_date, actual_date, delay_reasons
        )
    
    def _calculate_date_proximity_risk(self, delivery_date_str: str) -> int:
        """Calculate risk based on how soon the delivery is expected"""
        try:
            delivery_date = datetime.strptime(delivery_date_str, "%Y-%m-%d").date()
            today = date.today()
            
            days_until_delivery = (delivery_date - today).days
            
            if days_until_delivery <= 0:
                return 25  # Same day or overdue
            elif days_until_delivery == 1:
                return 20  # Next day
            elif days_until_delivery <= 3:
                return 10  # Within 3 days
            else:
                return 0   # More than 3 days
                
        except ValueError:
            return 5  # Invalid date format
    
    def get_risk_level_description(self, risk_score: int) -> str:
        """Convert numeric risk score to human-readable description"""
        if risk_score >= 70:
            return "High Risk"
        elif risk_score >= 40:
            return "Medium Risk"
        else:
            return "Low Risk"