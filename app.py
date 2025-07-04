from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from modules.sheet_loader import load_sheets
from modules.sqlite_loader import load_into_sqlite
from modules.query_cleaner import clean_sql_query, print_sql
from modules.logging_config import configure_logging
from modules.prompts import SYSTEM_PROMPT_TEMPLATE, ANSWER_PROMPT_TEMPLATE
from modules.llm_config import get_llm
from langchain_community.utilities import SQLDatabase
from langchain_community.tools import QuerySQLDatabaseTool
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
import tiktoken
import requests

app = FastAPI()

# WhatsApp settings
VERIFY_TOKEN = "12345"
ACCESS_TOKEN = "EAARZAswajqEkBPCskDRFvYhm7PoCb7DW7qlfpyZAGWApjkc7UXQ8G79iPJ6R9w3NSN9Mq3bcB357HfT0he95vEb6zjeTWPUfJAGZBqQ3QlK9e79Y6Myh9570JVlTRK16sHs5dhRjlYmRUT3sBBbqybaxAT8jZA0al6GjTH88WdLWZCNmakawNJdWb25wESXbCFsdcJJycSu6aNOJKFZBToKBcDvj3s0BX3ZBwMuZBJB7ij6cDQZDZD"
PHONE_NUMBER_ID = "624292667445289"

# Initialize Kabaddi bot
configure_logging()
tables = load_sheets()
engine = load_into_sqlite(tables)
db = SQLDatabase(engine)
llm = get_llm()
table_details = db.get_table_info()

final_prompt = PromptTemplate(
    input_variables=["input", "table_info", "top_k"],
    template=SYSTEM_PROMPT_TEMPLATE
)

generate_query = create_sql_query_chain(llm, db, prompt=final_prompt, k=None)
execute_query = QuerySQLDatabaseTool(db=db)
answer_prompt = PromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)
rephrase_answer = answer_prompt | llm | StrOutputParser()

select_table = lambda x: table_details

chain_with_result_check = (
    RunnablePassthrough.assign(table_info=select_table)
    | RunnablePassthrough.assign(
        raw_query=generate_query,
        query=generate_query | RunnableLambda(clean_sql_query)
    )
    | RunnableLambda(print_sql)
    | RunnablePassthrough.assign(result=itemgetter("query") | execute_query)
    | RunnableLambda(lambda x: (
        "This information is not available in the database."
        if not x["result"].strip()
        else rephrase_answer.invoke({
            "question": x["question"],
            "query": x["query"],
            "result": x["result"]
        })
    ))
)

# ✅ Kabaddi Bot API
class QuestionRequest(BaseModel):
    question: str

@app.post("/ask")
def ask_question(request: QuestionRequest):
    user_input = request.question.strip()
    if not user_input:
        raise HTTPException(status_code=400, detail="Question cannot be empty.")
    try:
        prompt_str = SYSTEM_PROMPT_TEMPLATE.format(
            input=user_input, table_info=table_details, top_k="5"
        )
        enc = tiktoken.get_encoding("cl100k_base")
        input_tokens = len(enc.encode(prompt_str))

        response = chain_with_result_check.invoke({
            "question": user_input,
            "messages": [],
            "table_info": table_details
        })

        output_tokens = len(enc.encode(str(response)))
        return {
            "answer": response,
            "token_usage": {
                "input": input_tokens,
                "output": output_tokens
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ✅ WhatsApp Verification Route
@app.get("/webhook")
async def verify_webhook(request: Request):
    params = dict(request.query_params)
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return int(challenge)
    else:
        return {"status": "error", "message": "Verification failed"}

# ✅ WhatsApp Webhook Route
@app.post("/webhook")
async def receive_message(request: Request):
    body = await request.json()
    print("Incoming Message:", body)

    try:
        phone_number = body['entry'][0]['changes'][0]['value']['messages'][0]['from']
        message_text = body['entry'][0]['changes'][0]['value']['messages'][0]['text']['body']
    except Exception as e:
        print("Error parsing message:", e)
        return {"status": "ok"}

    # Call Kabaddi bot
    try:
        response = chain_with_result_check.invoke({
            "question": message_text,
            "messages": [],
            "table_info": table_details
        })
    except Exception as e:
        response = f"Error: {e}"

    send_whatsapp_reply(phone_number, response)
    return {"status": "success"}

# ✅ Send WhatsApp Reply
def send_whatsapp_reply(phone_number, message):
    url = f"https://graph.facebook.com/v17.0/{PHONE_NUMBER_ID}/messages"
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "text": {"body": message}
    }
    response = requests.post(url, headers=headers, json=payload)
    print("WhatsApp API Response:", response.json())
