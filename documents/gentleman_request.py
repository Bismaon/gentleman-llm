from fastapi import FastAPI
from pydantic import BaseModel
from gentleman_llm import GentlemanLLM

app = FastAPI()


class GentlemanRequest(BaseModel):
    """Request model for analyzing a file with GentlemanLLM.

    Args:
        BaseModel (BaseModel): Pydantic base model for request validation.
    """

    filepath: str
    model: str | None
    hf_token: str


@app.post("/analyze")
def analyze(req: GentlemanRequest) -> list[dict]:
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
    service = GentlemanLLM(model=model, hf_token=req.hf_token)
    return service.analyze_file(req.filepath)
