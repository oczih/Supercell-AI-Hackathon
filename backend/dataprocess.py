from flask import Flask, jsonify, request
import pandas as pd
import numpy as np
from collections import Counter
import datetime
import os
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import io
import base64
from flask_cors import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

class DataProcessor:
    def __init__(self, posts_file=None, comments_file=None, analysis_file=None):
        """Initialize with data files if provided."""
        self.posts_df = pd.read_csv(posts_file) if posts_file else None
        self.comments_df = pd.read_csv(comments_file) if comments_file else None
        self.analysis_df = pd.read_csv(analysis_file) if analysis_file else None

        if self.analysis_df is not None:
            print("Analysis DataFrame columns:", self.analysis_df.columns)
        else:
            print("Analysis DataFrame not loaded.")

        if self.comments_df is not None:
            print("Comments DataFrame columns:", self.comments_df.columns)
        else:
            print("Comments DataFrame not loaded.")

        # Convert datetime strings to datetime objects
        if self.posts_df is not None and 'created_utc' in self.posts_df.columns:
            self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])

        if self.comments_df is not None and 'created_utc' in self.comments_df.columns:
            self.comments_df['created_utc'] = pd.to_datetime(self.comments_df['created_utc'])

        if self.analysis_df is not None and 'created_utc' in self.analysis_df.columns:
            self.analysis_df['created_utc'] = pd.to_datetime(self.analysis_df['created_utc'])

    
    def load_data(self, posts_file, comments_file, analysis_file=None):
        """Load data from CSV files."""
        self.posts_df = pd.read_csv(posts_file)
        self.comments_df = pd.read_csv(comments_file)
        
        if analysis_file:
            self.analysis_df = pd.read_csv(analysis_file)
        
        # Convert datetime strings to datetime objects
        if 'created_utc' in self.posts_df.columns:
            self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
        
        if 'created_utc' in self.comments_df.columns:
            self.comments_df['created_utc'] = pd.to_datetime(self.comments_df['created_utc'])
        
        if self.analysis_df is not None and 'created_utc' in self.analysis_df.columns:
            self.analysis_df['created_utc'] = pd.to_datetime(self.analysis_df['created_utc'])
    
    def get_trending_topics(self, limit=10):
        """Extract trending topics from the analysis."""
        if self.analysis_df is None:
            return []
        
        # Flatten the themes lists and count occurrences
        all_themes = []
        for themes_str in self.analysis_df['themes'].dropna():
            try:
                # Convert string representation of list to actual list
                themes = eval(themes_str) if isinstance(themes_str, str) else themes_str
                if isinstance(themes, list):
                    all_themes.extend(themes)
            except:
                continue
        
        # Count theme occurrences
        theme_counts = Counter(all_themes)
        
        # Return top N themes
        return [{"theme": theme, "count": count} 
                for theme, count in theme_counts.most_common(limit)]
    
    def get_sentiment_over_time(self, time_period='day'):
        """Calculate sentiment scores over time."""
        if self.analysis_df is None:
            return []
        
        # Ensure sentiment_score is numeric
        self.analysis_df['sentiment_score'] = pd.to_numeric(
            self.analysis_df['sentiment_score'], errors='coerce')
        
        # Group by time period
        if time_period == 'hour':
            self.analysis_df['time_bucket'] = self.analysis_df['created_utc'].dt.floor('H')
        elif time_period == 'day':
            self.analysis_df['time_bucket'] = self.analysis_df['created_utc'].dt.floor('D')
        elif time_period == 'week':
            self.analysis_df['time_bucket'] = self.analysis_df['created_utc'].dt.floor('W')
        else:
            self.analysis_df['time_bucket'] = self.analysis_df['created_utc'].dt.floor('D')
        
        # Calculate average sentiment per time period
        sentiment_by_time = self.analysis_df.groupby('time_bucket')['sentiment_score'].agg(
            ['mean', 'count']).reset_index()
        
        # Convert to list of dictionaries for JSON serialization
        result = []
        for _, row in sentiment_by_time.iterrows():
            result.append({
                "timestamp": row['time_bucket'].isoformat(),
                "sentiment": float(row['mean']),
                "count": int(row['count'])
            })
        
        return sorted(result, key=lambda x: x['timestamp'])
    
    def get_top_comments(self, limit=10, sort_by='score'):
        """Get top comments based on score or other metrics."""
        if self.analysis_df is None or self.comments_df is None:
            return []
        
        # Merge analysis with comments
        merged_df = pd.merge(
            self.analysis_df, 
            self.comments_df[['id', 'body', 'score', 'created_utc']],
            left_on='comment_id', 
            right_on='id',
            how='inner'
        )
        
        # Sort by the specified column
        if sort_by == 'sentiment':
            merged_df = merged_df.sort_values('sentiment_score', ascending=False)
        else:  # Default to score
            merged_df = merged_df.sort_values('score', ascending=False)
        
        # Get top N comments
        top_comments = []
        for _, row in merged_df.head(limit).iterrows():
            top_comments.append({
                "id": row['comment_id'],
                "body": row['body'],
                "score": int(row['score']),
                "sentiment": float(row['sentiment_score']),
                "sentiment_category": row['sentiment'],
                "themes": eval(row['themes']) if isinstance(row['themes'], str) else row['themes'],
                "summary": row['summary'],
                "created_utc": row['created_utc'].isoformat()
            })
        
        return top_comments
    
    def get_theme_distribution(self):
        """Get the distribution of themes."""
        if self.analysis_df is None:
            return {}
        
        # Extract all themes
        all_themes = []
        for themes_str in self.analysis_df['themes'].dropna():
            try:
                themes = eval(themes_str) if isinstance(themes_str, str) else themes_str
                if isinstance(themes, list):
                    all_themes.extend(themes)
            except:
                continue
        
        # Count theme occurrences
        theme_counts = Counter(all_themes)
        total = sum(theme_counts.values())
        
        # Calculate percentages
        result = {}
        for theme, count in theme_counts.items():
            result[theme] = {
                "count": count,
                "percentage": round(count / total * 100, 2) if total > 0 else 0
            }
        
        return result
    
    def generate_wordcloud(self, width=800, height=400):
        """Generate a word cloud image from comment text."""
        if self.comments_df is None:
            return None
        
        # Combine all comment text
        text = " ".join(self.comments_df['body'].dropna().astype(str))
        
        # Create word cloud
        wordcloud = WordCloud(width=width, height=height, background_color='white').generate(text)
        
        # Convert to image
        plt.figure(figsize=(width/100, height/100), dpi=100)
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        
        # Save to a bytes buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        # Convert to base64 string
        img_str = base64.b64encode(buf.read()).decode('utf-8')
        return f"data:image/png;base64,{img_str}"
    
    def get_developer_insights(self):
        """Generate insights specifically for developers."""
        if self.analysis_df is None:
            return {}
        
        # Categories of interest for developers
        categories = {
            "bugs": ["bugs/technical issues"],
            "balance": ["game balance"],
            "features": ["new features/content", "gameplay mechanics"],
            "ux": ["user interface", "performance"],
            "monetization": ["monetization"]
        }
        
        insights = {}
        
        # For each category, find relevant comments
        for category_name, themes in categories.items():
            category_comments = []
            
            for _, row in self.analysis_df.iterrows():
                row_themes = eval(row['themes']) if isinstance(row['themes'], str) else row['themes']
                
                if any(theme in row_themes for theme in themes):
                    # Find the corresponding comment text
                    if self.comments_df is not None:
                        comment_row = self.comments_df[self.comments_df['id'] == row['comment_id']]
                        if not comment_row.empty:
                            comment_text = comment_row.iloc[0]['body']
                            score = comment_row.iloc[0]['score']
                            
                            category_comments.append({
                                "id": row['comment_id'],
                                "text": comment_text,
                                "score": int(score),
                                "sentiment": float(row['sentiment_score']),
                                "summary": row['summary']
                            })
            
            # Sort by score and get top 5
            category_comments = sorted(category_comments, key=lambda x: x['score'], reverse=True)[:5]
            insights[category_name] = category_comments
        
        return insights

# Flask API routes
processor = DataProcessor()

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Load data files."""
    data = request.json
    posts_file = data.get('posts_file')
    comments_file = data.get('comments_file')
    analysis_file = data.get('analysis_file')
    
    if not posts_file or not comments_file:
        return jsonify({"error": "Missing required file paths"}), 400
    
    try:
        processor.load_data(posts_file, comments_file, analysis_file)
        return jsonify({"status": "Data loaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trending-topics', methods=['GET'])
def trending_topics():
    """Get trending topics."""
    limit = request.args.get('limit', default=10, type=int)
    topics = processor.get_trending_topics(limit=limit)
    return jsonify(topics)

@app.route('/api/sentiment-over-time', methods=['GET'])
def sentiment_over_time():
    """Get sentiment over time."""
    time_period = request.args.get('period', default='day')
    sentiment_data = processor.get_sentiment_over_time(time_period=time_period)
    return jsonify(sentiment_data)

@app.route('/api/top-comments', methods=['GET'])
def top_comments():
    """Get top comments."""
    limit = request.args.get('limit', default=10, type=int)
    sort_by = request.args.get('sort_by', default='score')
    comments = processor.get_top_comments(limit=limit, sort_by=sort_by)
    return jsonify(comments)

@app.route('/api/theme-distribution', methods=['GET'])
def theme_distribution():
    """Get theme distribution."""
    distribution = processor.get_theme_distribution()
    return jsonify(distribution)

@app.route('/api/wordcloud', methods=['GET'])
def wordcloud():
    """Get word cloud image."""
    width = request.args.get('width', default=800, type=int)
    height = request.args.get('height', default=400, type=int)
    image = processor.generate_wordcloud(width=width, height=height)
    if image:
        return jsonify({"image": image})
    else:
        return jsonify({"error": "Could not generate word cloud"}), 500

@app.route('/api/developer-insights', methods=['GET'])
def developer_insights():
    """Get developer insights."""
    insights = processor.get_developer_insights()
    return jsonify(insights)

@app.route('/api/status', methods=['GET'])
def status():
    """Get API status and data summary."""
    data_status = {
        "posts_loaded": processor.posts_df is not None,
        "comments_loaded": processor.comments_df is not None,
        "analysis_loaded": processor.analysis_df is not None
    }
    
    if processor.posts_df is not None:
        data_status["post_count"] = len(processor.posts_df)
    
    if processor.comments_df is not None:
        data_status["comment_count"] = len(processor.comments_df)
    
    if processor.analysis_df is not None:
        data_status["analyzed_comment_count"] = len(processor.analysis_df)
    
    return jsonify(data_status)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)