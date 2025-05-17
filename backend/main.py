from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dataprocess import DataProcessor
from scraper import RedditScraper
from llm import FeedbackAnalyzer

app = FastAPI()

# Initialize tools
processor = DataProcessor()
scraper = RedditScraper("ClashRoyale")
feedback_analyzer = FeedbackAnalyzer()

# Optional: test the model on startup
response = feedback_analyzer.analyze_comment("This game is confusing and hard to play.")
print("Model response:", response)

# CORS settings - allow all origins (relax this for production!)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Request Models ===
class LoadRequest(BaseModel):
    posts_file: str
    comments_file: str
    analysis_file: str

class CommentRequest(BaseModel):
    text: str

# === Endpoints ===

@app.get("/api/status")
def status():
    return {"status": "ok"}

@app.post("/api/load-data")
def load_data_endpoint(req: LoadRequest):
    load_data(req.posts_file, req.comments_file, req.analysis_file)
    return {"message": "Data loaded successfully."}

@app.get("/api/sentiment-over-time")
def sentiment(period: str = "day"):
    return analyze_data(period)

@app.get("/api/developer-insights")
def insights():
    return generate_insights()

@app.post("/api/analyze-comment")
def analyze_comment_endpoint(req: CommentRequest):
    result = feedback_analyzer.analyze_comment(req.text)
    return result
