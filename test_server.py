"""
Minimal test server to debug the hanging issue
"""
from fastapi import FastAPI
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Create minimal app
app = FastAPI(title="Test Server")

@app.get("/")
async def root():
    logger.info("Root endpoint called")
    return {"message": "Test server is working"}

@app.get("/test")
async def test():
    logger.info("Test endpoint called")
    return {"status": "ok", "message": "Simple test endpoint"}

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting minimal test server...")
    uvicorn.run(
        "test_server:app",
        host="0.0.0.0",
        port=8001,  # Use different port
        reload=True,
        log_level="info"
    )