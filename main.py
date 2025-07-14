import praw
import os
import openai
from dotenv import load_dotenv
import time
from datetime import datetime
from urllib.parse import urlparse

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

def initialize_reddit():
    """Initialize and return the Reddit API client"""
    try:
        return praw.Reddit(
            client_id=os.getenv("REDDIT_CLIENT_ID"),
            client_secret=os.getenv("REDDIT_CLIENT_SECRET"),
            user_agent=os.getenv("REDDIT_USER_AGENT")
        )
    except Exception as e:
        print(f"Failed to initialize Reddit client: {e}")
        return None

def validate_reddit_url(url):
    """Validate the Reddit profile URL format"""
    try:
        parsed = urlparse(url)
        if not all([parsed.scheme, parsed.netloc]):
            return False
        if "/user/" not in url:
            return False
        return True
    except:
        return False

def get_user_content(reddit, username, limit=25):
    """Fetch user posts and comments with error handling and rate limiting"""
    try:
        time.sleep(2)  # Rate limiting protection
        user = reddit.redditor(username)
        
        comments = []
        for comment in user.comments.new(limit=limit):
            comments.append(comment.body)
            time.sleep(0.5)  # Small delay between requests
        
        posts = []
        for submission in user.submissions.new(limit=limit):
            posts.append(f"{submission.title}\n{submission.selftext or ''}")
            time.sleep(0.5)
            
        return comments, posts
        
    except praw.exceptions.PRAWException as e:
        print(f"Reddit API error: {e}")
    except Exception as e:
        print(f"Unexpected error fetching content: {e}")
    return [], []

def generate_persona(comments, posts):
    """Generate persona using OpenAI with improved prompt and error handling"""
    try:
        # Combine and limit content to prevent exceeding token limits
        combined = "\n---POSTS---\n".join(posts[:5]) + "\n---COMMENTS---\n" + "\n".join(comments[:10])
        combined = combined[:8000]  # Roughly 2000 words limit
        
        prompt = f"""
Create a comprehensive user persona from these Reddit activities. For each trait:
1. Cite the exact text that supports it
2. Explain your reasoning
3. Rate confidence level (High/Medium/Low)

Format exactly like this:

=== PERSONA REPORT ===
Username: [username]

1. DEMOGRAPHICS:
- [Trait]: [Quote] (Confidence: [Level])
- [Trait]: [Quote] (Confidence: [Level])

2. INTERESTS:
- [Interest]: [Quote] (Confidence: [Level])

3. PERSONALITY:
- [Trait]: [Quote] (Confidence: [Level])

4. VALUES:
- [Value]: [Quote] (Confidence: [Level])

5. COMMUNICATION STYLE:
- [Style]: [Quote] (Confidence: [Level])

Content to analyze:
{combined}
"""
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7,
            max_tokens=1500
        )
        return response['choices'][0]['message']['content']
        
    except openai.error.OpenAIError as e:
        print(f"OpenAI API error: {e}")
    except Exception as e:
        print(f"Error generating persona: {e}")
    return "Persona generation failed. Please try again later."

def save_persona(username, persona):
    """Save persona to file with timestamp"""
    try:
        os.makedirs("output", exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"output/{username}_persona_{timestamp}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(persona)
        print(f"\nPersona saved to {filename}")
        return True
        
    except Exception as e:
        print(f"Failed to save persona: {e}")
        return False

def main():
    print("Reddit Persona Generator")
    print("------------------------")
    
    try:
        # Check requirements
        import praw
        import openai
    except ImportError:
        print("Missing required libraries. Run: pip install -r requirements.txt")
        return
    
    # Get and validate URL
    url = input("Enter Reddit profile URL (e.g., https://www.reddit.com/user/username/): ").strip()
    if not validate_reddit_url(url):
        print("Error: Invalid Reddit profile URL format")
        return
    
    username = url.split("/user/")[-1].rstrip("/")
    
    # Initialize Reddit
    reddit = initialize_reddit()
    if not reddit:
        return
    
    # Fetch content
    print(f"\nFetching content for: {username}")
    comments, posts = get_user_content(reddit, username)
    
    if not comments and not posts:
        print("Error: No content found or failed to fetch data")
        return
    
    print(f"Found {len(posts)} posts and {len(comments)} comments")
    
    # Generate persona
    print("\nGenerating persona... (This may take a moment)")
    persona = generate_persona(comments, posts)
    
    # Save and show result
    if save_persona(username, persona):
        print("\n=== PERSONA GENERATED SUCCESSFULLY ===")
        print("\nSummary:\n" + persona[:500] + "...")  # Show first part
    else:
        print("\nPersona generation completed but failed to save")

if __name__ == "__main__":
    main()