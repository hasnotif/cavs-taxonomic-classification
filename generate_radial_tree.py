#!/usr/bin/env python3
#------------------------------------------------------------------
# Created By: Irsyaad Hasif (hasifirsyaad@gmail.com)
# Created On: 26 Apr 2022 
# Version: 1.0
#------------------------------------------------------------------
# This script prunes the NCBI taxonomy to obtain a Newick tree
# containing only the Kraken2-classified taxonomic groups. It 
# then passes the tree to generate_radial_tree.R for visualisation.
#------------------------------------------------------------------

import os
import argparse
from ete3 import Tree, NCBITaxa

def main():
    cwd = os.getcwd()
    res_dir = os.path.join(cwd, "html_results")
    if os.path.exists(res_dir):
        os.chdir(res_dir)
    else:
        os.mkdir(res_dir)
        os.chdir(res_dir)

    parser = argparse.ArgumentParser(description = "Reads in Kraken2/Bracken report output and produces a radial tree of the identified taxonomic groups")
    parser.add_argument("-i", required = True, help = "specify Kraken2/Bracken report output")
    parser.add_argument("-o", "--output_tree", help = "specify filename of output tree image (default filetype = .svg)", default = "radial_tree.svg")
    parser.add_argument("-u", "--update_taxonomy", help = "update NCBI taxonomy files", action = "store_true")
    args = parser.parse_args()

    # obtain classified taxids from Kraken2/Bracken report output
    with open(args.i, "r") as r:
        classified_taxids = []
        for line in r:
            tab = line.split("\t")
            if tab[3] == "U" or tab[3] == "R":
                continue
            else:
                classified_taxids.append(tab[4])

    # Prune NCBI taxonomy tree
    ncbi = NCBITaxa()
    if args.update_taxonomy:
        ncbi.update_taxonomy_database()
    tree = ncbi.get_topology(classified_taxids)

    # Export Newick tree for R
    out = "radial_tree.txt"
    tree.write(features = ["name", "sci_name", "taxid", "rank"], format = 3, outfile = out)
    
    # Call R script with Newick tree file as input
    cmd = f"Rscript ~/cavs-taxonomic-classification/generate_radial_tree.R {out} {args.i} {args.output_tree}"
    os.system(cmd)
    
if __name__ == "__main__":
    main()