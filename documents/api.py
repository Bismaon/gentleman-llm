from fastapi import FastAPI
from pydantic import BaseModel
from gentleman_llm import GentlemanLLM

app = FastAPI()

class GentlemanRequest(BaseModel):
    filepath: str
    model: str | None
    hf_token: str


@app.post("/analyze")
def analyze(req: GentlemanRequest):
    if req.model is None:
        model = "meta-llama/Llama-3.1-8B-Instruct"
    else :
        model = req.model
    service = GentlemanLLM(model=model, hf_token=req.hf_token)
    return service.analyze_file(req.filepath)
