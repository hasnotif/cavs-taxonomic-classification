#!/usr/bin/env python3
# batch_download_refseq.py v0.1
# Downloads RefSeq sequences under a user-defined set of taxonomic groups in batches of 500

from email.policy import default
import os
import argparse
import re
import requests

def main():
    cwd = os.getcwd() # must be in $DB_NAME/taxonomy

    parser = argparse.ArgumentParser(description="Downloads RefSeq sequences under a user-defined set of taxonomic groups in batches of 500")
    parser.add_argument("i", help = "specify file containing newline-separated names of desired taxonomic groups")
    database_path = os.path.dirname(cwd)
    # print(database_path)
    default_seq_path = os.path.join(database_path, "sequences")
    # print(default_seq_path)
    if not os.path.exists(default_seq_path):
        os.mkdir(default_seq_path)
    parser.add_argument("-o", "--output_directory", help = "specify output directory of downloaded sequence files", default = default_seq_path)
    args = parser.parse_args()

    print("Parsing names.dmp")
    name_dict = load_ncbi_names("names.dmp") # key = name, value = taxid or [taxids]
    query_taxids = [] # contains (taxid, name) tuples

    print("Reading your taxonomic groups")
    with open(args.i, "r") as r:
        for name in r:
            name = name.strip("\n")
            if name == "":
                break
            if isinstance(name_dict[name], list):
                taxid_list = name_dict[name]
                print("Multiple taxIDs found for " + name + ": " + ", ".join(taxid_list))
                print("Please check which taxID is correct and type your chosen taxID(s) - if more than 1 taxID, separate them with a space")
                chosen_taxid = input("Enter your chosen taxID(s): ")
                chosen_taxid_list = chosen_taxid.split(" ")
                for taxid in chosen_taxid_list:
                    pair = (taxid, name)
                    query_taxids.append(pair)
            else:
                pair = (name_dict[name], name)
                query_taxids.append(pair)

    db = "nucleotide"
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    
    for pair in query_taxids:
        query_taxid = pair[0]
        query_name = pair[1] 
        query = f"txid{query_taxid}[Organism]+AND+RefSeq"
        ext = f"esearch.fcgi?db={db}&term={query}&usehistory=y"
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

        print(f"Downloading {count} {query_name} ({query_taxid}) RefSeq sequences in batches of 500")
        with open(os.path.join(args.output_directory, f"{query_name}_{query_taxid}.fasta"), "w") as w:
            retmax = 500
            for i in range(0, int(count), retmax):
                efetch_url = base + f"efetch.fcgi?db={db}&WebEnv={web_env}"
                efetch_url += f"&query_key={key}&retstart={i}"
                efetch_url += f"&retmax={retmax}&rettype=fasta&retmode=text"
                efetch_out = requests.get(efetch_url)
                w.write(efetch_out.text)
        print(f"Successfully downloaded {query_name} ({query_taxid}) RefSeq sequences")

    print("Batch download complete")

def get_substring(string, c1, c2):
    idx1 = string.index(c1)
    idx2 = string.index(c2, 1)
    new_string = string[idx1+1:idx2]
    return new_string

def load_ncbi_names(filename):
    name_dict = {}  # key = name, value = taxid or [taxids]

    with open(filename, 'r') as r:
        while 1:
            line = r.readline()
            if line == "":
                break
            line2 = line.rstrip()
            line2 = line2.replace("\t", "")
            tab = line2.split("|")
            if tab[3] == "scientific name":
                tax_id, name = tab[0], tab[1]

                # load name_dict
                if name in name_dict: # duplicate name found
                    if isinstance(name_dict[name], list): # name already has a list of taxids
                        taxid_list = name_dict[name]
                        taxid_list.append(str(tax_id))
                        name_dict[name] = taxid_list
                    else: # name currently assigned to one taxid 
                        new_taxid_list = [name_dict[name]]
                        new_taxid_list.append(str(tax_id))
                        name_dict[name] = new_taxid_list
                else:
                    name_dict[name] = str(tax_id)  

    return name_dict

if __name__ == "__main__":
    main()