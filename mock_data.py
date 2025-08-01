from models import Package, CarrierType
from typing import List
from datetime import datetime, timedelta
import random


def generate_mock_packages(count: int = 75) -> List[Package]:
    """Generate realistic mock shipment data for demo"""
    
    # Expanded realistic US locations with zip codes
    locations = [
        ("98101", "Seattle"), ("98102", "Seattle"), ("98103", "Seattle"),
        ("10001", "New York"), ("10002", "New York"), ("10003", "New York"), 
        ("10004", "New York"), ("10005", "New York"),
        ("90210", "Beverly Hills"), ("90211", "Beverly Hills"), ("90212", "Beverly Hills"),
        ("90001", "Los Angeles"), ("90002", "Los Angeles"), ("90003", "Los Angeles"),
        ("33101", "Miami"), ("33102", "Miami"), ("33109", "Miami Beach"),
        ("33139", "Miami Beach"), ("33141", "Miami"),
        ("60601", "Chicago"), ("60602", "Chicago"), ("60603", "Chicago"),
        ("60604", "Chicago"), ("60605", "Chicago"),
        ("75201", "Dallas"), ("75202", "Dallas"), ("75203", "Dallas"),
        ("30301", "Atlanta"), ("30302", "Atlanta"), ("30303", "Atlanta"),
        ("02101", "Boston"), ("02102", "Boston"), ("02103", "Boston"),
        ("19101", "Philadelphia"), ("19102", "Philadelphia"), ("19103", "Philadelphia"),
        ("85001", "Phoenix"), ("85002", "Phoenix"), ("85003", "Phoenix"),
        ("78701", "Austin"), ("78702", "Austin"), ("78703", "Austin"),
        ("94101", "San Francisco"), ("94102", "San Francisco"), ("94103", "San Francisco"),
        ("80201", "Denver"), ("80202", "Denver"), ("80203", "Denver"),
        ("37201", "Nashville"), ("37202", "Nashville"), ("37203", "Nashville"),
        ("97201", "Portland"), ("97202", "Portland"), ("97203", "Portland"),
        ("89101", "Las Vegas"), ("89102", "Las Vegas"), ("89103", "Las Vegas"),
        ("20001", "Washington DC"), ("20002", "Washington DC"), ("20003", "Washington DC"),
        ("55401", "Minneapolis"), ("55402", "Minneapolis"), ("55403", "Minneapolis"),
        ("63101", "St Louis"), ("63102", "St Louis"), ("63103", "St Louis"),
        ("48201", "Detroit"), ("48202", "Detroit"), ("48203", "Detroit"),
        ("32801", "Orlando"), ("32802", "Orlando"), ("32803", "Orlando"),
        ("28201", "Charlotte"), ("28202", "Charlotte"), ("28203", "Charlotte"),
        ("43201", "Columbus"), ("43202", "Columbus"), ("43203", "Columbus"),
        ("46201", "Indianapolis"), ("46202", "Indianapolis"), ("46203", "Indianapolis"),
    ]
    
    # All carriers with realistic distribution
    carriers = [CarrierType.UPS, CarrierType.FEDEX, CarrierType.USPS, CarrierType.DHL]
    carrier_weights = [0.35, 0.30, 0.25, 0.10]  # UPS and FedEx are more common
    
    packages = []
    today = datetime.now().date()
    
    for i in range(count):
        # Generate package ID with realistic format
        package_id = f"PKG{str(i+1).zfill(4)}"
        
        # Random location
        zip_code, city = random.choice(locations)
        
        # Weighted carrier selection
        carrier = random.choices(carriers, weights=carrier_weights)[0]
        
        # Delivery date: mostly near future (1-10 days), some further out
        if random.random() < 0.7:  # 70% within 10 days
            days_ahead = random.randint(1, 10)
        else:  # 30% up to 30 days out
            days_ahead = random.randint(11, 30)
            
        delivery_date = (today + timedelta(days=days_ahead)).strftime("%Y-%m-%d")
        
        package = Package(
            package_id=package_id,
            destination_zip=zip_code,
            destination_city=city,
            carrier=carrier,
            expected_delivery_date=delivery_date
        )
        
        packages.append(package)
    
    # Sort by delivery date for better demo presentation
    packages.sort(key=lambda p: p.expected_delivery_date)
    
    return packages


def generate_demo_packages() -> List[Package]:
    """Generate a smaller set of high-interest packages for focused demo"""
    
    # High-risk scenarios for demo
    today = datetime.now().date()
    tomorrow = (today + timedelta(days=1)).strftime("%Y-%m-%d")
    day_after = (today + timedelta(days=2)).strftime("%Y-%m-%d")
    next_week = (today + timedelta(days=7)).strftime("%Y-%m-%d")
    
    demo_packages = [
        # High risk - Miami in hurricane season, tight timeline
        Package(
            package_id="DEMO001",
            destination_zip="33139",
            destination_city="Miami Beach",
            carrier=CarrierType.USPS,
            expected_delivery_date=tomorrow
        ),
        # Medium risk - Seattle rain, decent carrier
        Package(
            package_id="DEMO002",
            destination_zip="98101",
            destination_city="Seattle",
            carrier=CarrierType.UPS,
            expected_delivery_date=day_after
        ),
        # Low risk - Good weather, reliable route
        Package(
            package_id="DEMO003",
            destination_zip="90210",
            destination_city="Beverly Hills",
            carrier=CarrierType.FEDEX,
            expected_delivery_date=next_week
        ),
        # High risk - Holiday season, USPS, tight timeline
        Package(
            package_id="DEMO004",
            destination_zip="10001",
            destination_city="New York",
            carrier=CarrierType.USPS,
            expected_delivery_date=tomorrow
        ),
        # Medium risk - DHL to complex location
        Package(
            package_id="DEMO005",
            destination_zip="60601",
            destination_city="Chicago",
            carrier=CarrierType.DHL,
            expected_delivery_date=day_after
        ),
    ]
    
    return demo_packages


# Generate full dataset for production demo
MOCK_PACKAGES = generate_mock_packages(75)

# Also provide focused demo set
DEMO_PACKAGES = generate_demo_packages()