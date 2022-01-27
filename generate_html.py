#!/usr/bin/env python3

import os
import argparse

def main():
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description = "Creates a HTML report of Kraken2 classification results")
    parser.add_argument("-r", "--kraken2_report", help = "specify Kraken2 report output file")
    parser.add_argument("-s", "--kraken2_standard", help = "specify Kraken2 standard output file")
    args = parser.parse_args()

    # calculate classification rate
    rate = get_classification_rate(args.kraken2_standard)
    print(f"{rate} of the sequences are classified.")

    # print taxa results from Kraken2 report - ignore unclassified and root
    taxa_results = get_taxa_results(args.kraken2_report)
    print(len(taxa_results))

def get_classification_rate(file):
    with open(file, "r") as r:
        lines = r.readlines()
        classified_count = 0
        total_count = len(lines)
        for line in lines:
            tab = line.split("\t")
            if tab[0] == "C":
                classified_count += 1

    res = '{:.2f}%'.format((classified_count/total_count)*100)
    return res

def get_taxa_results(file):
    dict = {}
    with open(file, "r") as r:
        lines = r.readlines()
        for line in lines:
            tab = line.split("\t")
            if tab[4] != "0" or "1":
                dict[tab[4]] = line
    return dict

if __name__ == "__main__":
    main()