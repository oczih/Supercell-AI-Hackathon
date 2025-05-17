import praw
import pandas as pd
import datetime
import os
from dotenv import load_dotenv
import time

# Load environment variables
load_dotenv()

class RedditScraper:
    def __init__(self, subreddit_name):
        """Initialize the Reddit scraper with credentials from environment variables."""
        self.reddit = praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT", "GamePulse:v0.1 (by /u/YourUsername)")
        )
        self.subreddit = self.reddit.subreddit(subreddit_name)
    
    def get_hot_posts(self, limit=25):
        """Fetch hot posts from the subreddit."""
        posts_data = []
        
        for post in self.subreddit.hot(limit=limit):
            # Skip stickied posts (usually announcements)
            if post.stickied:
                continue
                
            post_data = {
                'id': post.id,
                'title': post.title,
                'score': post.score,
                'num_comments': post.num_comments,
                'created_utc': datetime.datetime.fromtimestamp(post.created_utc),
                'url': post.url,
                'selftext': post.selftext,
                'upvote_ratio': post.upvote_ratio
            }
            posts_data.append(post_data)
            
        return pd.DataFrame(posts_data)
    
    def get_post_comments(self, post_id, limit=None):
        """Fetch comments for a specific post."""
        comments_data = []
        submission = self.reddit.submission(id=post_id)
        
        # Replace "MoreComments" objects with actual comments
        submission.comments.replace_more(limit=5)  # Limit to prevent excessive API calls
        
        comment_queue = list(submission.comments)
        while comment_queue and (limit is None or len(comments_data) < limit):
            comment = comment_queue.pop(0)
            
            if not hasattr(comment, 'body'):  # Skip non-comment objects
                continue
                
            comment_data = {
                'id': comment.id,
                'parent_id': comment.parent_id,
                'body': comment.body,
                'score': comment.score,
                'created_utc': datetime.datetime.fromtimestamp(comment.created_utc),
                'depth': comment.depth
            }
            comments_data.append(comment_data)
            
            # Add replies to the queue
            comment_queue.extend(comment.replies)
            
            # Avoid hitting rate limits
            time.sleep(0.1)
            
        return pd.DataFrame(comments_data)
    
    def get_recent_activity(self, post_limit=10, comment_limit=50):
        """Get recent posts and their comments."""
        posts = self.get_hot_posts(limit=post_limit)
        all_comments = []
        
        for post_id in posts['id']:
            comments = self.get_post_comments(post_id, limit=comment_limit)
            # Add post_id to link comments to posts
            if not comments.empty:
                comments['post_id'] = post_id
                all_comments.append(comments)
        
        if all_comments:
            all_comments_df = pd.concat(all_comments)
            return posts, all_comments_df
        else:
            return posts, pd.DataFrame()
            
    def save_data(self, posts, comments, base_filename):
        """Save scraped data to CSV files."""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        posts_filename = f"{base_filename}_posts_{timestamp}.csv"
        comments_filename = f"{base_filename}_comments_{timestamp}.csv"
        
        posts.to_csv(posts_filename, index=False)
        comments.to_csv(comments_filename, index=False)
        
        return posts_filename, comments_filename

# Example usage
if __name__ == "__main__":
    scraper = RedditScraper("ClashRoyale")
    posts, comments = scraper.get_recent_activity()
    
    if not posts.empty:
        print(f"Collected {len(posts)} posts and {len(comments)} comments")
        posts_file, comments_file = scraper.save_data(posts, comments, "clash_royale")
        print(f"Data saved to {posts_file} and {comments_file}")
    else:
        print("No data collected")