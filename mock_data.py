from models import Package, CarrierType
from typing import List
from datetime import datetime, timedelta


def generate_mock_packages() -> List[Package]:
    """Generate mock shipment data for testing"""
    
    packages = [
        Package(
            package_id="PKG001",
            destination_zip="98101",
            destination_city="Seattle",
            carrier=CarrierType.UPS,
            expected_delivery_date="2025-08-03"
        ),
        Package(
            package_id="PKG002", 
            destination_zip="10001",
            destination_city="New York",
            carrier=CarrierType.FEDEX,
            expected_delivery_date="2025-08-02"
        ),
        Package(
            package_id="PKG003",
            destination_zip="90210",
            destination_city="Beverly Hills",
            carrier=CarrierType.USPS,
            expected_delivery_date="2025-08-05"
        ),
        Package(
            package_id="PKG004",
            destination_zip="33101",
            destination_city="Miami",
            carrier=CarrierType.DHL,
            expected_delivery_date="2025-08-01"
        ),
        Package(
            package_id="PKG005",
            destination_zip="60601",
            destination_city="Chicago",
            carrier=CarrierType.UPS,
            expected_delivery_date="2025-08-04"
        )
    ]
    
    return packages


MOCK_PACKAGES = generate_mock_packages()