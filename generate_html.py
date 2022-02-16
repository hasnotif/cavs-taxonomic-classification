#!/usr/bin/env python3

import os
import argparse
import datetime
import shutil

def main():
    cwd = os.getcwd() # assume home directory

    # create 'results' html directory
    res_dir = os.path.join(cwd, "results")
    if not os.path.exists(res_dir):
        os.mkdir(res_dir)

    parser = argparse.ArgumentParser(description = "Creates a HTML report of Kraken2 classification results")
    parser.add_argument("-r", "--kraken2_report", help = "specify Kraken2 report output file")
    parser.add_argument("-s", "--kraken2_standard", help = "specify Kraken2 standard output file")
    parser.add_argument("-d", "--output_dir", help = "specify output directory for HTML files", default = res_dir)
    parser.add_argument("-t", "--tree_name", help = "specify filename of radial tree image", default = "tree.svg")
    parser.add_argument("-f", "--output_filename", help = "specify filename of HTML report", default = "results.html")
    parser.add_argument("-q", "--query_name", help = "specify a recognisable query name based on your experiment (eg. Pangolin-herpes-tumor-DNA)", default = "Kraken2 query")
    args = parser.parse_args()

    # copy CSS, javascript and Kraken2 output files to html directory
    shutil.copy(args.kraken2_report, "results")
    shutil.copy(args.kraken2_standard, "results")
    shutil.copy("cavs-taxonomic-classification/styles.css", "results")
    shutil.copy("cavs-taxonomic-classification/reportScript.js", "results")

    # calculate classification rate
    rate, total = get_classification_rate(args.kraken2_standard)

    # print taxa results from Kraken2 report - ignore unclassified and groups with 0 seq directly assigned (TBC)
    results = get_taxa_results(args.kraken2_report)

    # generate radial tree image, default = tree.svg
    os.system(f"~/cavs-taxonomic-classification/generate_radial_tree.py {args.kraken2_standard} -o {args.tree_name}")

    # generate HTML file
    page = HTMLGenerator(args.output_filename, total, rate, args.tree_name, args.query_name)
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
    return res, total_count

def get_taxa_results(file):
    results = []

    with open(file, "r") as r:
        lines = r.readlines()
        for line in lines:
            line = line.strip("\n")
            tab = line.split("\t")
            if tab[4] == "0":
                continue
            percentage_cover, num_cover, num_direct, rank, taxid, sci_name = tab[0], tab[1], tab[2], tab[3], tab[4], tab[5]
            result = (percentage_cover, num_cover, num_direct, rank, taxid, sci_name)
            results.append(result)
            
    return results

class HTMLGenerator(object):
    def __init__(self, filename, total_seq, cl_rate, tree_img, query_name):
        self.filename = filename
        self.total_seq = total_seq
        self.cl_rate = cl_rate
        self.tree_img = tree_img
        self.taxa_results = []
        self.query_name = query_name

    def add_taxa_results(self, results):
        self.taxa_results += results

    # dir = path where html file should be saved, eg. ~/results
    def write(self, dir):
        file = os.path.join(dir, self.filename)

        with open(file, "w") as w:
            w.write("<!DOCTYPE html>\n")
            w.write("<html>\n")

            # head section
            w.write("\t<head>\n")
            w.write("\t\t<link rel=\"stylesheet\" href=\"styles.css\">\n")
            w.write("\t\t<h1 id=\"header\">Kraken2 taxonomic classification results</h1>\n")
            w.write("\t</head>\n")

            # body section
            w.write("\t<body>\n")
            w.write("\t\t<h2>Report details</h2>\n")
            now = datetime.datetime.now()
            day = now.strftime("%d")
            mth = now.strftime("%B")
            year = now.strftime("%Y")
            t = now.strftime("%X")
            w.write(f"\t\t<p>This report for {self.query_name} was generated on {day} {mth} {year}, {t}.</p>\n")
            w.write("\t\t<h2>Summary of results</h2>\n")
            w.write(f"\t\t<p>Out of {self.total_seq} sequences, {self.cl_rate} are assigned with a taxonomic classification.</p>\n")

            # embed radial tree image
            w.write("\t\t<h3>Radial tree of Kraken2-classified taxonomic groups</h3>\n")
            w.write(f"\t\t<img id=\"radialTree\" src=\"{self.tree_img}\" alt=\"radial tree image\" width=\"750\" height=\"750\">\n")
            
            # draw table of taxa results
            w.write(f"\t\t<h2>Table of classified taxonomic groups</h2>\n")
            # header row
            w.write("\t\t<table id=\"taxonomyTable\" class=\"tablesorter\">\n")
            w.write("\t\t\t<thead>\n")
            w.write("\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t<th>Taxon Name</th>\n")
            w.write("\t\t\t\t\t<th>Taxonomic ID</th>\n")

            # Rank filter with dropdown menu
            w.write("\t\t\t\t\t<th>\n")
            w.write("\t\t\t\t\t\t<select name=\"rankList\" id=\"rankList\" class=\"form-control\">\n")
            w.write("\t\t\t\t\t\t\t<option selected disabled>Rank</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Domain\">Domain</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Kingdom\">Kingdom</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Phylum\">Phylum</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Class\">Class</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Order\">Order</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Family\">Family</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Genus\">Genus</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"Species\">Species</option>\n")
            w.write("\t\t\t\t\t\t\t<option value=\"All Ranks\">All Ranks</option>\n")
            w.write("\t\t\t\t\t\t</select>\n")
            w.write("\t\t\t\t\t</th>\n")

            w.write("\t\t\t\t\t<th id=\"3\" class=\"rankable\">Percentage of fragments covered (%)</th>\n")
            w.write("\t\t\t\t\t<th id=\"4\" class=\"rankable\">Number of fragments covered</th>\n")
            w.write("\t\t\t\t\t<th id=\"5\" class=\"rankable\">Number of fragments directly assigned</th>\n")
            w.write("\t\t\t\t</tr>\n")
            w.write("\t\t\t</thead>\n")

            w.write("\t\t\t<tbody>\n")
            # result = (percentage_cover, num_cover, num_ass_direct, rank, taxid, sci_name)
            for result in self.taxa_results:
                w.write("\t\t\t\t<tr>\n")
                w.write(f"\t\t\t\t\t<td id=\"name\">{result[5]}</td>\n")
                w.write(f"\t\t\t\t\t<td id=\"taxid\">{result[4]}</td>\n")
                w.write(f"\t\t\t\t\t<td id=\"rank\">{result[3]}</td>\n")
                w.write(f"\t\t\t\t\t<td id=\"percentage\">{result[0]}</td>\n")
                w.write(f"\t\t\t\t\t<td id=\"num_cover\">{result[1]}</td>\n")
                w.write(f"\t\t\t\t\t<td id=\"num_direct\">{result[2]}</td>\n")
                w.write("\t\t\t\t</tr>\n")
            w.write("\t\t\t</tbody>\n")
            w.write("\t\t</table>\n")

            # embed javascript
            w.write("\t\t<script src=\"reportScript.js\"></script>\n")

            w.write("\t</body>\n")
            w.write("</html>\n")        

if __name__ == "__main__":
    main()