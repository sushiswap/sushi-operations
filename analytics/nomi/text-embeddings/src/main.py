import pandas as pd
import os
import argparse
from datetime import datetime
from utils.tokenize import tokenize_blog
from utils.token_embeddings import compute_doc_embeddings
from utils.gpt import answer_with_gpt


def tokenize(url: str) -> pd.DataFrame:
    df = tokenize_blog(url)
    return df


def start_live_session(df: pd.DataFrame):
    # compute document embeddings
    print("Computing doc embeddings...")
    df = df.set_index(['title', 'heading'])

    # Find the duplicate indexes
    duplicated_indexes = df.index.duplicated(keep='first')

    # Keep only the non-duplicated indexes
    df = df[~duplicated_indexes]

    document_embeddings = compute_doc_embeddings(df)

    while True:
        user_prompt = input("Enter your prompt: ")
        if user_prompt.lower() == "exit":
            break
        else:
            print(f"\n Prompting: {user_prompt} \n")
            try:
                response, sections_tokens = answer_with_gpt(
                    user_prompt, df, document_embeddings)
                print(response)
            except Exception as e:
                print(f"Error occurred while prompting GPT: {e}")
                continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--tokenize', nargs='*',
                        help="Tokenize the URL content.")
    parser.add_argument('-c', '--consolidate', action='store_true',
                        help="Consolidate all tokenized CSV files.")
    parser.add_argument('-p', '--prompt', action='store_true',
                        help="Start a live session.")
    args = parser.parse_args()

    if args.tokenize is not None:
        dfs = []
        for url in args.tokenize:
            dfs.append(tokenize_blog(url))
        df = pd.concat(dfs)

        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")  # generates timestamp

        output_directory = './data/tokenized-sets/'
        # appends timestamp to filename
        output_filename = f'blog_{timestamp}.csv'

        df.to_csv(output_directory + output_filename, index=False)

    elif args.consolidate:
        dfs = []
        for file in os.listdir('./data/tokenized-sets/'):
            if file.endswith('.csv'):
                dfs.append(pd.read_csv('./data/tokenized-sets/' + file))

        df = pd.concat(dfs)
        df = df.drop_duplicates()  # remove duplicates

        output_directory = './data/full-tokenized-sets/'
        output_filename = 'full_tokenized_sets_data.csv'

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        df.to_csv(output_directory + output_filename, index=False)

    elif args.prompt:
        # Load the dataframe
        df = pd.read_csv(
            './data/full-tokenized-sets/full_tokenized_sets_data.csv')

        # start the live session
        start_live_session(df)
