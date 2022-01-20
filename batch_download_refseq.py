#!/usr/bin/env python3
# batch_download_refseq.py v0.4 - added optional API key argument
# Downloads RefSeq sequences under a user-defined taxonomic group in batches of 500

import os
import argparse
import re
import requests
import logging

def main():
    logging.basicConfig(filename = "logger.log", encoding = "utf-8", filemode = "w", level = logging.INFO)
    logging.info("Start")

    parser = argparse.ArgumentParser(description="Downloads RefSeq sequences under a user-defined set of taxonomic groups in batches of 500")
    parser.add_argument("i", help = "specify taxid of taxonomic group")
    parser.add_argument("n", help = "specify name of taxonomic group")
    parser.add_argument("-o", "--output_directory", help = "specify output directory of downloaded sequence files") # default = $DB_NAME/sequences
    parser.add_argument("-k", "--api_key", help = "specify NCBI API key (optional)", default = None)
    args = parser.parse_args()

    db = "nucleotide"
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    query_taxid = args.i
    query_name = args.n
    query = f"txid{query_taxid}[Organism]+AND+RefSeq"
    ext = f"esearch.fcgi?db={db}&term={query}&usehistory=y"
    if args.api_key != None:
        ext += f"&api_key={args.api_key}"
    url = base + ext

    try:
        output = requests.get(url)
    except Exception as e:
        logging.warning(f"Failed to access {url} due to {e}")
        
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
            try:
                efetch_out = requests.get(efetch_url)
            except requests.exceptions.ChunkedEncodingError as e:
                logging.warning(f"Failed to download from {efetch_url} due to {e}")
                continue
            w.write(efetch_out.text)
    print(f"Successfully downloaded {query_name} (taxid: {query_taxid}) RefSeq sequences")

    logging.info("End")

def get_substring(string, c1, c2):
    idx1 = string.index(c1)
    idx2 = string.index(c2, 1)
    new_string = string[idx1+1:idx2]
    return new_string

if __name__ == "__main__":
    main()