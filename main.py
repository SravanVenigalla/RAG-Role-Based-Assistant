from fastapi import FastAPI, Depends
from app.auth import authenticate
from app.rag_chain import get_rag_chain

app = FastAPI(title="RAG Role-Based Assistant")

@app.get("/")
def root():
    return {"message": "Welcome to RAG Role-Based Assistant API"}

@app.post("/login")
def login(user=Depends(authenticate)):
    return user

@app.post("/chat")
def chat(query: str, user=Depends(authenticate)):
    response = get_rag_chain(user["role"], query)
    return {"answer": response["answer"]}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
