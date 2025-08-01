#!/usr/bin/env python3
"""
Test script for ShipStation integration endpoints
"""
import asyncio
import json
from main import enrich_shipments, get_order_risk_assessment
from models import ShipStationResponse, ShipStationShipment, ShipStationStore, ShipStationWeight


async def test_shipstation_integration():
    """Test the ShipStation integration endpoints"""
    print("Testing ShipStation Integration")
    print("=" * 50)
    
    # Create sample ShipStation data based on your provided format
    sample_data = {
        "page": 1,
        "pageSize": 250,
        "totalCount": 3,
        "pageData": [
            {
                "salesOrderId": "114bee91-3d21-58f4-8f5e-7d97b0405bc2",
                "fulfillmentPlanId": "1147831",
                "orderNumber": "100083598",
                "recipientName": "Michel Cheve",
                "orderDateTime": "2018-04-25T21:48:29",
                "shipByDateTime": "2018-04-26T16:02:37.46",
                "countryCode": "FR",
                "state": "91",
                "derivedStatus": "AWP",
                "store": {
                    "storeGuid": "0b5755f1-b33d-48b9-bba7-04d5306bbd10",
                    "marketplaceCode": None
                },
                "serviceId": "13",
                "serviceName": None,
                "shipFromId": "301",
                "shipFromName": "My Default Location",
                "weight": {
                    "unit": "Ounces",
                    "value": 96
                },
                "requestedService": "Select Shipping Method - Cheapest- First Class Mail"
            },
            {
                "salesOrderId": "224bee91-3d21-58f4-8f5e-7d97b0405bc2",
                "fulfillmentPlanId": "1147832",
                "orderNumber": "100083599",
                "recipientName": "John Smith",
                "orderDateTime": "2025-08-01T10:30:00",
                "shipByDateTime": "2025-08-02T16:00:00",
                "countryCode": "US",
                "state": "WA",
                "derivedStatus": "AWP",
                "store": {
                    "storeGuid": "0b5755f1-b33d-48b9-bba7-04d5306bbd10",
                    "marketplaceCode": None
                },
                "serviceId": "14",
                "serviceName": "UPS Ground",
                "shipFromId": "301",
                "shipFromName": "My Default Location",
                "weight": {
                    "unit": "Ounces",
                    "value": 32
                },
                "requestedService": "UPS Ground"
            },
            {
                "salesOrderId": "334bee91-3d21-58f4-8f5e-7d97b0405bc2",
                "fulfillmentPlanId": "1147833",
                "orderNumber": "100083600",
                "recipientName": "Sarah Johnson",
                "orderDateTime": "2025-08-01T14:15:00",
                "shipByDateTime": "2025-08-03T10:00:00",
                "countryCode": "US",
                "state": "FL",
                "derivedStatus": "AWP",
                "store": {
                    "storeGuid": "0b5755f1-b33d-48b9-bba7-04d5306bbd10",
                    "marketplaceCode": None
                },
                "serviceId": "15",
                "serviceName": "FedEx Express",
                "shipFromId": "301",
                "shipFromName": "My Default Location",
                "weight": {
                    "unit": "Ounces",
                    "value": 8
                },
                "requestedService": "FedEx 2Day"
            }
        ]
    }
    
    # Convert to Pydantic model
    try:
        shipstation_request = ShipStationResponse(**sample_data)
        print(f"✓ Successfully parsed ShipStation data with {len(shipstation_request.pageData)} shipments")
    except Exception as e:
        print(f"✗ Failed to parse ShipStation data: {str(e)}")
        return
    
    print("\n[TEST 1] Shipment Enrichment")
    print("-" * 30)
    
    try:
        # Test the enrichment endpoint
        enriched_response = await enrich_shipments(shipstation_request)
        
        print(f"✓ Enrichment successful!")
        print(f"  Total shipments: {enriched_response.totalCount}")
        print(f"  Page data count: {len(enriched_response.pageData)}")
        
        # Show enriched results
        for shipment in enriched_response.pageData:
            print(f"  {shipment.fulfillmentPlanId}: {shipment.recipientName}")
            print(f"    State: {shipment.state} -> Risk Score: {shipment.riskScore}")
            print(f"    Service: {shipment.requestedService}")
            print()
            
    except Exception as e:
        print(f"✗ Enrichment failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n[TEST 2] Detailed Risk Assessment")
    print("-" * 30)
    
    # Test detailed risk assessment for each fulfillment plan
    for shipment in enriched_response.pageData:
        fulfillment_id = shipment.fulfillmentPlanId
        print(f"Testing detailed assessment for {fulfillment_id}...")
        
        try:
            detailed_risk = await get_order_risk_assessment(fulfillment_id)
            
            print(f"✓ Detailed risk assessment for {fulfillment_id}:")
            print(f"  Score: {detailed_risk.score}/100")
            print(f"  Confidence: {detailed_risk.confidenceLevel}%")
            print(f"  Predicted Delay: {detailed_risk.predictedDelayDays} days")
            print(f"  Factors:")
            
            for factor_name, factor in detailed_risk.factors.items():
                print(f"    {factor_name}: {factor.score} ({factor.level}) - {factor.status}")
            
            print()
            
        except Exception as e:
            print(f"✗ Detailed assessment failed for {fulfillment_id}: {str(e)}")
    
    print("\n[TEST 3] JSON Response Validation")
    print("-" * 30)
    
    # Test JSON serialization (important for API responses)
    try:
        json_response = enriched_response.json()
        parsed_back = json.loads(json_response)
        
        print("✓ JSON serialization works correctly")
        print(f"  First shipment risk score: {parsed_back['pageData'][0]['riskScore']}")
        
        # Validate structure matches expected frontend format
        first_shipment = parsed_back['pageData'][0]
        required_fields = ['fulfillmentPlanId', 'riskScore', 'recipientName', 'state']
        
        missing_fields = [field for field in required_fields if field not in first_shipment]
        if missing_fields:
            print(f"✗ Missing required fields: {missing_fields}")
        else:
            print("✓ All required fields present in response")
            
    except Exception as e:
        print(f"✗ JSON serialization failed: {str(e)}")
    
    print("\n" + "=" * 50)
    print("ShipStation Integration Testing Complete!")
    print("Ready for frontend integration! 🚀")


if __name__ == "__main__":
    asyncio.run(test_shipstation_integration())