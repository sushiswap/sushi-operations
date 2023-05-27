import pandas as pd
import numpy as np
import tiktoken
import openai
import os
from utils.token_embeddings import order_by_similarity
from utils.config import OPEN_API_KEY

COMPLETIONS_MODEL = "gpt-3.5-turbo"

COMPLETIONS_API_PARAMS = {
    # We use temperature of 0.0 because it gives the most predictable, factual answer.
    "temperature": 0.5,
    "top_p": 0.5,
    "max_tokens": 2000,
    "model": COMPLETIONS_MODEL,
}

MAX_SECTION_LEN = 2000
SEPARATOR = "\n* "
ENCODING = "gpt2"  # encoding for text-davinci-003

encoding = tiktoken.get_encoding(ENCODING)
separator_len = len(encoding.encode(SEPARATOR))

openai.api_key = OPEN_API_KEY


def construct_prompt(question: str, context_embeddings: dict, df: pd.DataFrame) -> str:
    """
    Fetch relevant
    """
    most_relevant_document_sections = order_by_similarity(
        question, context_embeddings)

    chosen_sections = []
    chosen_sections_len = 0
    chosen_sections_indexes = []

    for _, section_index in most_relevant_document_sections:
        # Add contexts until we run out of space.
        document_section = df.loc[section_index]

        chosen_sections_len += document_section.tokens + \
            separator_len

        if chosen_sections_len > MAX_SECTION_LEN:
            break

        chosen_sections.append(
            SEPARATOR + document_section.content.replace("\n", " "))
        chosen_sections_indexes.append(str(section_index))

    # Useful diagnostic information
    print(f"Selected {len(chosen_sections)} document sections:")
    print("\n".join(chosen_sections_indexes))

    return chosen_sections, chosen_sections_len


def answer_with_gpt(
    query: str,
    df: pd.DataFrame,
    document_embeddings: dict[(str, str), np.array],
    show_prompt: bool = False
) -> str:
    messages = [
        # {"role": "system", "content": "You are a sushi chatbot, only answer the question by using the provided context. If your are unable to answer the question using the provided context, say 'I don't know'"}
        {"role": "system", "content": "You are a defi wizard with knowledge on all of defi dedicated to helping with sushiswap chat support, answer the question using the provided context as help. It is okay for you to also use out of context knowledge to help you answer the prompt."}
    ]
    prompt, section_length = construct_prompt(
        query,
        document_embeddings,
        df
    )
    if show_prompt:
        print(prompt)

    context = ""
    for article in prompt:
        context = context + article

    context = context + '\n\n --- \n\n + ' + query

    messages.append({"role": "user", "content": context})
    response = openai.ChatCompletion.create(
        messages=messages,
        **COMPLETIONS_API_PARAMS
    )

    return '\n' + response['choices'][0]['message']['content'], section_length
