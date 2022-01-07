#!/usr/bin/env python3
# generate_download_filtered_seq_pipeline.py v0.1 
# Generates a makefile which downloads specific RefSeq sequences based on user-defined set of taxonomic groups

import os
import argparse

def main():
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description = "Download specific RefSeq sequences based on a user-defined set of taxonomic groups")
    parser.add_argument('i', help = "specify input file in .txt format - taxon names must be newline-separated")
    parser.add_argument('-m', '--makefile_name', help = "specify filename of makefile with .mk extension", default = "download_filtered_seq.mk")
    parser.add_argument('-d', '--output_directory', help = "specify directory of output .fasta file", default = cwd)
    args = parser.parse_args()

    print("Processing your taxonomic groups")
    with open(args.i, 'r') as r:
        query_taxnames = r.readlines()
    query_taxnames2 = []
    for taxname in query_taxnames:
        query_taxnames2.append(taxname.strip("\n"))

    names_dmp_dict, names_dmp_dict_reversed = load_name_dict(filename="names.dmp") # this names.dmp must be the filtered version
    
    query_taxids = []
    for taxname in query_taxnames2:
        if isinstance(names_dmp_dict_reversed[taxname], list):
            taxid_list = names_dmp_dict_reversed[taxname]
            print("Multiple taxIDs found for " + taxname + ": " + ", ".join(taxid_list))
            print("Please check which taxID is correct and type your chosen taxID(s) - if more than 1 taxID, separate them with a space")
            chosen_taxid = input("Enter your chosen taxID(s): ")
            chosen_taxid_list = chosen_taxid.split(" ")
            query_taxids += chosen_taxid_list
        else:
            taxid = names_dmp_dict_reversed[taxname]
            query_taxids.append(str(taxid))

    print("Generating targets and dependencies for makefile")
    tgts = []
    deps = []
    cmds = []

    for taxid in query_taxids:
        tgt = f'{args.output_directory}/{names_dmp_dict[taxid]}.fa.OK'
        tgts.append(tgt)

        dep = ''
        deps.append(dep)

        cmd = f'esearch -db taxonomy -query "txid{taxid} [Organism]"|elink -target nuccore|efilter -query "refseq"|efetch -format fasta > {names_dmp_dict[taxid]}.fa'
        cmds.append(cmd)

    print("Writing makefile")
    write_makefile(tgts, deps, cmds, args.makefile_name)
        
def load_name_dict(filename: str = "names.dmp"):
    names_dmp_dict = {} # key = taxid, value = name
    names_dmp_dict_reversed = {} # key = name, value = taxid

    with open(filename, 'r') as r:
        while 1:
            line = r.readline()
            if line == "":
                break
            line2 = line.replace("\t", "")
            tab = line2.split("|")

            tax_id = str(tab[0])
            name = str(tab[1])

            names_dmp_dict[tax_id] = name

            if name in names_dmp_dict_reversed:
                if isinstance(names_dmp_dict_reversed[name], list):
                    taxid_list = names_dmp_dict_reversed[name]
                    taxid_list.append(str(tax_id))
                    names_dmp_dict_reversed[name] = taxid_list
                else:
                    new_taxid_list = [names_dmp_dict_reversed[name]]
                    new_taxid_list.append(str(tax_id))
                    names_dmp_dict_reversed[name] = new_taxid_list
            else:
                names_dmp_dict_reversed[name] = str(tax_id)

    return (names_dmp_dict, names_dmp_dict_reversed)

def write_makefile(tgts, deps, cmds, filename):
    with open(filename, 'w') as f:
        f.write("all : ") 
        for tgt in tgts:
            f.write(f'{tgt} ')
        f.write("\n\n")

        for i in range(len(tgts)):
            f.write(f'{tgts[i]} : {deps[i]}\n')
            f.write(f'\t{cmds[i]}\n')
            f.write(f'\ttouch {tgts[i]}\n\n')

if __name__ == "__main__":
    main()
