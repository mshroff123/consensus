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

client = boto3.client('kendra')
lambda_client = boto3.client('lambda')
dynamodb = boto3.resource('dynamodb')


questions_table = dynamodb.Table('6998-questions-db')
comments_table = dynamodb.Table('6998-comments-db')




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
    time.sleep(.1)   

def get_key_claims(comments, llm_resp_array):
     # init pinecone
    PINECONE_API_KEY_TWO = 'a912715a-99f3-4c4d-8538-4f8a98fc4b0f'
    PINECONE_ENV_TWO = 'northamerica-northeast1-gcp'

    comments = comments
    llm_resp_array = llm_resp_array
    

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

    while True:
        var = wait_on_index(index_name)
        if var:
            break
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
        xc = index.query(xq, top_k=10, include_metadata=True)
        for result in xc['matches']:
            if result['score'] < .75:
                break

            if claim in key_claims_hash:
               claims_list = key_claims_hash[claim]
               claims_list.append(result['metadata']['text'])
               key_claims_hash[claim] = claims_list
            else:               
                key_claims_hash[claim] = [result['metadata']['text']]
            # query dynamo db table to get all related questions

    pinecone.delete_index(index_name)
    print("FINAL TIME")
    e = datetime.datetime.now()
    print(e)

      # return search results and headers
    return key_claims_hash


def lambda_handler(event, context):
    # TODO implement
    print(event)
    query = event["queryStringParameters"]["q"]
    
    #TIME
    start_time = time.time()

    # create the query vector
    # xq = model.encode(query).tolist()

    # now query
    e = datetime.datetime.now()
    questions = []

    PINECONE_API_KEY = '974f9758-d34f-4083-b82d-a05e3b1742ae'
    PINECONE_ENV = 'us-central1-gcp'

    pinecone.init(
        api_key=PINECONE_API_KEY,
        environment=PINECONE_ENV
    )


    index = pinecone.Index("semantic-search-6998")

    openai_embed = OpenAIEmbeddings(openai_api_key=openai.api_key)

    xq = openai_embed.embed_query(query)

    # now query
    e = datetime.datetime.now()
    questions = []
    xc = index.query(xq, top_k=10, include_metadata=True)
    # xc = index.query(xq, top_k=3, include_metadata=True)

    #print(e)

    ex = datetime.datetime.now()

    total_tokens = 0

    
    for result in xc['matches']:
        if result['score'] < .5:
            break

        response = questions_table.query(
            IndexName='title-index',
            KeyConditionExpression=Key('title').eq(result['metadata']['text'])
        )

        print(result['metadata']['text'])
        # query dynamo db table to get all related questions

        for item in response['Items']:
            questions.append(item['id'])

    # query dynamo db to get all comments

    
    #TIME
    
    end_time = time.time()
    time_diff = end_time - start_time

    print("PINECONE #1: {:.3f} seconds".format(time_diff))
    
    start_time = time.time()
    
    comments = []


    totalTokensOver = False

    for result in questions:
        response = comments_table.query(
            IndexName='parent_id-index',
            KeyConditionExpression=Key('parent_id').eq(result)
        )



        for item in response['Items']:
            num_tokens = num_tokens_from_string(item['body'],"cl100k_base")
            total_tokens +=  num_tokens

            if total_tokens > 3600:
                totalTokensOver = True
                break

            comments.append(item['body'])
      
        if totalTokensOver:
            break


    print(ex)
    x = datetime.datetime.now()

    print(len(comments))
    comments_df = pd.DataFrame({'body': comments})
    loader = DataFrameLoader(comments_df, page_content_column="body")
    documents = loader.load()

    text_splitter = CharacterTextSplitter(chunk_size=10000, chunk_overlap=500)
    texts = text_splitter.split_documents(documents)
    docs = []
    counter = 0
    content = ""
    content_array = []
    for text in texts:
        if counter < 20:
            counter += 1
            content += text.page_content
            content += '\n'
        else:
            counter = 0
            content_array.append(content)
            content = ""
            content += text.page_content
            content += '\n'
    content_array.append(content)
    docs = [Document(page_content=t) for t in content_array]
    # query langchain for questions to get the desired result

    #TIME
    
    end_time = time.time()
    time_diff = end_time - start_time

    print("DYNAMO DB + DOC SPLITTER: {:.3f} seconds".format(time_diff))
    
    start_time = time.time()    


    prompt_template_p1 = f"Given the following Reddit comments in response to the search query {query}, "


    #prompt_template_p2 = """identify the most frequently occuring key claims (2-6 claims) found in the comments and output it as a list of key claims."
    #prompt_template_p2 = """list the key claims for each comment in the format [claim1,claim2, etc.]"""
    #prompt_template_p2 = """list the key claims for each comment. If a 
    #comment makes an irrelevant or troll claim in response to the question ignore it. 

    prompt_template_p2 = """identify the most frequently occurring key claims (2-6 claims) found in the comments 
    that directly answer the search query. Output a list of key claims."

    ```{text}```

    """

    prompt_template_formatted = prompt_template_p1 + prompt_template_p2
    PROMPT = PromptTemplate(template=prompt_template_formatted, input_variables=["text"])



    combine_template_p1 = f"The following are the relevant key claims extracted from reddit comments made in response to the question {query} , "
    combine_template_p2 = """ Generate a list of brief explanations each separated by # for each of the most commonly occuring claims (up to 6 claims) 
    that represents the wide array of opinions made across all the key claims provided below: 

    ```{text}```
    """

    combine_template =  combine_template_p1 + combine_template_p2

    combine_prompt = PromptTemplate(
        input_variables=["text"],
        template=combine_template,
    )

    chain = load_summarize_chain(llm=OpenAI(temperature=0, batch_size=60) ,chain_type="map_reduce", map_prompt=PROMPT, combine_prompt=combine_prompt)
    llm_resp = chain.run(docs)
    print(llm_resp)


    #llm_resp = llm_resp[2:]

    if llm_resp[-1] == '#':
        llm_resp = llm_resp[:len(llm_resp) - 2]
    llm_resp_array = llm_resp.split('#')
    print(llm_resp_array)

    '''
    start_array_index = 0
    end_array_index = 0

    for i in range(len(llm_resp)):
        if llm_resp[i] == '[':
            start_array_index = i
        if llm_resp[i] == ']':
            end_array_index = i

    print(llm_resp)
    llm_resp = llm_resp[start_array_index + 1: end_array_index]

    llm_resp_array = llm_resp.split(',')
    '''

    # llm_resp_array = llm_resp_json[0]["claims"]

    
    end_time = time.time()
    time_diff = end_time - start_time

    print("LLM: {:.3f} seconds".format(time_diff))
    
    #TIME
    start_time = time.time()

    # key_claims_hash = get_key_claims(comments, llm_resp_array)


    
    input_params = {
        "comments": comments,
        "llm_resp_array" : llm_resp_array
    }


    '''
    # call other lambda
    response = lambda_client.invoke(
        FunctionName="arn:aws:lambda:us-east-1:214763411219:function:comments-relevance",
        InvocationType="RequestResponse",
        Payload=json.dumps(input_params)
    )

    print(response['Payload'])

    response_payload = json.load(response['Payload'])
    print(response_payload)
    key_claims_hash = response_payload['body']

    total_len = 0
    relevance_score = {}
    
    for key, value in key_claims_hash.items():
        relevance_score[key] = len(value)
        total_len += len(value)
    
    relevance_score = {k: v/total_len for k, v in relevance_score.items()}

    key_claims = []
    for claim in llm_resp_array:
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
    
    end_time = time.time()
    time_diff = end_time - start_time

    print("PINECONE #2 KEY CLAIM EXTRACTION: {:.3f} seconds".format(time_diff))


    '''
    # return search results and headers
    return {
        'statusCode': 200,
        'headers': {
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'OPTIONS,GET',
        },
        'body':  json.dumps(input_params)
    }




def num_tokens_from_string(string: str, encoding_name: str) -> int:
    """Returns the number of tokens in a text string."""
    encoding = tiktoken.get_encoding(encoding_name)
    num_tokens = len(encoding.encode(string))
    return num_tokens