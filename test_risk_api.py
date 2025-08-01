#!/usr/bin/env python3
"""
Test script for the enhanced risk assessment API
"""
import asyncio
import json
from main import get_enhanced_risk_assessment
from mock_data import MOCK_PACKAGES


async def test_enhanced_risk_api():
    """Test the enhanced risk assessment API endpoint"""
    print("Testing Enhanced Risk Assessment API")
    print("=" * 50)
    
    # Test with first few packages
    for i, package in enumerate(MOCK_PACKAGES[:3]):
        print(f"\n[TEST {i+1}] Package: {package.package_id}")
        print(f"  Destination: {package.destination_city}, {package.destination_zip}")
        print(f"  Carrier: {package.carrier}")
        print(f"  Expected: {package.expected_delivery_date}")
        
        try:
            # Call the API endpoint function
            result = await get_enhanced_risk_assessment(package.package_id)
            
            print(f"  Result:")
            print(f"    Score: {result.score}/100")
            print(f"    Confidence: {result.confidenceLevel}%")
            print(f"    Predicted Delay: {result.predictedDelayDays} days")
            print(f"    Original Date: {result.originalDeliveryDate}")
            print(f"    Revised Date: {result.revisedDeliveryDate}")
            print(f"    Factors:")
            
            for factor_name, factor in result.factors.items():
                print(f"      {factor_name}: {factor.score} ({factor.level}) - {factor.status}")
            
            print("  STATUS: SUCCESS")
            
        except Exception as e:
            print(f"  STATUS: ERROR - {str(e)}")
    
    print("\n" + "=" * 50)
    print("Testing cache functionality...")
    
    # Test cache hit
    package = MOCK_PACKAGES[0]
    print(f"Requesting same package again: {package.package_id}")
    try:
        result = await get_enhanced_risk_assessment(package.package_id)
        print(f"Cache test successful - Score: {result.score}")
    except Exception as e:
        print(f"Cache test failed: {str(e)}")
    
    print("\nAPI testing complete!")


if __name__ == "__main__":
    asyncio.run(test_enhanced_risk_api())