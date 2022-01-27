#!/usr/bin/env python3
# generate_batch_download_pipeline.py v0.3.1
# Generates a makefile which batch downloads specific RefSeq sequences based on user-defined set of taxonomic groups
# Retmax = 500 by default

import os
import argparse

def main():
    cwd = os.getcwd() # must be in $DB_NAME/
    db_path = cwd
    tax_path = os.path.join(db_path, "taxonomy")
    default_seq_path = os.path.join(cwd, "sequences")

    parser = argparse.ArgumentParser(description = "Download specific RefSeq sequences based on a user-defined set of taxonomic groups")
    parser.add_argument('i', help = "specify input file in .txt format - taxon names must be newline-separated")
    parser.add_argument('-m', '--makefile_name', help = "specify filename of makefile with .mk extension", default = "batch_download_refseq.mk")
    parser.add_argument("-k", "--api_key", help = "specify NCBI API key (optional)", default = None)
    args = parser.parse_args()

    if not os.path.exists(default_seq_path):
        os.mkdir(default_seq_path)
        print(f"Created {default_seq_path} directory - sequence files will be downloaded and saved here")

    print("Processing your taxonomic groups")
    with open(args.i, 'r') as r:
        query_taxnames = r.readlines()
    query_taxnames2 = []
    for taxname in query_taxnames:
        query_taxnames2.append(taxname.strip("\n"))

    print("Parsing names.dmp")
    # changing to $DB_NAME/taxonomy directory
    os.chdir(tax_path)
    name_dict = load_ncbi_names("names.dmp") # key = name, value = taxid or [taxids]
    query_list = [] # contains (taxid, name) tuples

    for name in query_taxnames2:
        if isinstance(name_dict[name], list):
            taxid_list = name_dict[name]
            print(f"Multiple taxIDs found for {name}: {taxid_list}")
            print(f"Please check which taxID is correct and type your chosen taxID(s) - if more than 1 taxID, separate them with a space")
            chosen_taxid = input("Enter your chosen taxID(s): ")
            chosen_taxid_list = chosen_taxid.split(" ")
            for taxid in chosen_taxid_list:
                pair = (taxid, name)
                query_list.append(pair)
        else:
            pair = (name_dict[name], name)
            query_list.append(pair)

    mg = MakefileGenerator(args.makefile_name)

    # pass query names and taxids (+ API key if available) as separate inputs to batch_download_refseq.py via makefile 
    print("Generating targets and dependencies for makefile")
    for query in query_list:
        tgt = f'{default_seq_path}/{query[1]}_{query[0]}.fa.OK'
        dep = ''
        cmd = f'~/cavs-taxonomic-classification/batch_download_refseq.py {query[0]} {query[1]} -o {default_seq_path}'
        if args.api_key != None:
            cmd += f" -k {args.api_key}"
        mg.add(tgt, dep, cmd)

    print("Writing makefile")
    # change back to $DB_NAME/
    os.chdir(db_path)
    mg.write()
    print(f"Successfully generated makefile ({args.makefile_name})")

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

class MakefileGenerator(object):
    def __init__(self, makefile):
        self.makefile = makefile
        self.tgts = []
        self.deps = []
        self.cmds = []

    def add(self, tgt, dep, cmd):
        self.tgts.append(tgt)
        self.deps.append(dep)
        self.cmds.append(cmd)

    def print(self):
        print('.DELETE_ON_ERROR:')
        for i in range(len(self.tgts)):
            print(f'{self.tgts[i]} : {self.deps[i]}')
            print(f'\t{self.cmds[i]}')
            print(f'\ttouch {self.tgts[i]}')

    def write(self):
        with open(self.makefile, 'w') as f:
            f.write(f".DELETE_ON_ERROR:")
            f.write("\n\n")
            f.write("all : ") 
            for tgt in self.tgts:
                f.write(f'{tgt} ')
            f.write("\n\n")

            for i in range(len(self.tgts)):
                f.write(f'{self.tgts[i]} : {self.deps[i]}\n')
                f.write(f'\t{self.cmds[i]}\n')
                f.write(f'\ttouch {self.tgts[i]}\n\n')
    
if __name__ == "__main__":
    main()