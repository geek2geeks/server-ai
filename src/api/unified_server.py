# Location: E:/justica/src/api/unified_server.py

import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from prometheus_client import start_http_server
from src.core.monitoring.server import GPUMonitor
from src.api.server import app as api_app
import threading
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_metrics_server(port: int = 8001):
    """Run the Prometheus metrics server."""
    try:
        start_http_server(port)
        monitor = GPUMonitor()
        logger.info(f"Metrics server started on port {port}")
        
        while True:
            monitor.collect_metrics()
            time.sleep(1)
    except Exception as e:
        logger.error(f"Metrics server error: {e}")
        raise

def main():
    # Start metrics server in a separate thread
    metrics_thread = threading.Thread(
        target=run_metrics_server,
        args=(8001,),
        daemon=True
    )
    metrics_thread.start()
    logger.info("Started metrics collection thread")

    # Run the main API server
    uvicorn.run(api_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()