import httpx
import os
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import logging

logger = logging.getLogger(__name__)


class WeatherService:
    def __init__(self):
        self.api_key = os.getenv("OPENWEATHER_API_KEY", "mock_api_key")
        self.base_url = "http://api.openweathermap.org/data/2.5/weather"
        # In-memory cache for demo
        self._cache: Dict[str, Dict[str, Any]] = {}
        # Hardcoded cities for demo
        self.supported_cities = {"Seattle", "New York"}
        
        # Log initialization details
        if self.api_key == "mock_api_key":
            logger.info("WeatherService initialized in MOCK MODE (no API key provided)")
        else:
            logger.info(f"WeatherService initialized with API key: {self.api_key[:8]}...")
            logger.info(f"Supported cities for real API calls: {self.supported_cities}")
            logger.info(f"API endpoint: {self.base_url}")
        
    async def get_weather_risk(self, city: str) -> Dict[str, Any]:
        """Get weather-based risk factors for a city"""
        
        logger.info(f"Getting weather risk for city: {city}")
        
        # Use cache if available
        if city in self._cache:
            logger.info(f"Cache HIT for {city} - returning cached result")
            return self._cache[city]
        
        logger.info(f"Cache MISS for {city} - fetching new data")
        
        # Only call API for supported cities, mock others
        if city in self.supported_cities and self.api_key != "mock_api_key":
            logger.info(f"Making REAL API call for {city} (supported city with valid API key)")
            try:
                weather_data = await self._fetch_weather_data(city)
                risk_data = self._analyze_weather_risk(weather_data)
                logger.info(f"Real API call successful for {city}: risk_score={risk_data['risk_score']}, reasons={risk_data['reasons']}")
            except Exception as e:
                logger.warning(f"Real API call failed for {city}: {str(e)} - falling back to mock data")
                # Fallback to mock data if API fails
                risk_data = self._get_mock_weather_risk(city)
        else:
            if city not in self.supported_cities:
                logger.info(f"Using MOCK data for {city} (not in supported cities: {self.supported_cities})")
            else:
                logger.info(f"Using MOCK data for {city} (no valid API key)")
            risk_data = self._get_mock_weather_risk(city)
            
        # Cache result
        logger.info(f"Caching result for {city}")
        self._cache[city] = risk_data
        return risk_data
    
    async def _fetch_weather_data(self, city: str) -> Dict[str, Any]:
        """Fetch actual weather data from OpenWeatherMap API"""
        logger.debug(f"Calling OpenWeatherMap API for {city}")
        
        async with httpx.AsyncClient() as client:
            params = {
                "q": city,
                "appid": self.api_key,
                "units": "metric"
            }
            logger.debug(f"API request URL: {self.base_url}")
            logger.debug(f"API request params: {dict(params, appid='***HIDDEN***')}")
            
            response = await client.get(self.base_url, params=params)
            logger.debug(f"API response status: {response.status_code}")
            
            response.raise_for_status()
            weather_data = response.json()
            
            logger.info(f"Weather data received for {city}: {weather_data.get('weather', [{}])[0].get('main', 'unknown')} - {weather_data.get('weather', [{}])[0].get('description', 'no description')}")
            
            return weather_data
    
    def _analyze_weather_risk(self, weather_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze weather data to determine risk factors"""
        logger.info("Analyzing real weather data for risk factors")
        risk_score = 0
        reasons = []
        
        # Check weather conditions
        if "weather" in weather_data:
            main_weather = weather_data["weather"][0]["main"].lower()
            description = weather_data["weather"][0].get("description", "")
            logger.info(f"Weather condition: {main_weather} ({description})")
            
            if main_weather in ["thunderstorm", "snow"]:
                risk_score += 30
                reasons.append(f"severe weather: {main_weather}")
                logger.info(f"HIGH RISK: Severe weather detected (+30 points)")
            elif main_weather in ["rain", "drizzle"]:
                risk_score += 15
                reasons.append(f"wet weather: {main_weather}")
                logger.info(f"MEDIUM RISK: Wet weather detected (+15 points)")
            elif main_weather in ["fog", "mist"]:
                risk_score += 10
                reasons.append("low visibility conditions")
                logger.info(f"LOW RISK: Poor visibility detected (+10 points)")
            else:
                logger.info(f"Good weather conditions (no additional risk)")
        
        # Check wind speed
        if "wind" in weather_data:
            wind_speed = weather_data["wind"].get("speed", 0)
            logger.info(f"Wind speed: {wind_speed} m/s")
            if wind_speed > 10:
                risk_score += 10
                reasons.append("high winds")
                logger.info(f"HIGH WINDS: Additional risk (+10 points)")
        
        final_risk = min(risk_score, 50)  # Cap weather risk at 50
        logger.info(f"Weather risk analysis complete: {risk_score} points (capped at {final_risk}), reasons: {reasons}")
            
        return {
            "risk_score": final_risk,
            "reasons": reasons,
            "weather_data": weather_data
        }
    
    def _get_mock_weather_risk(self, city: str) -> Dict[str, Any]:
        """Generate mock weather risk for demo purposes"""
        logger.info(f"Generating mock weather data for {city}")
        
        mock_risks = {
            "Seattle": {
                "risk_score": 25,
                "reasons": ["rainy conditions", "low visibility"],
                "weather_data": {"main": "Rain", "description": "light rain"}
            },
            "New York": {
                "risk_score": 10,
                "reasons": ["partly cloudy"],
                "weather_data": {"main": "Clouds", "description": "scattered clouds"}
            },
            "Beverly Hills": {
                "risk_score": 5,
                "reasons": [],
                "weather_data": {"main": "Clear", "description": "clear sky"}
            },
            "Miami": {
                "risk_score": 20,
                "reasons": ["thunderstorm potential"],
                "weather_data": {"main": "Thunderstorm", "description": "possible storms"}
            },
            "Chicago": {
                "risk_score": 15,
                "reasons": ["windy conditions"],
                "weather_data": {"main": "Clear", "description": "clear but windy"}
            }
        }
        
        mock_data = mock_risks.get(city, {
            "risk_score": 5,
            "reasons": [],
            "weather_data": {"main": "Clear", "description": "clear sky"}
        })
        
        logger.info(f"Mock weather for {city}: {mock_data['weather_data']['main']} - risk_score={mock_data['risk_score']}, reasons={mock_data['reasons']}")
        
        return mock_data