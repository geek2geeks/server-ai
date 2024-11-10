# src/api/server.py

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import torch
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional
import logging

from src.core.gpu_utils import GPUManager

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

@app.post("/process/image")
async def process_image(
    file: UploadFile = File(...),
    operations: Optional[List[str]] = ["resize", "enhance"]
) -> Dict:
    """
    Process uploaded image using GPU acceleration.
    """
    try:
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Convert to GPU tensor
        with gpu_manager.allocate_memory(required_memory_mb=1000) as device_id:
            image_tensor = torch.from_numpy(image).cuda(device_id)
            
            results = {}
            processing_times = {}
            
            # Process based on requested operations
            for op in operations:
                start_time = torch.cuda.Event(enable_timing=True)
                end_time = torch.cuda.Event(enable_timing=True)
                
                start_time.record()
                if op == "resize":
                    # Resize to 4K
                    processed = torch.nn.functional.interpolate(
                        image_tensor.permute(2, 0, 1).unsqueeze(0).float(),
                        size=(2160, 3840),
                        mode='bilinear'
                    )
                elif op == "enhance":
                    # Simple enhancement (example)
                    processed = image_tensor.float() * 1.2
                    processed = torch.clamp(processed, 0, 255)
                
                end_time.record()
                torch.cuda.synchronize()
                
                processing_times[op] = f"{start_time.elapsed_time(end_time):.2f}ms"
                results[op] = processed.cpu().numpy()

            return {
                "status": "success",
                "processing_times": processing_times,
                "gpu_memory": {
                    "allocated": f"{torch.cuda.memory_allocated()/1e9:.2f}GB",
                    "reserved": f"{torch.cuda.memory_reserved()/1e9:.2f}GB"
                }
            }
            
    except Exception as e:
        logger.error(f"Image processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/gpu/stats")
async def get_gpu_statistics() -> Dict:
    """
    Get detailed GPU statistics.
    """
    try:
        stats = gpu_manager.get_gpu_stats()
        memory_stats = gpu_manager.get_system_memory_usage()
        
        return {
            "gpu_stats": stats,
            "system_memory": memory_stats,
            "torch_memory": {
                "allocated": f"{torch.cuda.memory_allocated()/1e9:.2f}GB",
                "reserved": f"{torch.cuda.memory_reserved()/1e9:.2f}GB",
                "max_allocated": f"{torch.cuda.max_memory_allocated()/1e9:.2f}GB"
            }
        }
    except Exception as e:
        logger.error(f"Failed to get GPU stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)