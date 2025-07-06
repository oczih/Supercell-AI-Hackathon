A web app that gathers, analyzes, and visualizes player feedback from public sources like Reddit, YouTube comments, and app reviews — powered by open-source LLMs, no paid APIs.

🧩 Core Features
  1. Data Scraping
    🔍 Pull Reddit threads from a game’s subreddit (e.g., r/ClashRoyale)
  Optional: Scrape YouTube comments from recent videos
  Optional: Parse Google Play / App Store reviews (static samples or small-scale scraping)
  2. Natural Language Processing
  🧠 Use a local LLM (like Mistral 7B or TinyLlama or smaller LLM) to:
    - Summarize long threads or comment chains
    - Detect themes (bugs, balance issues, praise)
    - Categorize and score sentiment
  3. Visualization Dashboard
  📊 Show:
    Trending topics (word cloud or tag list)
    Sentiment over time (graph)
    Most liked or insightful comments
  Toggle between Reddit / YouTube / Reviews
  4. Developer Mode
    🛠️ View top pain points by category: “Bug reports,” “Frustrations,” “Suggestions”, i have now 4 files for backend do you think they are enough, i have dataprocess.py llm.py scraper.py and main.py
