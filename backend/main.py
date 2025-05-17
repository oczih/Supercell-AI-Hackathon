from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dataprocess import DataProcessor
from scraper import RedditScraper
from llm import FeedbackAnalyzer

app = FastAPI()
processor = DataProcessor()
scraper = RedditScraper("ClashRoyale")
feedback_analyzer = FeedbackAnalyzer()

response = feedback_analyzer.analyze_comment("This game is confusing and hard to play.")
print("Model response:", response)
# Allow frontend to access backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with your frontend URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class LoadRequest(BaseModel):
    posts_file: str
    comments_file: str
    analysis_file: str

@app.get("/api/status")
def status():
    # Optional: check if data is loaded
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

# Add more routes for:
# - trending-topics
# - wordcloud
# - top-comments
# - theme-distribution
