import json
import openai
import os
import pinecone
import pandas as pd
from langchain.document_loaders import DataFrameLoader
from langchain.llms import OpenAI
from langchain.chains.question_answering import load_qa_chain
from langchain.chains.summarize import load_summarize_chain
from langchain.prompts import PromptTemplate
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.text_splitter import CharacterTextSplitter
from langchain.docstore.document import Document
import datetime
import boto3
from boto3.dynamodb.conditions import Key
import tiktoken
from tqdm.auto import tqdm
import time


openai.api_key = "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"
os.environ["OPENAI_API_KEY"] = "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"

def wait_on_index(index: str):
  """
  Takes the name of the index to wait for and blocks until it's available and ready.
  """
  ready = False
  while not ready: 
    try:
      desc = pinecone.describe_index(index)
      if desc[7]['ready']:
        return True
    except pinecone.core.client.exceptions.NotFoundException:
      # NotFoundException means the index is created yet.
      pass
    time.sleep(1)   

def lambda_handler(event, context):
     # init pinecone
    PINECONE_API_KEY_TWO = 'a912715a-99f3-4c4d-8538-4f8a98fc4b0f'
    PINECONE_ENV_TWO = 'northamerica-northeast1-gcp'


    body = json.loads(event['body'])
    print(body)
    comments = body['comments']
    llm_resp_array = body['llm_resp_array']
    

    pinecone.init(
        api_key=PINECONE_API_KEY_TWO,
        environment=PINECONE_ENV_TWO
    )

    batch_size = 128

    index_name = 'semantic-search-relevant-comments'

    # only create index if it doesn't exist
    if index_name not in pinecone.list_indexes():
        pinecone.create_index(
            name=index_name,
            dimension=1536,
            metric='cosine'
        )

        wait_on_index(index_name)
        # now connect to the index
    print('done creating index')
    index = pinecone.Index(index_name)
    print('connected to index')

    # upload comments to pinecone
    for i in tqdm(range(0, len(comments), batch_size)):
        # find end of batch
        i_end = min(i + batch_size, len(comments))
        # create IDs batch
        ids = [str(x) for x in range(i, i_end)]
        # create metadata batch
        metadatas = [{'text': text} for text in comments[i:i_end]]
        # create embeddings
        # xc = model.encode(questions[i:i_end])
        openai_embed = OpenAIEmbeddings(openai_api_key=openai.api_key)

        xc = openai_embed.embed_documents(comments[i:i_end])
        # create records list for upsert
        records = []
        for i in range(len(ids)):
            record = (ids[i], xc[i], metadatas[i])
            records.append(record)

        # upsert to Pinecone
        print("uploading")
        index.upsert(vectors=records)

    # semantic search comments now on key claims
    key_claims_hash = {}
    for claim in llm_resp_array:
        # get 5 most relevant comments
        openai_embed = OpenAIEmbeddings(openai_api_key=openai.api_key)
        xq = openai_embed.embed_query(claim)
        xc = index.query(xq, top_k=20, include_metadata=True)
        for result in xc['matches']:
            if result['score'] < .85:
                break
            if claim in key_claims_hash:
               claims_list = key_claims_hash[claim]
               claims_list.append(result['metadata']['text'])
               key_claims_hash[claim] = claims_list
            else:               
                key_claims_hash[claim] = [result['metadata']['text']]
            # query dynamo db table to get all related questions

    # pinecone.delete_index(index_name)

    total_len = 0
    relevance_score = {}
    
    for key, value in key_claims_hash.items():
        relevance_score[key] = len(value)
        total_len += len(value)
    
    relevance_score = {k: (v*100)//total_len for k, v in relevance_score.items()}

    key_claims = []
    for claim in key_claims_hash.keys():
        claim_response = {}
        claim_response["claim"] = claim
        claim_response["relevance_score"] = relevance_score[claim]
        claim_response["supporting_comments"] = key_claims_hash[claim]
        key_claims.append(claim_response)

    search_results = {
        "search_id": str(len(comments)),
        "summary": "",
        "key_claims": key_claims
    }
    

    print("FINAL TIME")
    e = datetime.datetime.now()
    print(e)

      # return search results and headers
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': '*',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
        },
        'body': json.dumps(search_results)
    }