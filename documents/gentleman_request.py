from fastapi import FastAPI
from pydantic import BaseModel
from util import write_file
from gentleman_llm import GentlemanLLM
import os

app = FastAPI()


class AnalyzeRequest(BaseModel):
    """Request model for analyzing a file with GentlemanLLM.

    Args:
        BaseModel (BaseModel): Pydantic base model for request validation.
    """

    filepath: str
    model: str | None
    hf_token: str |None


@app.post("/analyze")
def analyze(req: AnalyzeRequest) -> list[dict]:
    """Analyzes a file using the specified LLM model.

    Args:
        req (GentlemanRequest): The request containing file path, model, and Hugging Face token.

    Returns:
        list[dict]: Analysis results from the LLM.
    """
    if req.model is None:
        model = "meta-llama/Llama-3.1-8B-Instruct"
    else:
        model = req.model
    if req.hf_token is None:
        hf_token = os.getenv("HF_TOKEN")
    else:
        hf_token = req.hf_token
    service = GentlemanLLM(model=model, hf_token=hf_token)
    return service.analyze_file(req.filepath)


class UploadRequest(BaseModel):
    """Request model for uploading a file with GentlemanLLM.

    Args:
        BaseModel (BaseModel): Pydantic base model for request validation.
    """

    filename: str
    content: str
    
@app.post("/upload")
def upload(req: UploadRequest) -> bool:
    """Uploads a file using the specified content.

    Args:
        req (UploadRequest): The request containing filename and content.

    Returns:
        bool: Result of the upload operation.
    """
    write_file(f"code/{req.filename}", req.content)
    return True
