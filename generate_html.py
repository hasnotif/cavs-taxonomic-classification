#!/usr/bin/env python3

import os
import argparse

def main():
    cwd = os.getcwd()
    res_dir = os.path.join(cwd, "results")
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)

    parser = argparse.ArgumentParser(description = "Creates a HTML report of Kraken2 classification results")
    parser.add_argument("-r", "--kraken2_report", help = "specify Kraken2 report output file")
    parser.add_argument("-s", "--kraken2_standard", help = "specify Kraken2 standard output file")
    parser.add_argument("-d", "--output_dir", help = "specify output directory for HTML files", default = res_dir)
    args = parser.parse_args()

    # calculate classification rate
    rate = get_classification_rate(args.kraken2_standard)

    # print taxa results from Kraken2 report - ignore unclassified and root
    results = get_taxa_results(args.kraken2_report)

    # generate HTML file
    page = HTMLGenerator("results.html")
    page.add_cl_rate(rate)
    page.add_taxa_results(results)
    page.write(args.output_dir)

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
    """ phylum_dict = {}
    class_dict = {}
    order_dict = {}
    family_dict = {}
    genus_dict = {}
    species_dict = {} """

    results = []

    with open(file, "r") as r:
        lines = r.readlines()
        for line in lines:
            line = line.strip("\n")
            tab = line.split("\t")
            percentage_cover = tab[0]
            num_cover = tab[1]
            num_ass_direct = tab[2]
            rank = tab[3]
            taxid = tab[4]
            sci_name = tab[5]
            result = (percentage_cover, num_cover, num_ass_direct, rank, taxid, sci_name) 
            results.append(result)
            """ if taxid != "0" or "1":
                rank = tab[3]
                if "P" in rank:
                    phylum_dict[taxid] = line
                if "C" in rank:
                    class_dict[taxid] = line
                if "O" in rank:
                    order_dict[taxid] = line
                if "F" in rank:
                    family_dict[taxid] = line
                if "G" in rank:
                    genus_dict[taxid] = line
                if "S" in rank:
                    species_dict[taxid] = line """

    return results

class HTMLGenerator(object):
    def __init__(self, filename):
        self.filename = filename
        self.cl_rate = " of the sequences are classified."
        self.taxa_results = []
        
    def add_cl_rate(self, rate):
        self.cl_rate = str(rate) + self.cl_rate

    def add_taxa_results(self, results):
        self.taxa_results += results

    # dir = path where html file should be saved, eg. ~/results
    def write(self, dir):
        file = os.path.join(dir, self.filename)

        with open(file, "w") as w:
            w.write("<html>\n")

            # head section
            w.write("\t<head>\n")
            w.write("\t\t<h1>Kraken2 taxonomic classification results</h1>\n")
            w.write("\t</head>\n")

            # body section
            w.write("\t<body>\n")
            w.write(f"\t\t<p>{self.cl_rate}</p>\n")
            
            # draw table of taxa results
            w.write("\t\t<table>\n")
            w.write("\t\t\t<tr>\n")
            w.write("\t\t\t\t<th>Taxon Name</th>\n")
            w.write("\t\t\t\t<th>Taxonomic ID</th>\n")
            w.write("\t\t\t\t<th>Rank</th>\n")
            w.write("\t\t\t\t<th>Percentage of fragments covered</th>\n")
            w.write("\t\t\t\t<th>Number of fragments covered</th>\n")
            w.write("\t\t\t\t<th>Number of fragments directly assigned</th>\n")
            w.write("\t\t\t</tr>\n")

            # result = (percentage_cover, num_cover, num_ass_direct, rank, taxid, sci_name)
            for result in self.taxa_results:
                w.write("\t\t\t<tr>\n")
                w.write(f"\t\t\t\t<td>{result[5]}</td>\n")
                w.write(f"\t\t\t\t<td>{result[4]}</td>\n")
                w.write(f"\t\t\t\t<td>{result[3]}</td>\n")
                w.write(f"\t\t\t\t<td>{result[0]}</td>\n")
                w.write(f"\t\t\t\t<td>{result[1]}</td>\n")
                w.write(f"\t\t\t\t<td>{result[2]}</td>\n")
                w.write("\t\t\t</tr>\n")

            w.write("\t\t</table>\n")
            w.write("</body>\n")

            w.write("</html>\n")        

if __name__ == "__main__":
    main()