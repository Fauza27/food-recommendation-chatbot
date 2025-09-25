from fastapi import FastAPI
from dotenv import load_dotenv
from api.chatbot import router as chatbot_router
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI(title="RAG Chatbot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001","http://food-recomendation-chatbot-app.us-east-1.elasticbeanstalk.com", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chatbot_router, prefix="/api")

@app.get("/")
def root():
    return {"message": "RAG Chatbot Backend is running"}

@app.get("/health")
async def health():
    return {"status": "healthy"}