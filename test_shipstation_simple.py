#!/usr/bin/env python3
"""
Simple test for ShipStation integration (Windows compatible)
"""
import asyncio
import json
from main import enrich_shipments, get_order_risk_assessment
from models import ShipStationResponse


async def test_integration():
    print("Testing ShipStation Integration")
    print("=" * 50)
    
    # Sample data matching your format
    sample_data = {
        "page": 1,
        "pageSize": 250,
        "totalCount": 3,
        "pageData": [
            {
                "salesOrderId": "test-order-1",
                "fulfillmentPlanId": "1147831",
                "orderNumber": "100083598",
                "recipientName": "Michel Cheve",
                "orderDateTime": "2025-08-01T21:48:29",
                "shipByDateTime": "2025-08-02T16:02:37",
                "countryCode": "FR",
                "state": "FR",
                "derivedStatus": "AWP",
                "store": {
                    "storeGuid": "test-store-guid",
                    "marketplaceCode": None
                },
                "serviceId": "13",
                "serviceName": None,
                "shipFromId": "301",
                "shipFromName": "My Default Location",
                "weight": {
                    "unit": "Ounces",
                    "value": 96.0
                },
                "requestedService": "Select Shipping Method - Cheapest- First Class Mail"
            },
            {
                "salesOrderId": "test-order-2",
                "fulfillmentPlanId": "1147832",
                "orderNumber": "100083599",
                "recipientName": "John Smith",
                "orderDateTime": "2025-08-01T10:30:00",
                "shipByDateTime": "2025-08-02T16:00:00",
                "countryCode": "US",
                "state": "WA",
                "derivedStatus": "AWP",
                "store": {
                    "storeGuid": "test-store-guid",
                    "marketplaceCode": None
                },
                "serviceId": "14",
                "serviceName": "UPS Ground",
                "shipFromId": "301",
                "shipFromName": "My Default Location",  
                "weight": {
                    "unit": "Ounces",
                    "value": 32.0
                },
                "requestedService": "UPS Ground"
            }
        ]
    }
    
    try:
        # Test 1: Parse and enrich shipments
        shipstation_request = ShipStationResponse(**sample_data)
        print(f"SUCCESS: Parsed {len(shipstation_request.pageData)} shipments")
        
        # Test enrichment
        enriched = await enrich_shipments(shipstation_request)
        print(f"SUCCESS: Enriched {len(enriched.pageData)} shipments")
        
        # Show results
        for shipment in enriched.pageData:
            print(f"  {shipment.fulfillmentPlanId}: Risk Score = {shipment.riskScore}")
            print(f"    {shipment.recipientName} ({shipment.state})")
            print(f"    Service: {shipment.requestedService}")
            print()
        
        # Test 2: Detailed risk assessment  
        first_id = enriched.pageData[0].fulfillmentPlanId
        print(f"Testing detailed assessment for {first_id}...")
        
        detailed = await get_order_risk_assessment(first_id)
        print(f"SUCCESS: Detailed risk assessment")
        print(f"  Score: {detailed.score}/100")
        print(f"  Confidence: {detailed.confidenceLevel}%")
        print(f"  Delay Days: {detailed.predictedDelayDays}")
        
        # Test 3: JSON output
        json_output = enriched.json()
        parsed = json.loads(json_output)
        first_risk = parsed['pageData'][0]['riskScore']
        print(f"SUCCESS: JSON serialization works, first risk score: {first_risk}")
        
        print("\n" + "=" * 50)
        print("INTEGRATION READY FOR FRONTEND!")
        print("Your endpoints are working correctly.")
        
    except Exception as e:
        print(f"ERROR: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_integration())