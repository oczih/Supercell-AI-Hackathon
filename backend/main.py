from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI
from pydantic import BaseModel
from dataprocess import DataProcessor
from scraper import RedditScraper
from llm import FeedbackAnalyzer
from fastapi import HTTPException, Query
from typing import Optional

app = FastAPI()
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]
# Initialize tools
processor = DataProcessor()
scraper = RedditScraper("ClashRoyale")
feedback_analyzer = None

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Optional: test the model on startup
#response = feedback_analyzer.analyze_comment("This game is confusing and hard to play.")
#print("Model response:", response)
def get_feedback_analyzer():
    global feedback_analyzer
    if feedback_analyzer is None:
        feedback_analyzer = FeedbackAnalyzer()
    return feedback_analyzer
# CORS settings - allow all origins (relax this for production!)

class LoadRequest(BaseModel):
    posts_file: str
    comments_file: str
    analysis_file: Optional[str] = None

@app.post("/api/load-data")
async def load_data(req: LoadRequest):
    try:
        processor.load_data(req.posts_file, req.comments_file, req.analysis_file)
        return {"status": "Data loaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/trending-topics")
async def trending_topics(limit: int = Query(10, ge=1)):
    return processor.get_trending_topics(limit=limit)

@app.get("/api/sentiment-over-time")
async def sentiment_over_time(period: str = Query("day")):
    return processor.get_sentiment_over_time(time_period=period)

@app.get("/api/top-comments")
async def top_comments(limit: int = Query(10, ge=1), sort_by: str = Query("score")):
    return processor.get_top_comments(limit=limit, sort_by=sort_by)

@app.get("/api/theme-distribution")
async def theme_distribution():
    return processor.get_theme_distribution()

@app.get("/api/wordcloud")
async def wordcloud(width: int = Query(800, ge=100), height: int = Query(400, ge=100)):
    image = processor.generate_wordcloud(width=width, height=height)
    if image:
        return {"image": image}
    else:
        raise HTTPException(status_code=500, detail="Could not generate word cloud")

@app.get("/api/developer-insights")
async def developer_insights():
    return processor.get_developer_insights()

@app.get("/api/status")
async def status():
    data_status = {
        "posts_loaded": processor.posts_df is not None,
        "comments_loaded": processor.comments_df is not None,
        "analysis_loaded": processor.analysis_df is not None,
    }

    if processor.posts_df is not None:
        data_status["post_count"] = len(processor.posts_df)

    if processor.comments_df is not None:
        data_status["comment_count"] = len(processor.comments_df)

    if processor.analysis_df is not None:
        data_status["analyzed_comment_count"] = len(processor.analysis_df)

    return data_status


class CommentRequest(BaseModel):
    text: str

@app.post("/api/analyze-comment")
async def analyze_comment(req: CommentRequest):
    analyzer = get_feedback_analyzer()
    try:
        result = analyzer.analyze_comment(req.text)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))