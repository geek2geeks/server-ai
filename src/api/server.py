# E:/justica/src/api/server.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Fix the import path
from src.core.gpu.gpu_utils import GPUManager  # Changed from src.core.gpu_utils

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="GPU-Accelerated AI Server",
    description="High-performance AI server leveraging RTX 3090",
    version="0.1.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize GPU Manager
gpu_manager = GPUManager()

@app.get("/health")
async def health_check() -> Dict:
    """
    Check server health and GPU status.
    """
    try:
        gpu_stats = gpu_manager.get_gpu_stats()
        return {
            "status": "healthy",
            "gpu_available": torch.cuda.is_available(),
            "gpu_info": {
                "name": torch.cuda.get_device_name(0),
                "memory_allocated": f"{torch.cuda.memory_allocated()/1e9:.2f}GB",
                "memory_reserved": f"{torch.cuda.memory_reserved()/1e9:.2f}GB"
            },
            "gpu_stats": gpu_stats
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/process-image")
async def process_image(file: UploadFile = File(...)):
    """
    Process an uploaded image using GPU-accelerated OpenCV.
    """
    try:
        contents = await file.read()
        np_image = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(np_image, cv2.IMREAD_COLOR)

        # Upload image to GPU
        gpu_image = cv2.cuda_GpuMat()
        gpu_image.upload(image)

        # Apply Gaussian Blur on GPU
        gpu_blurred = cv2.cuda.GaussianBlur(gpu_image, (15, 15), 0)
        result_image = gpu_blurred.download()

        _, buffer = cv2.imencode('.jpg', result_image)
        return JSONResponse(content={"status": "success", "data": buffer.tobytes().decode('latin1')})
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gpu-info")
async def get_gpu_info() -> Dict:
    """
    Get detailed GPU information.
    """
    try:
        if not torch.cuda.is_available():
            raise Exception("CUDA is not available")

        gpu_properties = torch.cuda.get_device_properties(0)
        return {
            "name": gpu_properties.name,
            "total_memory": f"{gpu_properties.total_memory / 1e9:.2f} GB",
            "multi_processor_count": gpu_properties.multi_processor_count,
            "cuda_cores": gpu_manager.get_cuda_cores(0),
            "compute_capability": f"{gpu_properties.major}.{gpu_properties.minor}"
        }
    except Exception as e:
        logger.error(f"Failed to get GPU info: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/run-model")
async def run_model(data: Dict):
    """
    Run inference on a given input using a pre-loaded model.
    """
    try:
        # Placeholder for model inference
        input_data = data.get("input")
        if input_data is None:
            raise ValueError("No input data provided")

        # Example dummy model operation
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        input_tensor = torch.tensor(input_data).to(device)
        output = input_tensor * 2  # Dummy operation

        return {"status": "success", "output": output.cpu().tolist()}
    except Exception as e:
        logger.error(f"Model inference failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)