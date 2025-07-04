# main.py
from modules.sheet_loader import load_sheets
from modules.sqlite_loader import load_into_sqlite
from modules.query_cleaner import clean_sql_query, print_sql
from modules.logging_config import configure_logging
from modules.prompts import SYSTEM_PROMPT_TEMPLATE, ANSWER_PROMPT_TEMPLATE
from modules.llm_config import get_llm
from langchain_community.utilities import SQLDatabase
from langchain_community.tools.sql_database.tool import QuerySQLDataBaseTool
from langchain.chains import create_sql_query_chain
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from operator import itemgetter
import tiktoken


configure_logging()


def main():
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
    execute_query = QuerySQLDataBaseTool(db=db)
    answer_prompt = PromptTemplate.from_template(ANSWER_PROMPT_TEMPLATE)
    rephrase_answer = answer_prompt | llm | StrOutputParser()

    select_table = lambda x: table_details

    print("\n===== TABLE INFO PASSED TO LLM =====\n")
    print(table_details)
    print("\n====================================\n")
    print("\U0001F7E2 Start chatting (type 'exit' to quit)")

    while True:
        user_input = input("\nUser: ").strip()
        if user_input.lower() in {"exit", "quit"}:
            print("\U0001F44B Exiting.")
            break

        try:
            prompt_str = SYSTEM_PROMPT_TEMPLATE.format(
                input=user_input, table_info=table_details, top_k="5"
            )
            enc = tiktoken.get_encoding("cl100k_base")
            input_tokens = len(enc.encode(prompt_str))

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

            response = chain_with_result_check.invoke({
                "question": user_input,
                "messages": [],
                "table_info": table_details
            })

            output_tokens = len(enc.encode(str(response)))
            print(f"\nAI: {response}")
            print(f"\n[Token usage] Input: {input_tokens} tokens | Output: {output_tokens} tokens\n")

        except Exception as e:
            print(f"\u26A0\uFE0F Error: {e}")


if __name__ == "__main__":
    main()
