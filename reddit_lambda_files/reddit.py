# this function is used to build the raw results using a reddit scrape

import json
import praw

def lambda_handler(event, context):

    reddit = praw.Reddit(client_id='2z1kCNZ87wgQbs8k0fr5ew', client_secret='4V-jniLxhQvjiYZC3FgCYjEy5B27zA')

    subreddit = reddit.subreddit('AskReddit')
    top_posts = subreddit.top(limit=10)

    for post in top_posts:
        print(post.title)
    
    
    reddit_results = {
        "comments":
            [
                {"comment_body": "Magnesium helps me with tension headaches and anxiety, lemon balm for anxiety, melatonin for sleep if i cant fall asleep on my own, probiotics to help keep me regular and maca helps to get me in the mood better since i also take sertaline which kills my libido", 
                "upvotes": 3, 
                "url": "https://www.reddit.com/r/Supplements/comments/12f13il/comment/jiuvzvs/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button"},
                {"comment_body": "Creatine or betaine anhydrous for strength. Peak 02 performance, very good nitric oxide that actually fuckin works. L carnatine and CLA (which takes up to 4-6 months to see results, for me atleast. Hydroxycut w/ no caffine on a diet honestly did me good, but it was hard on the body. Pro biotics. Fish oil. Castor oil for the skin (very noticeable if you want to glow. Night shred by alpha lion actually has been working believe it or not. Vitamin D , zinc.", 
                "upvotes": 10, 
                "url": "https://www.reddit.com/r/Supplements/comments/12f13il/comment/jfig5bm/?utm_source=share&utm_medium=web3x&utm_name=web3xcss&utm_term=1&utm_content=share_button"}
            ]
    }
    
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps(reddit_results)
    }