#!/usr/bin/env python3

import os
import argparse
from ete3 import NCBITaxa

def main():
    cwd = os.getcwd() # must be in $DB_NAME/

    parser = argparse.ArgumentParser(description = "Reads in Kraken2 classification output and produces a radial tree of the identified taxonomic groups")
    parser.add_argument("i", help = "specify Kraken2 classification output file")
    args = parser.parse_args()

    # obtain classified taxids from Kraken2 output file
    with open(args.i, "r") as r:
        classified_taxids = []
        for line in r:
            tab = line.split("\t")
            cu = tab[0]
            if cu == "C":
                taxid = tab[2]
                if not taxid.isdigit():
                    taxid = extract_taxid(taxid)
                if taxid not in classified_taxids:
                    classified_taxids.append(taxid)

    ncbi = NCBITaxa()
    tree = ncbi.get_topology(classified_taxids)
    tree.render("test_tree.png", w = 180, units = "mm")
 
# eg. Streptococcus agalactiae (taxid 2754)
def extract_taxid(name):
    idx1 = name.index("(")
    idx2 = name.index(")")
    bracket = name[idx1+1:idx2]
    idx3 = bracket.index(" ")
    idx4 = len(bracket)
    taxid = bracket[idx3+1:idx4]
    return taxid

if __name__ == "__main__":
    main()

