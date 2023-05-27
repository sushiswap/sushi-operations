#!/bin/bash

# Assuming your text file is called urls.txt
while read -r url
do
  make run-tokenize url="$url"
done < content-to-scrape.txt