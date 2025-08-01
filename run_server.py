#!/usr/bin/env python3
"""
Script to run the Shipment Risk Prediction Engine server
"""
import uvicorn
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting Shipment Risk Prediction Engine on {host}:{port}")
    print(f"API Documentation: http://{host}:{port}/docs")
    print(f"Interactive API: http://{host}:{port}/redoc")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        log_level="info"
    )