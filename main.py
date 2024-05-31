import uvicorn
import schemas
import pinecone
import jwt
import requests
import json
from general_utils import *
from db_utils import *

from fastapi import FastAPI, status,Depends,Header
from fastapi.responses import JSONResponse
from fastapi import Depends, Request

from apscheduler.schedulers.background import BackgroundScheduler

from langchain.embeddings import HuggingFaceEmbeddings
import logging
from auth.auth_bearer import JWTBearer
from auth.auth_handler import signJWT, decodeJWT
from fastapi.middleware.cors import CORSMiddleware
from langchain.embeddings import OpenAIEmbeddings
import openai
from email_templates import approval_email_body, user_login_email_body, verification_email_body
from starlette.middleware.trustedhost import TrustedHostMiddleware


JWT_SECRET = "CompitativeAI"

app = FastAPI()
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])


load_dotenv()

sender_email = os.getenv('email_username')
sendGridApiKey = os.getenv('sendGridApiKey')
verification_subject = os.getenv('subject_verification')
approval_Subject = os.getenv("subject_approval")
user_login_Subject = os.getenv("subject_user_login")
daniel_email = os.getenv("daniel_email")

open_ai_Api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = os.getenv("OPENAI_API_KEY")

API_KEY_FOR_EMAIL_CHECK = os.getenv("API_KEY_FOR_EMAIL_CHECK")


# Setup the custom logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
formatter = logging.Formatter(
    '%(asctime)s:%(name)s:%(levelname)s:%(message)s:%(funcName)s')
file_handler = logging.FileHandler('compitition.log')
file_handler.setFormatter(formatter)
logger.addHandler(file_handler)


origins = ["*"]
app.add_middleware(
                   CORSMiddleware, 
                   allow_origins=origins,
                   allow_credentials=True, 
                   allow_methods=["*"], 
                   allow_headers=["*"]
                )


# Connecting the Database
def db():
    try:
        cursor, conn = connect_DB()
        logger.info("Database Connection Successful")   
        return cursor, conn
    except Exception as ex:
        logger.critical(f"Database Connection Error: {str(ex)}")    


# Scheduling the Number of Query Updating
try:
    cursor, conn = db()
    scheduler = BackgroundScheduler()
    print("Running the Cron Job")
    scheduler.add_job(my_cron_job, trigger="cron",hour=00, minute=00, args=(cursor, conn))
    scheduler.start()
    print("Cron Job Done")
    logger.info("Scheduler init Done")
except Exception as ex:
    logger.critical(f"Scheduler init Error: {str(ex)}")


embed_fn = OpenAIEmbeddings(openai_api_key=open_ai_Api_key)


@app.get("/")
def startup():
    return JSONResponse("Welcome to CompetitionAI")


@app.post("/sign_up_new_user")
def sign_up_new_user(params: schemas.SignUp, request: Request):
    try:
        cursor, conn = db()
        generated_number = rand.randint(100000, 999999)

        if check_Email(params.email):
            if (params.code1 == 97) and (params.code2 == 199) and (params.code3 == 45) and (params.code4 == 888225):
                if send_email_for_verification(sender_email, params.email, verification_subject, verification_email_body, generated_number, sendGridApiKey) and add_verification_code(params.email, generated_number, cursor, conn):
                    client_ip = request.client.host
                    logger.info(f"Request Came From:  {str(client_ip)}")
                    logger.info(f"Signup very Successful For {str(params.email)}")
                    conn.close()
                    return JSONResponse(content={"message": "SignUp Successful!"}, status_code=status.HTTP_200_OK)
                else:
                    logger.info(f"Signup Failed For {str(params.email)}")
                    conn.close()
                    return JSONResponse(content={"message": "SignUp Failed!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Signup Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.post("/verify_sign_up")
def verify_sign_up(params: schemas.Verify_SignUp):
    
    try:
        cursor, conn = db()
        hashed_password = hash_password(params.password)

        if verify_Signup(params.email, params.verification_code, cursor, conn):
            if insert_User(params.first_name, params.last_name, params.email, hashed_password, params.company, params.position, cursor, conn):
                user_login_email_body1 = user_login_email_body.replace('aaaaaa', params.first_name +" "+ params.last_name)
                user_login_email_body1 = user_login_email_body1.replace('bbbbbb', params.email)
                user_login_email_body1 = user_login_email_body1.replace('cccccc', params.company)
                user_login_email_body1 = user_login_email_body1.replace('dddddd', params.position)
                send_user_login_email(sender_email, daniel_email, user_login_Subject, user_login_email_body1, sendGridApiKey)
                return JSONResponse(content={"message": "User Verified!",
                                            "Verified": True}, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={"message": "User could not Verify! Try Again",
                                            "Verified": False}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"message": "User could not Verify! Try Again",
                                            "Verified": False}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Signup Verification Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.post("/resend_verification_code")
def resend_verification_code(email:str):
    try:
        cursor, conn = db()
        generated_number = rand.randint(100000, 999999)
        if (add_verification_code(email, generated_number, cursor, conn)):
            send_email_for_verification(sender_email, email, verification_subject, verification_email_body, generated_number, sendGridApiKey)
            return JSONResponse(content={"message": "Verification Code Sent!"}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"message": "Verification Code not Sent"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Resend Verification Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)


@app.post("/login")
def login(params: schemas.Login):
    try:
        cursor, conn = db()
        hashed_password = hash_password(params.password)
        
        data = login_user(params.email, hashed_password, cursor)
        if not data:
            conn.close()
            return JSONResponse(content={"message": "Login Failed!"}, status_code=status.HTTP_200_OK)
        
        if data[0]:
            my_token = signJWT(data[0])
            if update_login_details(data[0], cursor, conn):

                logger.info(f"Login Successful For {str(params.email)}")
                conn.close()
                return JSONResponse(content={"message": "Login Successful!", "Token": my_token['access_token'].decode(), "UserID": data[0], "First Name": data[1], "Last Name": data[2], "Email": data[3], "Company": data[5], "Position": data[6], "Role": data[10]}, status_code=status.HTTP_200_OK)

            else:
                logger.info(f"Login Failed For {str(params.email)}")
                conn.close()
                return JSONResponse(content={"message": "Login Failed!"}, status_code=status.HTTP_200_OK)
        else:
            return JSONResponse(content={"message": "Login Failed!"}, status_code=status.HTTP_400_BAD_REQUEST)
    
    except Exception as ex:
        logger.critical(f"login Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.get("/get_users", dependencies=[Depends(JWTBearer())])
def get_users(validity:int):
    try:
        cursor, conn = db()
        data = get_specified_users(validity, cursor)
        conn.close()
        return JSONResponse(content={"message": "Data Extracted!", "Data": data}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Get User Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.get("/validate_user", dependencies=[Depends(JWTBearer())])
def validate_user(userid:int, email:str):
    try:
        cursor, conn = db()
        if update_validity(userid, cursor, conn):
            send_account_approval_email(sender_email, email, approval_Subject, approval_email_body, sendGridApiKey)
            conn.close()
            return JSONResponse(content={"message": "User Validated!"}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Request Failed!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Validating User Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.put("/add_query", dependencies=[Depends(JWTBearer())])
def add_query(vectorstore:str, query:str, request:Request, number_of_queries:int):
    
    try:
        cursor, conn = db()
        token = request.headers.get("Authorization").split()[1]
        user_id = jwt.decode(token,JWT_SECRET, algorithms=[os.environ.get('JWT_ALGORITHM')])
        userid = user_id.get('user_id')
        answer = select_store_and_perform_semantic_search(vectorstore, query, embed_fn)
        sources_and_response = parse_output(answer['source_documents'])

        number_of_queries = number_of_queries - 1
        
        if "I'm sorry" in answer['result']:
            return JSONResponse(content={"message": "Query Resolved!","Query": query, "Simple_Response": answer["result"] , "Source_Response": sources_and_response, "flag" : 0}, status_code=status.HTTP_200_OK)
        else:
            general_answer = make_response(answer["result"])
            # general_answer = answer["result"]
            if add_query_details(userid, query, general_answer, number_of_queries, sources_and_response, vectorstore ,cursor, conn):
                conn.close()
                return JSONResponse(content={"message": "Query Resolved!","Query": query, "Simple_Response": general_answer , "Source_Response": sources_and_response, "flag" : 1}, status_code=status.HTTP_200_OK)
            else:
                conn.close()
                return JSONResponse(content={"message": "Request Failed!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Query Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.get("/check_queries", dependencies=[Depends(JWTBearer())])
def query_check(request:Request):
    try:
        cursor, conn = db()
        token = request.headers.get("Authorization").split()[1]
        user_id = jwt.decode(token,JWT_SECRET, algorithms=[os.environ.get('JWT_ALGORITHM')])
        userid = user_id.get('user_id')
        data = check_queries(userid, cursor)

        if data["Number_of_Queries"] >= 1:
            conn.close()
            return JSONResponse(content={"message": "Valid!", "Data": data}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Invalid!",  "Data": data}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Query Check Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.delete("/delete_user", dependencies=[Depends(JWTBearer())])
def delete_user(user_id:int):
    try:
        cursor, conn = db()
        if user_deletion(user_id, cursor, conn):
            conn.close()
            return JSONResponse(content={"message": "User Deleted Successfully!"}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Request Failed!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Delete User Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.delete("/reject_user", dependencies=[Depends(JWTBearer())])
def user_reject(user_id:int):
    try:
        cursor, conn = db()
        if reject_user(user_id, cursor, conn):
            conn.close()
            return JSONResponse(content={"message": "User Rejected Successfully!"}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Request Failed!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Reject User Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.get("/get_history", dependencies=[Depends(JWTBearer())])
def get_history(vectorstore:str):
    
    try:
        cursor, conn = db()
        data = get_query_history(vectorstore, cursor)

        if data:
            conn.close()
            return JSONResponse(content={"message": "Data Retreived Successfully!", "Data" : data}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Data Not Found!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Get User History Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.get("/get_history_of_a_user", dependencies=[Depends(JWTBearer())])
def get_history_of_a_user(user_id:int):
    
    try:
        cursor, conn = db()
        data = get_user_query_history(user_id, cursor)

        if data:
            conn.close()
            return JSONResponse(content={"message": "Data Retreived Successfully!", "Data" : data}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Data Not Found!"}, status_code=status.HTTP_200_OK)
    except Exception as ex:
        logger.critical(f"Get User History Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)
    

@app.get("/get_db_usage_history", dependencies=[Depends(JWTBearer())])
def get_db_usage_history(timeline:int):
    try:
        cursor, conn = db()
        if timeline == 0:
            data = get_usage_of_db_without_timeline(cursor)
        else:
            data = get_usage_of_db_with_timeline(timeline, cursor)

        if data:
            conn.close()
            return JSONResponse(content={"message": "Data Retreived Successfully!", "Data" : data}, status_code=status.HTTP_200_OK)
        else:
            conn.close()
            return JSONResponse(content={"message": "Data Not Found!"}, status_code=status.HTTP_200_OK)

    except Exception as ex:
        logger.critical(f"Get DB Usage History Failed: {str(ex)}")
        return JSONResponse(content={"error": str(ex)}, status_code=status.HTTP_400_BAD_REQUEST)


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8290)