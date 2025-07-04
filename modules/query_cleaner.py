import re
import logging

# def clean_sql_query(text: str) -> str:
#     block_pattern = r"```(?:sql|SQL|SQLQuery|mysql|postgresql)?\\s*(.*?)\\s*```"
#     text = re.sub(block_pattern, r"\\1", text, flags=re.DOTALL)
#     prefix_pattern = r"^(?:SQL\\s*Query|SQLQuery|MySQL|PostgreSQL|SQL)\\s*:\\s*"
#     text = re.sub(prefix_pattern, "", text, flags=re.IGNORECASE)
#     sql_statement_pattern = r"(SELECT.*?;)"
#     match = re.search(sql_statement_pattern, text, flags=re.IGNORECASE | re.DOTALL)
#     if match:
#         text = match.group(1)
#     return re.sub(r'\\s+', ' ', text.strip())

import re


def clean_sql_query(text: str) -> str:
    # Remove SQL code blocks
    text = re.sub(r"```(?:sql|SQL|SQLQuery|mysql|postgresql)?\s*(.*?)\s*```", r"\1", text, flags=re.DOTALL)
    
    # Remove leading labels like "SQL:", "sqlite", "ite", etc.
    text = re.sub(r"^(?:sqlite|ite|SQL\s*Query|SQLQuery|MySQL|PostgreSQL|SQL)\s*:?[\s\\n]*", "", text.strip(), flags=re.IGNORECASE)
    
    # Normalize whitespace
    return re.sub(r'\s+', ' ', text.strip())

def print_sql(x):
    print("\\nLLM-generated SQL (raw):", x.get("raw_query"))
    print("Cleaned SQL:", x.get("query"))

    logging.info("User Question: %s", x.get("question", "N/A"))
    logging.info("Cleaned SQL: %s", x.get("query"))
    return x
