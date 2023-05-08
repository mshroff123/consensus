import json
import boto3
import openai
import pinecone
import torch
from sentence_transformers import SentenceTransformer

client = boto3.client('kendra')
openai.api_key = "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"


def lambda_handler(event, context):
    # TODO implement
    query = event["queryStringParameters"]["q"]

    model = SentenceTransformer('all-MiniLM-L6-v2', device=device)
    model.save

    # init pinecone
    PINECONE_API_KEY = '974f9758-d34f-4083-b82d-a05e3b1742ae'
    PINECONE_ENV = 'us-central1-gcp'

    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENV
    )

    index = pinecone.Index("semantic-search-6998")

    # Sample Query
    query = "Best exercises for strengthening my wrists?"

    # create the query vector
    xq = model.encode(query).tolist()

    # now query
    xc = index.query(xq, top_k=3, include_metadata=True)
    for result in xc['matches']:
        print(f"{round(result['score'], 2)}: {result['metadata']['text']}")

    # return search results and headers
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
        },
        'body': []
    }

