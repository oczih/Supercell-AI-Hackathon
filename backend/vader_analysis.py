import pandas as pd
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import ast

def analyze_sentiment(comments_file, output_file):
    # Load comments CSV
    comments_df = pd.read_csv(comments_file)
    
    # Initialize VADER sentiment analyzer
    analyzer = SentimentIntensityAnalyzer()
    
    # Prepare columns for analysis output
    analysis_data = []
    
    for _, row in comments_df.iterrows():
        comment_id = row['id']
        body = str(row['body'])
        
        vs = analyzer.polarity_scores(body)
        compound = vs['compound']
        
        # Determine sentiment category based on compound score
        if compound >= 0.05:
            sentiment = 'positive'
        elif compound <= -0.05:
            sentiment = 'negative'
        else:
            sentiment = 'neutral'
        
        # Fake 'themes' and 'summary' columns to avoid errors (you can customize later)
        themes = []
        summary = ""
        
        analysis_data.append({
            'comment_id': comment_id,
            'sentiment_score': compound,
            'sentiment': sentiment,
            'themes': str(themes),  # stored as string to match your backend expectations
            'summary': summary
        })
    
    # Convert to DataFrame
    analysis_df = pd.DataFrame(analysis_data)
    
    # Save to CSV
    analysis_df.to_csv(output_file, index=False)
    print(f"Sentiment analysis saved to {output_file}")

if __name__ == "__main__":
    comments_csv = "clash_royale_comments_20250517_150746.csv"  # your comments file
    output_csv = "clash_royale_sentiment_20250517_150746.csv"  # output analysis file
    
    analyze_sentiment(comments_csv, output_csv)
