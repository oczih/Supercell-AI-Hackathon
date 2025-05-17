import pandas as pd
import os

def csv_to_json(csv_file, json_file):
    df = pd.read_csv(csv_file)
    df.to_json(json_file, orient='records', date_format='iso')
    print(f"Converted {csv_file} to {json_file}")

if __name__ == "__main__":
    base_path = os.path.dirname(os.path.abspath(__file__))

    posts_csv = os.path.join(base_path, "clash_royale_posts_20250517_150746.csv")  # Replace with your actual filename
    comments_csv = os.path.join(base_path, "clash_royale_comments_20250517_150746.csv")  # Replace with your actual filename
    sentiment_csv = os.path.join(base_path, "clash_royale_sentiment_20250517_150746.csv")
    posts_json = os.path.join(base_path, "data", "posts.json")
    comments_json = os.path.join(base_path, "data", "comments.json")
    sentiment_json = os.path.join(base_path, "data", "sentiment.json")
    # Make sure the 'data' folder exists
    os.makedirs(os.path.join(base_path, "data"), exist_ok=True)

    csv_to_json(posts_csv, posts_json)
    csv_to_json(comments_csv, comments_json)
    csv_to_json(sentiment_csv, sentiment_json)
