import pandas as pd
import json
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
from tqdm import tqdm
import re

class FeedbackAnalyzer:
    def __init__(self, model_name="mistralai/Mistral-7B-Instruct-v0.2", device="cuda"):
        """
        Initialize the feedback analyzer with a local LLM.
        
        Args:
            model_name: Hugging Face model ID for the LLM
            device: 'cuda' for GPU or 'cpu' for CPU
        """
        self.device = "cuda" if torch.cuda.is_available() and device == "cuda" else "cpu"
        print(f"Using device: {self.device}")
        
        # Load model and tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name, 
            torch_dtype=torch.float16 if self.device == "cuda" else torch.float32,
            low_cpu_mem_usage=True
        ).to(self.device)
        
        # Define sentiment and theme categories
        self.sentiment_categories = ["very negative", "negative", "neutral", "positive", "very positive"]
        self.theme_categories = [
            "bugs/technical issues", 
            "game balance", 
            "gameplay mechanics", 
            "new features/content",
            "monetization", 
            "community/social aspects", 
            "user interface",
            "performance",
            "praise/appreciation"
        ]
    
    def analyze_comment(self, comment_text):
        """Analyze a single comment for sentiment and themes."""
        # Create prompt for the LLM
        prompt = f"""Analyze this gaming-related comment:
        
"{comment_text}"

Respond in JSON format only:
{{
  "sentiment": "one of: very negative, negative, neutral, positive, very positive",
  "sentiment_score": "number from -1.0 to 1.0",
  "themes": ["list of main themes from: bugs/technical issues, game balance, gameplay mechanics, new features/content, monetization, community/social aspects, user interface, performance, praise/appreciation"],
  "summary": "brief one-sentence summary of the comment"
}}
"""
        
        # Generate response from the model
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=512,
                temperature=0.1,  # Low temperature for more deterministic outputs
                do_sample=True
            )
        
        response = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Extract JSON from response
        try:
            # Find text between first '{' and last '}'
            json_text = re.search(r'\{.*\}', response, re.DOTALL)
            if json_text:
                result = json.loads(json_text.group(0))
                return result
            else:
                return {
                    "sentiment": "neutral",
                    "sentiment_score": 0.0,
                    "themes": [],
                    "summary": "Failed to analyze comment"
                }
        except json.JSONDecodeError:
            # Fallback for malformed JSON
            return {
                "sentiment": "neutral",
                "sentiment_score": 0.0,
                "themes": [],
                "summary": "Failed to analyze comment"
            }
    
    def batch_analyze(self, comments_df, text_column="body", batch_size=20):
        """Analyze a batch of comments from a DataFrame."""
        results = []
        
        # Process in batches to show progress and avoid memory issues
        for i in tqdm(range(0, len(comments_df), batch_size)):
            batch = comments_df.iloc[i:i+batch_size]
            
            for _, row in batch.iterrows():
                comment_text = row[text_column]
                if not isinstance(comment_text, str) or not comment_text.strip():
                    continue
                    
                analysis = self.analyze_comment(comment_text)
                
                # Add comment metadata to the analysis
                analysis['comment_id'] = row.get('id', '')
                analysis['post_id'] = row.get('post_id', '')
                analysis['score'] = row.get('score', 0)
                analysis['created_utc'] = row.get('created_utc', '')
                
                results.append(analysis)
        
        return pd.DataFrame(results)
    
    def summarize_thread(self, comments_text):
        """Summarize a thread of comments."""
        # Create prompt for the LLM
        prompt = f"""Summarize the key points and common themes in these gaming-related comments:
        
{comments_text}

Provide:
1. A concise summary of the main discussion points
2. The most common complaints or issues
3. Any positive feedback or appreciation
4. The most important user suggestions

Keep the summary brief but comprehensive.
"""
        
        # Generate response from the model
        inputs = self.tokenizer(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=1024,
                temperature=0.3
            )
        
        summary = self.tokenizer.decode(outputs[0], skip_special_tokens=True)
        
        # Remove the initial prompt from the summary
        if summary.startswith(prompt):
            summary = summary[len(prompt):].strip()
        
        return summary
    
    def export_results(self, analysis_df, filename):
        """Export analysis results to CSV."""
        analysis_df.to_csv(filename, index=False)
        print(f"Analysis exported to {filename}")

# Example usage
if __name__ == "__main__":
    analyzer = FeedbackAnalyzer()

    # Single comment analysis
    response = analyzer.analyze_comment("This game is confusing and hard to play.")
    print(response)

    # Load comments from CSV
    comments_df = pd.read_csv("clash_royale_comments_20240516_120000.csv")

    # Batch analyze
    analysis_results = analyzer.batch_analyze(comments_df)

    # Export results
    analyzer.export_results(analysis_results, "clash_royale_analysis_results.csv")

    # Generate summary for a specific post
    post_id = "example_post_id"
    post_comments = comments_df[comments_df['post_id'] == post_id]['body'].tolist()
    if post_comments:
        post_comments_text = "\n\n".join(post_comments[:20])  # Limit to first 20 comments
        summary = analyzer.summarize_thread(post_comments_text)
        print(f"Thread Summary for post {post_id}:\n{summary}")
