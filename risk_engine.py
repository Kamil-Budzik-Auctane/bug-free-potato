from models import Package, RiskAssessment, CarrierType, EnhancedRiskAssessment, RiskFactor
from weather_service import WeatherService
from database import risk_db
from datetime import datetime, date, timedelta
from typing import List, Dict, Tuple
import calendar
import logging
import math

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
    
    def _get_risk_level(self, score: int) -> str:
        """Get risk level for individual factors"""
        if score >= 80:
            return "high"
        elif score >= 50:
            return "medium"
        else:
            return "low"
    
    def _estimate_route_distance(self, destination_zip: str) -> int:
        """Estimate route distance and complexity based on zip code"""
        # Simple distance estimation based on zip code patterns
        # In production, you'd use actual routing APIs
        zip_num = int(destination_zip[:5]) if destination_zip.isdigit() and len(destination_zip) >= 5 else 50000
        
        # West Coast (90000-99999) - typically longer routes from east coast distribution centers
        if 90000 <= zip_num <= 99999:
            return 65  # Higher risk due to cross-country shipping
        
        # East Coast major metros (00000-19999) - good infrastructure
        elif zip_num <= 19999:
            return 35  # Lower risk, established routes
        
        # Midwest (60000-69999) - central, moderate complexity
        elif 60000 <= zip_num <= 69999:
            return 45
        
        # South (30000-39999) - mixed urban/rural
        elif 30000 <= zip_num <= 39999:
            return 55
        
        # Mountain/Plains states - sparse, complex routes
        else:
            return 70
    
    def _calculate_confidence_level(self, package: Package, has_weather_data: bool, 
                                  has_performance_data: bool) -> int:
        """Calculate AI confidence level based on available data quality"""
        confidence = 70  # Base confidence
        
        # Boost confidence based on data availability
        if has_weather_data:
            confidence += 10
        if has_performance_data:
            confidence += 15
        
        # Popular carriers have more data = higher confidence
        if package.carrier in [CarrierType.UPS, CarrierType.FEDEX]:
            confidence += 5
        
        return min(confidence, 95)  # Cap at 95% - never 100% certain
    
    def _predict_delay_days(self, risk_score: int) -> int:
        """Predict delay days based on risk score"""
        if risk_score >= 80:
            return 2  # High risk = 2 days delay
        elif risk_score >= 50:
            return 1  # Medium risk = 1 day delay
        else:
            return 0  # Low risk = no delay
    
    def _calculate_revised_delivery_date(self, original_date: str, delay_days: int) -> str:
        """Calculate revised delivery date"""
        try:
            original = datetime.strptime(original_date, "%Y-%m-%d")
            revised = original + timedelta(days=delay_days)
            return revised.strftime("%Y-%m-%dT00:00:00Z")
        except ValueError:
            # Fallback if date parsing fails
            return datetime.now().strftime("%Y-%m-%dT00:00:00Z")
    
    async def calculate_enhanced_risk_assessment(self, package: Package) -> EnhancedRiskAssessment:
        """Calculate enhanced risk assessment for frontend API"""
        logger.info(f"Calculating enhanced risk assessment for package {package.package_id}")
        
        # Get individual factor scores
        carrier_risk = await self.db.get_carrier_risk(package.carrier.value)
        geographic_risk = await self.db.get_geographic_risk(package.destination_zip)
        performance_risk = await self.db.get_delivery_performance_risk(package.carrier.value, package.destination_zip)
        route_risk = self._estimate_route_distance(package.destination_zip)
        
        # Get weather risk
        weather_risk = 0
        weather_reasons = []
        has_weather_data = False
        try:
            weather_data = await self.weather_service.get_weather_risk(package.destination_city)
            weather_risk = weather_data.get("risk_score", 0)
            weather_reasons = weather_data.get("reasons", [])
            has_weather_data = True
        except Exception as e:
            weather_risk = 10  # Default weather risk
            weather_reasons = ["weather data unavailable"]
            logger.warning(f"Weather service failed: {str(e)}")
        
        # Calculate weighted overall score (matching frontend requirements)
        # Carrier Performance: 30%, Route Distance: 25%, Weather: 25%, Current Delays: 20%
        overall_score = int(
            (carrier_risk * 0.30) + 
            (route_risk * 0.25) + 
            (weather_risk * 0.25) + 
            (performance_risk * 0.20)
        )
        overall_score = min(overall_score, 100)
        
        # Build factors breakdown
        factors = {
            "carrierPerformance": RiskFactor(
                score=carrier_risk,
                weight=30,
                status=f"Carrier {package.carrier} reliability based on historical data" if carrier_risk < 50 else f"Poor performance history with {package.carrier}",
                level=self._get_risk_level(carrier_risk)
            ),
            "routeDistance": RiskFactor(
                score=route_risk,
                weight=25,
                status="Optimized delivery route" if route_risk < 50 else "Long distance route with multiple stops",
                level=self._get_risk_level(route_risk)
            ),
            "weather": RiskFactor(
                score=weather_risk,
                weight=25,
                status=weather_reasons[0] if weather_reasons else "Clear weather conditions",
                level=self._get_risk_level(weather_risk)
            ),
            "currentDelays": RiskFactor(
                score=performance_risk,
                weight=20,
                status="No current delays detected" if performance_risk < 50 else "Carrier experiencing network-wide delays",
                level=self._get_risk_level(performance_risk)
            )
        }
        
        # Calculate confidence and delay prediction
        confidence = self._calculate_confidence_level(package, has_weather_data, performance_risk > 0)
        delay_days = self._predict_delay_days(overall_score)
        
        # Format dates
        original_date = f"{package.expected_delivery_date}T00:00:00Z"
        revised_date = self._calculate_revised_delivery_date(package.expected_delivery_date, delay_days)
        
        logger.info(f"Enhanced risk assessment complete: score={overall_score}, confidence={confidence}, delay={delay_days} days")
        
        return EnhancedRiskAssessment(
            score=overall_score,
            confidenceLevel=confidence,
            predictedDelayDays=delay_days,
            factors=factors,
            originalDeliveryDate=original_date,
            revisedDeliveryDate=revised_date
        )
    
    def _map_shipstation_to_package(self, shipment: dict) -> Package:
        """Convert ShipStation shipment to our internal Package format"""
        # Extract basic info
        package_id = shipment.get('fulfillmentPlanId', shipment.get('orderNumber', 'UNKNOWN'))
        
        # Map destination - use state code as zip approximation
        # In production, you'd want proper address resolution
        state_to_zip_mapping = {
            'CA': '90210',  # California -> Beverly Hills
            'WA': '98101',  # Washington -> Seattle  
            'NY': '10001',  # New York -> Manhattan
            'FL': '33101',  # Florida -> Miami
            'IL': '60601',  # Illinois -> Chicago
            'TX': '75201',  # Texas -> Dallas
            'FR': '75001',  # France -> Paris (mock)
            'UK': '10001',  # UK -> treat as NY for demo
            'DE': '10001',  # Germany -> treat as NY for demo
        }
        
        state = shipment.get('state', 'CA')
        destination_zip = state_to_zip_mapping.get(state, '90210')  # Default to CA
        
        # Map destination city from state
        state_to_city_mapping = {
            'CA': 'Los Angeles',
            'WA': 'Seattle',
            'NY': 'New York', 
            'FL': 'Miami',
            'IL': 'Chicago',
            'TX': 'Dallas',
            'FR': 'Paris',
            'UK': 'London',
            'DE': 'Berlin'
        }
        destination_city = state_to_city_mapping.get(state, 'Los Angeles')
        
        # Map carrier from service info
        requested_service = shipment.get('requestedService', '').lower()
        service_name = shipment.get('serviceName', '').lower() if shipment.get('serviceName') else ''
        
        # Determine carrier from service description
        if 'ups' in requested_service or 'ups' in service_name:
            carrier = CarrierType.UPS
        elif 'fedex' in requested_service or 'fedex' in service_name:
            carrier = CarrierType.FEDEX
        elif 'usps' in requested_service or 'first class' in requested_service or 'priority' in requested_service:
            carrier = CarrierType.USPS
        elif 'dhl' in requested_service or 'dhl' in service_name:
            carrier = CarrierType.DHL
        else:
            # Default based on service characteristics
            if 'cheapest' in requested_service or 'first class' in requested_service:
                carrier = CarrierType.USPS  # Cheapest usually USPS
            else:
                carrier = CarrierType.UPS   # Default to UPS
        
        # Use shipByDateTime as delivery date, or estimate from order date
        ship_by = shipment.get('shipByDateTime', shipment.get('orderDateTime', ''))
        if ship_by:
            try:
                # Parse the ship by date and add 2-3 days for delivery
                from datetime import datetime, timedelta
                ship_date = datetime.fromisoformat(ship_by.replace('Z', '+00:00'))
                estimated_delivery = ship_date + timedelta(days=2)  # Add 2 days for delivery
                expected_delivery_date = estimated_delivery.strftime('%Y-%m-%d')
            except:
                # Fallback to a future date
                from datetime import datetime, timedelta
                expected_delivery_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        else:
            from datetime import datetime, timedelta
            expected_delivery_date = (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d')
        
        return Package(
            package_id=package_id,
            destination_zip=destination_zip,
            destination_city=destination_city,
            carrier=carrier,
            expected_delivery_date=expected_delivery_date
        )
    
    async def calculate_shipstation_risk_score(self, shipment: dict) -> int:
        """Calculate just the risk score for ShipStation shipment enrichment"""
        try:
            # Convert to our internal format
            package = self._map_shipstation_to_package(shipment)
            
            # Get basic risk assessment
            risk_assessment = await self.calculate_risk_score(package)
            
            return risk_assessment.risk_score
        except Exception as e:
            logger.warning(f"Error calculating risk for shipment {shipment.get('fulfillmentPlanId', 'UNKNOWN')}: {str(e)}")
            # Return default medium risk if calculation fails
            return 50