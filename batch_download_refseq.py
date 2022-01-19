#!/usr/bin/env python3
# batch_download_refseq.py v0.3 - modified to facilitate parallel batch downloads via makefile
# Downloads RefSeq sequences under a user-defined taxonomic group in batches of 500

import os
import argparse
import re
import requests

def main():
    parser = argparse.ArgumentParser(description="Downloads RefSeq sequences under a user-defined set of taxonomic groups in batches of 500")
    parser.add_argument("i", help = "specify taxid of taxonomic group")
    parser.add_argument("n", help = "specify name of taxonomic group")
    parser.add_argument("-o", "--output_directory", help = "specify output directory of downloaded sequence files") # default = $DB_NAME/sequences
    args = parser.parse_args()

    db = "nucleotide"
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    query_taxid = args.i
    query_name = args.n
    query = f"txid{query_taxid}[Organism]+AND+RefSeq"
    ext = f"esearch.fcgi?db={db}&term={query}&usehistory=y&api_key=9551d35e36c6a9cc3d58ab68607b265c2608"
    url = base + ext

    output = requests.get(url)
        
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
            efetch_url += f"&api_key=9551d35e36c6a9cc3d58ab68607b265c2608"
            efetch_out = requests.get(efetch_url)
            w.write(efetch_out.text)
    print(f"Successfully downloaded {query_name} (taxid: {query_taxid}) RefSeq sequences")

def get_substring(string, c1, c2):
    idx1 = string.index(c1)
    idx2 = string.index(c2, 1)
    new_string = string[idx1+1:idx2]
    return new_string

if __name__ == "__main__":
    main()