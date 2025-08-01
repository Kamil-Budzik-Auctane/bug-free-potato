"""
Simple API test script
"""
import asyncio
import aiosqlite
from database import risk_db

async def test_everything():
    print("Testing API components...")
    
    # 1. Test database initialization
    try:
        print("1. Testing database initialization...")
        await risk_db.initialize()
        print("   OK Database initialized successfully")
    except Exception as e:
        print(f"   ERROR Database failed: {e}")
        return
    
    # 2. Test database queries
    try:
        print("2. Testing database queries...")
        ups_risk = await risk_db.get_carrier_risk("UPS")
        print(f"   OK UPS risk score: {ups_risk}")
        
        geo_risk = await risk_db.get_geographic_risk("98101")
        print(f"   OK Seattle geographic risk: {geo_risk}")
        
        perf_risk = await risk_db.get_delivery_performance_risk("UPS", "98101")
        print(f"   OK UPS->Seattle performance risk: {perf_risk}")
        
    except Exception as e:
        print(f"   ERROR Database queries failed: {e}")
        return
    
    print("\nSUCCESS All database tests passed!")
    print("Server should now work properly")
    print("\nTo test the API:")
    print("1. Start server: python run_server.py")
    print("2. Test: http://localhost:8000/")
    print("3. Initialize DB: POST http://localhost:8000/admin/initialize-database")
    print("4. Test packages: http://localhost:8000/packages")

if __name__ == "__main__":
    asyncio.run(test_everything())