import json
import praw

def formatted_query_comments(query):
    reddit = praw.Reddit(client_id='2z1kCNZ87wgQbs8k0fr5ew', client_secret='4V-jniLxhQvjiYZC3FgCYjEy5B27zA', user_agent='Consearch by maansishroff@gmail.com')

    # build reddit_results to be correctly formatted for API Gateway
    reddit_results = {"posts": []}
    
    # Search for posts related to the keyword
    posts = reddit.subreddit('all').search(query, limit=10, sort='relevance')
    
    # Loop over the posts that match the search query
    for post in posts:
        post_comments = {"comments": []}
        # search for comments related to the post
        post.comments.replace_more(limit=10)
        comments = post.comments.list()
        top_comments = sorted(comments, key=lambda c: c.score, reverse=True)[:5]
        
        # loop over the comments and add to the post_comments dictionary
        for comment in top_comments:
            if "thanks" not in comment.body.lower() or "thank you" not in comment.body.lower():
                post_comments["comments"].append({
                    "comment_body": comment.body, 
                    "comment_score": comment.score, 
                    "comment_url": post.url+comment.permalink})
        
        # add the post to reddit_results
        reddit_results["posts"].append({
            "post_title": post.title, 
            "post_score": post.score, 
            "post_url": post.url, 
            "comments": post_comments["comments"]})
    
    return reddit_results


def lambda_handler(event, context):

    query = event["queryStringParameters"]["q"]
    reddit_results = formatted_query_comments(query)
    
    return {
        "statusCode": 200,
        "headers": {
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "OPTIONS,GET"
        },
        "body": json.dumps(reddit_results)
    }