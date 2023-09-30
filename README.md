# Consensus Search

Consensus Search is a powerful search engine that leverages the wisdom of crowds to provide human, unbiased, and comprehensive answers to open-ended questions. By consolidating results from various discussion-based platforms such as Reddit, Quora, Stack Overflow, and Twitter, Consensus Search ensures users receive genuine insights from real users, instead of biased or sponsored content.

http://intelligent-search-frontend.s3-website-us-east-1.amazonaws.com 

## Features

- **Intelligent Search**: Aggregates and analyzes data from numerous discussion boards using engagement, relevance, and feedback data (upvotes, likes, views) available through APIs.
- **OpenAI GPT-3 Integration**: Performs sentiment analysis, summarization, and opinion grouping on the collected data, providing users with concise, relevant answers.
- **Opinion and Consensus Metrics**: Displays prevailing consensus using proprietary relevance percentages and groups opinions based on similar concepts.
- **Wide Range of Topics**: Covers a diverse array of topics such as medical, travel, general knowledge, tech, and reviews.

# Repository Contents

## Directories:
- **consensus-gpt**: Tools and scripts that utilize GPT for deriving a consensus from various inputs.
- **enhanced-summary**: Components that aim to produce or enhance summaries from data or articles.
- **gpt-search**: Implements GPT-based search functionalities.
- **gpt-summary**: Modules that leverage the GPT model to create or extract summaries.
- **gpt**: General utilities and scripts related to GPT.
- **raw-search**: Codebase for conducting unprocessed or 'raw' searches.
- **regular**: Standard implementations, potentially baseline features without enhancements.

## Key Files:
- **Dockerfile**: Instructions to build a Docker container for the Lynk application.
- **app.py**: Main application file, possibly the API or primary service entry point.
- **app_enhanced_summary.py**: Variant of the main app focusing on enhanced summary generation.
- **prev_version.py**: Legacy version of primary functionality.
- **raw_search_lambda.py**: Lambda function dedicated to raw search operations.
- **raw_search_lambda_pushshift.py**: Raw search lambda function, with integration for pushshift (Reddit data platform).
- **requirements.txt**: Lists the Python dependencies required for the project.




## Acknowledgements

- [OpenAI](https://www.openai.com/) for their GPT-3 API
- [PRAW (Python Reddit API Wrapper)](https://praw.readthedocs.io/)
- [Flask](https://flask.palletsprojects.com/) for the lightweight web framework
- All contributors and users of Consensus Search, helping us build a better search experience for everyone

