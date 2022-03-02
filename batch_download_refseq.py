#!/usr/bin/env python3
# batch_download_refseq.py v0.5 - upon failure, downloads will now retry up to a maximum of 3 times 
# Batch downloads RefSeq sequences classified under a specific taxonomic group
# Retmax = 500 by default

import os
import argparse
import re
import requests
import time

def main():
    parser = argparse.ArgumentParser(description="Downloads RefSeq sequences under a user-defined set of taxonomic groups in batches of 500")
    parser.add_argument("i", help = "specify taxid of taxonomic group")
    parser.add_argument("n", help = "specify name of taxonomic group")
    parser.add_argument("-o", "--output_directory", help = "specify output directory of downloaded sequence files") # default = $DB_NAME/sequences
    parser.add_argument("-k", "--api_key", help = "specify NCBI API key (optional)", default = None)
    parser.add_argument("-v", "--verbose", help = "toggles verbose mode on", action = "store_true")
    args = parser.parse_args()

    db = "nucleotide"
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    query_taxid = args.i
    query_name = args.n
    query = f"txid{query_taxid}[Organism]+AND+RefSeq[filter]+AND+complete genome[TI]"
    ext = f"esearch.fcgi?db={db}&term={query}&usehistory=y"
    if args.api_key != None:
        ext += f"&api_key={args.api_key}"
    url = base + ext
    output = get_esearch_out(url, args.verbose)
    if output is None:
        print(f"Failed to obtain search results for {query_name} (taxid {query_taxid})")
        print("Please retry later.")
        exit()

    p1 = re.compile(r"<WebEnv>(\S+)</WebEnv>")
    p2 = re.compile(r"<QueryKey>(\d+)</QueryKey>")
    p3 = re.compile(r"<Count>(\d+)</Count>")
    m1 = p1.search(output.text).group()
    m2 = p2.search(output.text).group()
    m3 = p3.search(output.text).group()
    web_env = get_substring(m1, ">", "<")
    key = get_substring(m2, ">", "<")
    count = get_substring(m3, ">", "<")

    print(f"Downloading {count} {query_name} (taxid: {query_taxid}) RefSeq sequences in batches of 500")
    with open(os.path.join(args.output_directory, f"{query_name}_{query_taxid}.fa"), "w") as w:
        retmax = 500
        for i in range(0, int(count), retmax):
            efetch_url = base + f"efetch.fcgi?db={db}&WebEnv={web_env}"
            efetch_url += f"&query_key={key}&retstart={i}"
            efetch_url += f"&retmax={retmax}&rettype=fasta&retmode=text"
            if args.api_key != None:
                efetch_url += f"&api_key={args.api_key}"
            efetch_out = get_efetch_out(efetch_url, args.verbose)
            if efetch_out is None:
                print(f"Max download retries reached for {efetch_url} - please retry later")
                continue
            w.write(efetch_out.text)
    print(f"Download complete for {query_name} (taxid: {query_taxid})")

def get_substring(string, c1, c2):
    idx1 = string.index(c1)
    idx2 = string.index(c2, 1)
    new_string = string[idx1+1:idx2]
    return new_string

def sleep(timeout, retry=3):
    def decorator(func):
        def _wrapper(*args, **kwargs):
            retries = 0
            while retries < retry:
                try:
                    value = func(*args, **kwargs)
                    if value != None:
                        return value
                except Exception as e:
                    time.sleep(timeout)
                    retries += 1
            return None
        return _wrapper
    return decorator

@sleep(3)
def get_esearch_out(esearch_url, v):
    try:
        output = requests.get(esearch_url)
        return output
    except Exception as e:
        if v:
            print(f"Failed to access {esearch_url} due to {e}\n")
            print("Retrying...")
        raise e

@sleep(3)
def get_efetch_out(efetch_url, v):
    try:
        efetch_out = requests.get(efetch_url)
        return efetch_out
    except requests.exceptions.ChunkedEncodingError as e:
        if v:
            print(f"Failed to download from {efetch_url} due to {e}\n")
            print("Retrying...")
        raise requests.exceptions.ChunkedEncodingError

if __name__ == "__main__":
    main()