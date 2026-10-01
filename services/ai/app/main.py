from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .rag_engine import ask_question

app = FastAPI(title="BrokerLite AI Service")

class ChatRequest(BaseModel):
    question: str

class ChatResponse(BaseModel):
    answer: str

@app.post("/chat", response_model=ChatResponse)
def chat_with_ai(request: ChatRequest):
    try:
        # Call the RAG engine
        answer = ask_question(request.question)
        return {"answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
def health_check():
    return {"status": "AI Service is running"}