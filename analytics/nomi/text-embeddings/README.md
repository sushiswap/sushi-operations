# Nomi Ai Text Embeddings

Uses text embeddings from various blog / content sources to give context to chat-gpt when prompting it with questions.

## Tokenize Content

1. Add urls line by line to `content-to-scrape.txt`
2. Run `./run-tokenize.sh` to tokenize all of the content on each url, will be saved off in `./data/tokenized-sets`
3. Run `make run-consolidate` to consolidate all of the tokenized data into a single data set.

## Prompting GPT

`make run-prompt`

### Context

There are 2 directories in `/data` that need to be created: `full-tokenized-sets`, `tokenized-sets`. Running the `run-tokenize.sh` script will pull all the content text from blog posts and sushi academy urls, saving off each into a csv. The content/text is being separated by the main heading and all subsequent headings.

Step 3 then consolidates all of these tokenized sets into a single dataframe and saves it off as a csv. Then we running the gpt prompt will use that file, create openai embeddings from it, and serve answers to prompts using the text embeddings as context.
