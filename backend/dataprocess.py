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
        """Initialize with data files if provided (expects JSON files)."""
        self.posts_df = None
        self.comments_df = None
        self.analysis_df = None
        
        # Load data if files are provided
        if any([posts_file, comments_file, analysis_file]):
            self.load_data(posts_file, comments_file, analysis_file)
    
    def load_data(self, posts_file=None, comments_file=None, analysis_file=None):
        """Load data from JSON files."""
        try:
            if posts_file:
                self.posts_df = pd.read_json(posts_file)
                if 'created_utc' in self.posts_df.columns:
                    # Handle created_utc which may be in string format
                    if self.posts_df['created_utc'].dtype == 'object':
                        self.posts_df['created_utc'] = pd.to_datetime(self.posts_df['created_utc'])
                print(f"Posts DataFrame loaded: {self.posts_df.shape}")
        except Exception as e:
            print(f"Failed to load posts data: {e}")
            
        try:
            if comments_file:
                self.comments_df = pd.read_json(comments_file)
                if 'created_utc' in self.comments_df.columns:
                    # Handle created_utc which may be in string format
                    if self.comments_df['created_utc'].dtype == 'object':
                        self.comments_df['created_utc'] = pd.to_datetime(self.comments_df['created_utc'])
                print(f"Comments DataFrame loaded: {self.comments_df.shape}")
        except Exception as e:
            print(f"Failed to load comments data: {e}")
            
        try:
            if analysis_file:
                self.analysis_df = pd.read_json(analysis_file)
                if 'created_utc' in self.analysis_df.columns:
                    # Handle created_utc which may be in string format
                    if self.analysis_df['created_utc'].dtype == 'object':
                        self.analysis_df['created_utc'] = pd.to_datetime(self.analysis_df['created_utc'])
                print(f"Analysis DataFrame loaded: {self.analysis_df.shape}")
        except Exception as e:
            print(f"Failed to load analysis data: {e}")
            
        # Load data from strings if provided (for testing and direct input)
        self._update_data_structure()    
    def _parse_themes(self, themes_data):
        """Helper method to parse themes data which could be in different formats."""
        if isinstance(themes_data, list):
            return themes_data
        elif isinstance(themes_data, str):
            try:
                return eval(themes_data)  # Convert string representation to list
            except:
                return []
        else:
            return []
    def get_trending_topics(self, limit=30):
        """Extract trending topics from the analysis."""
        if self.analysis_df is None:
            return []
        
        # Check if we have themes data
        if 'themes' not in self.analysis_df.columns or self.analysis_df['themes'].isnull().all() or (
                self.analysis_df['themes'].astype(str).str.strip() == '[]').all():
            # If no themes data, analyze comment text to create topics
            if self.analysis_df is not None and self.comments_df is not None:
                # Create a mapping of comment_id to comment text
                comment_id_to_text = {}
                for _, row in self.comments_df.iterrows():
                    comment_id_to_text[row['id']] = row['body']
                
                # Extract words from comments referenced in analysis
                comment_words = []
                for _, row in self.analysis_df.iterrows():
                    comment_id = row['comment_id']
                    if comment_id in comment_id_to_text:
                        # Simple word extraction (could be improved with NLP)
                        words = comment_id_to_text[comment_id].lower().split()
                        # Filter out common words and short words
                        words = [w for w in words if len(w) > 3 and w not in 
                                ['this', 'that', 'have', 'with', 'will', 'game', 'just', 'from', 'they', 'what', 'when']]
                        comment_words.extend(words)
                
                # Count word occurrences
                word_counts = Counter(comment_words)
                
                # Return top N words as topics
                return [{"theme": word, "count": count} 
                        for word, count in word_counts.most_common(limit)]
            return []
        
        # If we have themes data, use it
        all_themes = []
        for themes_str in self.analysis_df['themes'].dropna():
            try:
                # Handle different formats of themes data
                themes = self._parse_themes(themes_str)
                if isinstance(themes, list):
                    all_themes.extend(themes)
            except Exception as e:
                print(f"Error parsing themes: {e}")
                continue
        
        # Count theme occurrences
        theme_counts = Counter(all_themes)
        
        # Return top N themes
        return [{"theme": theme, "count": count} 
                for theme, count in theme_counts.most_common(limit)]
    
    def get_sentiment_over_time(self, time_period='day'):
        if self.analysis_df is None or self.comments_df is None:
            return []

        df = self.analysis_df.copy()
        # Yhdistetään created_utc comments_df:stä oikealla sarakkeen nimellä
        df = df.merge(self.comments_df[['id', 'created_utc']], left_on='comment_id', right_on='id', how='left')

        df['sentiment_score'] = pd.to_numeric(df['sentiment_score'], errors='coerce')
        df['created_utc'] = pd.to_datetime(df['created_utc'])

        if time_period == 'hour':
            df['time_bucket'] = df['created_utc'].dt.floor('H')
        elif time_period == 'day':
            df['time_bucket'] = df['created_utc'].dt.floor('D')
        elif time_period == 'week':
            df['time_bucket'] = df['created_utc'].dt.floor('W')
        else:
            df['time_bucket'] = df['created_utc'].dt.floor('D')

        sentiment_by_time = df.groupby('time_bucket')['sentiment_score'].agg(['mean', 'count']).reset_index()

        result = []
        for _, row in sentiment_by_time.iterrows():
            mean_val = float(row['mean']) if not pd.isna(row['mean']) else 0.0
            result.append({
                "timestamp": row['time_bucket'].isoformat(),
                "sentiment": mean_val,
                "count": int(row['count'])
            })

        return sorted(result, key=lambda x: x['timestamp'])



    
    def get_top_comments(self, limit=50, sort_by='score'):
        """Get top comments based on score or other metrics."""
        if self.analysis_df is None or self.comments_df is None:
            return []

        # Create a copy to avoid modifying original dataframes
        analysis_df = self.analysis_df.copy()
        comments_df = self.comments_df.copy()

        # Merge dataframes
        merged_df = pd.merge(
            analysis_df, 
            comments_df[['id', 'body', 'score', 'created_utc']],
            left_on='comment_id', 
            right_on='id',
            how='inner'
        )

        # Remove infinite values and NaNs that aren't JSON-compatible
        merged_df = merged_df.replace([float('inf'), float('-inf')], np.nan)
        merged_df = merged_df.dropna(subset=['sentiment_score', 'body', 'score'])
        
        # Sort based on requested criterion
        if sort_by == 'sentiment':
            merged_df = merged_df.sort_values('sentiment_score', ascending=False)
        else:  # default to score
            merged_df = merged_df.sort_values('score', ascending=False)

        # Extract top comments
        top_comments = []
        for _, row in merged_df.head(limit).iterrows():
            try:
                created_str = row['created_utc'].isoformat() if hasattr(row['created_utc'], 'isoformat') else str(row['created_utc'])
                themes_val = self._parse_themes(row['themes'])
                
                top_comments.append({
                    "id": row['comment_id'],
                    "body": row['body'],
                    "score": int(row['score']),
                    "sentiment": float(row['sentiment_score']),
                    "sentiment_category": row['sentiment'],
                    "themes": themes_val,
                    "summary": row.get('summary', ''),
                    "created_utc": created_str,
                })
            except Exception as e:
                print(f"Error processing row id {row.get('comment_id', 'unknown')}: {e}")

        return top_comments
    
    def get_theme_distribution(self):
        print(self.analysis_df['themes'].head(10))
        """Get the distribution of themes."""
        if self.analysis_df is None:
            return {}
        # Extract all themes
        all_themes = []
        for themes_str in self.analysis_df['themes'].dropna():
            try:
                themes = self._parse_themes(themes_str)
                if isinstance(themes, list):
                    all_themes.extend(themes)
            except Exception as e:
                print(f"Error parsing themes: {e}")
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
        
        try:
            # Combine all comment text, limit to reduce memory usage
            sample_size = min(1000, len(self.comments_df))
            sampled_comments = self.comments_df.sample(sample_size) if len(self.comments_df) > sample_size else self.comments_df
            text = " ".join(sampled_comments['body'].dropna().astype(str))
            
            # Create word cloud
            wordcloud = WordCloud(
                width=width, 
                height=height, 
                background_color='white',
                max_words=200  # Limit words for performance
            ).generate(text)
            
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
        except Exception as e:
            print(f"Error generating wordcloud: {e}")
            return None
    
    def get_developer_insights(self):
        """Generate insights specifically for developers."""
        if self.analysis_df is None or self.comments_df is None:
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
                try:
                    row_themes = self._parse_themes(row['themes'])
                    
                    if any(theme in row_themes for theme in themes):
                        # Find the corresponding comment text
                        comment_row = self.comments_df[self.comments_df['id'] == row['comment_id']]
                        if not comment_row.empty:
                            comment_text = comment_row.iloc[0]['body']
                            score = comment_row.iloc[0]['score']
                            
                            category_comments.append({
                                "id": row['comment_id'],
                                "text": comment_text,
                                "score": int(score),
                                "sentiment": float(row['sentiment_score']),
                                "summary": row.get('summary', '')
                            })
                except Exception as e:
                    print(f"Error processing developer insights for row: {e}")
                    continue
            
            # Sort by score and get top 5
            category_comments = sorted(category_comments, key=lambda x: x['score'], reverse=True)[:5]
            insights[category_name] = category_comments
        
        return insights
    
    def _update_data_structure(self):
        """Update data structure to ensure compatibility with API methods."""
        # Check and handle themes field in analysis data
        if self.analysis_df is not None and 'themes' in self.analysis_df.columns:
            # Ensure themes is properly formatted
            self.analysis_df['themes'] = self.analysis_df['themes'].apply(
                lambda x: '[]' if pd.isna(x) or x == '' else x)
            
        # Add any missing columns with default values
        if self.analysis_df is not None:
            if 'summary' not in self.analysis_df.columns:
                self.analysis_df['summary'] = None

# Flask API routes
processor = DataProcessor()

@app.route('/api/load-data', methods=['POST'])
def load_data():
    """Load data files."""
    try:
        data = request.json
        posts_file = data.get('posts_file')
        comments_file = data.get('comments_file')
        analysis_file = data.get('analysis_file')
        
        if not posts_file or not comments_file:
            return jsonify({"error": "Missing required file paths"}), 400
        
        processor.load_data(posts_file, comments_file, analysis_file)
        return jsonify({"status": "Data loaded successfully"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/trending-topics', methods=['GET'])
def trending_topics():
    """Get trending topics."""
    try:
        limit = request.args.get('limit', default=10, type=int)
        topics = processor.get_trending_topics(limit=limit)
        return jsonify(topics)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/sentiment-over-time', methods=['GET'])
def sentiment_over_time():
    try:
        time_period = request.args.get('period', default='day')
        sentiment_data = processor.get_sentiment_over_time(time_period=time_period)
        return jsonify(sentiment_data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/top-comments', methods=['GET'])
def top_comments():
    """Get top comments."""
    try:
        limit = request.args.get('limit', default=10, type=int)
        sort_by = request.args.get('sort_by', default='score')
        comments = processor.get_top_comments(limit=limit, sort_by=sort_by)
        return jsonify(comments)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/theme-distribution', methods=['GET'])
def theme_distribution():
    """Get theme distribution."""
    try:
        distribution = processor.get_theme_distribution()
        return jsonify(distribution)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/wordcloud', methods=['GET'])
def wordcloud():
    """Get word cloud image."""
    try:
        width = request.args.get('width', default=800, type=int)
        height = request.args.get('height', default=400, type=int)
        image = processor.generate_wordcloud(width=width, height=height)
        if image:
            return jsonify({"image": image})
        else:
            return jsonify({"error": "Could not generate word cloud"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/developer-insights', methods=['GET'])
def developer_insights():
    """Get developer insights."""
    try:
        insights = processor.get_developer_insights()
        return jsonify(insights)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/status', methods=['GET'])
def status():
    """Get API status and data summary."""
    try:
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
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)