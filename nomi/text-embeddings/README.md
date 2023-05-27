# Nomi Ai Text Embeddings

Uses text embeddings from various blog / content sources to give context to chat-gpt when prompting it with questions.

## Tokenize Content

1. Add urls line by line to `content-to-scrape.txt`
2. Run `./run-tokenize.sh` to tokenize all of the content on each url, will be saved off in `./data/tokenized-sets`
3. Run `make run-consolidate` to consolidate all of the tokenized data into a single data set.

## Prompting GPT

`make run-prompt`
