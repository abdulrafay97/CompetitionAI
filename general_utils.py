import hashlib
import os
import pinecone
import requests

from langchain.vectorstores import Pinecone
from langchain.chains import RetrievalQA
from langchain.chat_models import ChatOpenAI
from langchain import PromptTemplate

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import openai
import random as rand

from langchain.chat_models import ChatOpenAI
from langchain.embeddings import OpenAIEmbeddings
from langchain.chains import LLMChain, HypotheticalDocumentEmbedder
from langchain.prompts import PromptTemplate

def hash_password(password):
    input_bytes = password.encode('utf-8')
    sha256_object = hashlib.sha256()
    sha256_object.update(input_bytes)
    hashed_output = sha256_object.hexdigest()

    return hashed_output


def select_store_and_perform_semantic_search(vectorstore, query, embed_fn):
    if vectorstore == 'CMAC':
        return semantic_search("cmamd-1536-openai", embed_fn, query)
    elif vectorstore == 'CMAG':
        return semantic_search("cmag-1536-openai", embed_fn, query)
    elif vectorstore == 'ECG':
        return semantic_search("ecg-1536-openai", embed_fn, query)
    elif vectorstore == 'UKFS':
        return semantic_search("ukfs-1536-openai", embed_fn, query)
    elif vectorstore == 'USFTC':
        return semantic_search("usftc-1536-openai", embed_fn, query)


def semantic_search(index, embed_fn, query):
    pinecone.init(api_key = os.getenv("PINECONE_API_KEY"), environment = os.getenv("PINCONE_ENV"))
    index_name = index
    index = pinecone.Index(index_name)

    llm = ChatOpenAI(model="gpt-3.5-turbo-16k", openai_api_key="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", temperature=0.2)
    hyde_embed_fn = HypotheticalDocumentEmbedder.from_llm(llm, embed_fn, "web_search")

    vectordb_lg = Pinecone(index, hyde_embed_fn,"text")

    prompt_template = """
        You are a helpful Competition Law expert. Use the following pieces of context to answer the question at the end.
        Please give the answer in a very expressive way. So, A person can have the full context.
        If you don't know the answer, just say you don't know. DO NOT try to make up an answer.
        If the question is not related to the context, politely respond that you are tuned to only answer questions using information in the competition authority's public documents in the CompetitionAI database and suggest they try to rephrase the question.
        ((((Give a helpful answer in MarkDown Format))))
        Context: {context}
        Question: {question}
    """

    mprompt_url = PromptTemplate(
        template=prompt_template, input_variables=["context", "question"], validate_template=False)
    chain_type_kwargs = {"prompt": mprompt_url}

    qa = RetrievalQA.from_chain_type(
                                    llm=llm, 
                                    chain_type="stuff", 
                                    retriever=vectordb_lg.as_retriever(search_kwargs={"k": 4}),
                                    chain_type_kwargs=chain_type_kwargs,
                                    return_source_documents=True
                                )
    
    return qa({"query":query})


def parse_output(documents):
    lst = []
    for doc in documents:
        my_dict = {}
        my_dict['Source'] = doc.metadata['source']
        my_dict['Text'] = doc.page_content

        lst.append(my_dict)

    return lst


def check_Email(email):
    if (email == "rafayrana036@gmail.com") or (email == "hafizumair.ie@gmail.com"):
        return False
    else:
        return True
    

def make_response(answer):
    messages = [
        {"role": "system", "content": """You are trained to change the format of given context into HTML Markup."""},
        {"role": "user", "content": f"""Generate the Markup format for the given context. Context: {answer}"""}
    ]

    response = openai.ChatCompletion.create(
                        model="gpt-3.5-turbo-16k",
                        messages=messages,
                        n=1, 
                        stop=None, 
                        temperature=0.0)

    response_text = response.choices[0].message.content.strip()

    return response_text


def send_email_for_verification(sender_email, receiver_email, subject, email_body, generated_number, sendGridApiKey):
    
    email_body = email_body.replace("XXXXXX", str(generated_number))

    message = Mail(
        from_email = sender_email,
        to_emails = receiver_email,
        subject = subject,
        html_content = email_body
    )

    try:
        sg = SendGridAPIClient(sendGridApiKey)
        response = sg.send(message)
        return True
    except Exception as e:
        print(e)
        return False


def send_account_approval_email(sender_email, receiver_email, subject, email_body, sendGridApiKey):

    message = Mail(
        from_email = sender_email,
        to_emails = receiver_email,
        subject = subject,
        html_content = email_body
    )

    try:
        sg = SendGridAPIClient(sendGridApiKey)
        response = sg.send(message)
        return True
    except Exception as e:
        return False
    

def send_user_login_email(sender_email, receiver_email, subject, email_body, sendGridApiKey):
    
    message = Mail(
        from_email = sender_email,
        to_emails = receiver_email,
        subject = subject,
        html_content = email_body
    )

    try:
        sg = SendGridAPIClient(sendGridApiKey)
        response = sg.send(message)
        return True
    except Exception as e:
        return False
