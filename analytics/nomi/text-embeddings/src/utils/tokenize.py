import requests
from bs4 import BeautifulSoup
import pandas as pd
import tiktoken
import re
import string


def strip_punctuation_and_emoji(text):
    # This pattern will find all word characters (alphanumeric and underscore)
    emoji_pattern = re.compile("[\W]+", re.UNICODE)
    text = emoji_pattern.sub(r'', text)
    # This will remove punctuation
    text = text.translate(str.maketrans('', '', string.punctuation))
    return text


def tokenize_blog(url: str) -> pd.DataFrame:
    print(f"Tokenizing {url}...")
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    # Find the title of the article
    title = soup.find('h1').text

    # Define the DataFrame
    df = pd.DataFrame(columns=['title', 'heading', 'content'])

    # Find all headers and paragraphs in the body
    content_tags = soup.find_all(
        ['h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'ul', 'li', 'img'])

    # Initialize a tokenizer
    enc = tiktoken.encoding_for_model("gpt-4")

    data = []

    # construct df splitting up content of article by section
    current_section_title = ""
    current_section_i = 0
    content_buffer = ""
    tokens_count = 0
    for tag in content_tags:
        text_content = tag.text if tag.name != 'img' else tag['alt']

        # Preprocess text content
        text_content = strip_punctuation_and_emoji(text_content)
        text_content = re.sub('\s+', ' ', text_content).strip()

        if tag.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
            # If there is content in the buffer, save it to the DataFrame
            if content_buffer:
                data.append({'title': title,
                            'heading': f"{current_section_title}-{current_section_i}",
                             'content': content_buffer})
                current_section_i += 1
            current_section_title = text_content
            content_buffer = ""
            tokens_count = 0
        else:
            tokens = list(enc.encode(text_content))
            # If adding this text exceeds the max limit
            if tokens_count + len(tokens) > 1500:
                data.append({'title': title,
                            'heading': f"{current_section_title}-{current_section_i}",
                             'content': content_buffer})
                current_section_i += 1
                content_buffer = text_content  # Start new content buffer with current tag text
                # Start new tokens count with current tag tokens
                tokens_count = len(tokens)
            else:
                content_buffer += ' ' + text_content  # Add current tag text to content buffer
                # Add current tag tokens to tokens count
                tokens_count += len(tokens)

    # Add last content buffer
    if content_buffer:
        data.append({'title': title,
                    'heading': f"{current_section_title}-{current_section_i}",
                     'content': content_buffer})

    # Add last content buffer
    data.append({'title': title,
                'heading': f"{current_section_title}-{current_section_i}",
                 'content': content_buffer})

    df = pd.DataFrame(data)

    # Create a new column for token counts & set index
    df['tokens'] = df['content'].apply(lambda x: len(list(enc.encode(x))))
    df = df[df['tokens'] != 0]

    print(df.head())
    print(f"Total rows in data: {len(df)}")

    return df
