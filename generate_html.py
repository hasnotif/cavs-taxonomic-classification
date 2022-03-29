#!/usr/bin/env python3

import os
import argparse
import datetime
import shutil

def main():
    cwd = os.getcwd() # assume home directory

    # create 'html_results' html directory
    res_dir = os.path.join(cwd, "html_results")
    if not os.path.exists(res_dir):
        print("Creating HTML directory...")
        os.mkdir(res_dir)

    parser = argparse.ArgumentParser(description = "Creates a HTML report of Kraken2/Bracken classification results")
    parser.add_argument("-r", "--report_output", help = "specify Kraken2/Bracken report output file")
    parser.add_argument("-s", "--standard_output", help = "specify Kraken2 standard output file")
    parser.add_argument("-t", "--tree_name", help = "specify filename of radial tree image", default = "radial_tree.svg")
    parser.add_argument("-f", "--output_filename", help = "specify filename of HTML report", default = "results.html")
    parser.add_argument("-q", "--query_name", help = "specify a recognisable query name based on your experiment (eg. Pangolin-herpes-tumor-DNA)", default = "Kraken2 query")
    parser.add_argument("-u", "--update_taxonomy", help = "update NCBI taxonomy files", action = "store_true")
    args = parser.parse_args()

    # copy CSS, javascript and Kraken2/Bracken output files to html directory
    shutil.copy(args.report_output, res_dir)
    shutil.copy(args.standard_output, res_dir)
    shutil.copy("cavs-taxonomic-classification/styles.css", res_dir)
    shutil.copy("cavs-taxonomic-classification/reportScript.js", res_dir)
    shutil.copy("cavs-taxonomic-classification/cavs_logo.jpg", res_dir)

    done_msg = "DONE"

    # calculate classification rate from Kraken2 standard output
    print("Calculating classification rate...", end = " ")
    rate, total = get_classification_rate(args.standard_output)
    print(done_msg)

    # print taxa results from Kraken2 report - ignore unclassified and groups with 0 seq directly assigned (TBC)
    print("Obtaining taxa results...", end = " ")
    results = get_taxa_results(args.report_output)
    print(done_msg)

    # generate radial tree image, default = tree.svg
    print("Generating radial taxonomy tree...", end = " ")
    cmd = f"~/cavs-taxonomic-classification/generate_radial_tree.py {args.report_output} -o {args.tree_name}"
    if args.update_taxonomy:
        cmd += f" --update_taxonomy"
    os.system(cmd)
    print(done_msg)

    # generate HTML file
    print("Generating HTML report...", end = " ")
    page = HTMLGenerator(args.report_output, args.output_filename, total, rate, args.tree_name, args.query_name)
    page.add_taxa_results(results)
    page.write(res_dir)
    print(done_msg)
    print(f"The HTML report has been successfully generated in the following directory: {res_dir}")

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
    def __init__(self, report_file, filename, total_seq, cl_rate, tree_img, query_name):
        self.report_file = report_file
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
            w.write("\t</head>\n")

            # body section
            w.write("\t<body>\n")
            # header div
            w.write("\t\t<div class=\"header\">\n")
            w.write("\t\t\t<div id=\"header_details\">\n")
            now = datetime.datetime.now()
            day = now.strftime("%d")
            mth = now.strftime("%B")
            year = now.strftime("%Y")
            t = now.strftime("%X")
            w.write(f"\t\t\t\t{day} {mth} {year}, {t}\n")
            w.write("\t\t\t\t<br>\n")
            w.write(f"\t\t\t\t<a href=\"../html_results\" id=\"folder_link\">{self.query_name}</a>\n")
            w.write("\t\t\t</div>\n")
            w.write("\t\t\t<div id=\"header_title\">\n")
            w.write("\t\t\t\t<img id=\"cavslogo\" src=\"cavs_logo.jpg\" alt=\"cavs_logo\" height=\"55\" width=\"55\">\n")
            w.write("\t\t\t\t<a id=\"title\">Taxonomic Classification Report</a>\n")
            w.write("\t\t\t</div>\n")
            w.write("\t\t</div>\n")
            w.write("\t\t<div class=\"main\">\n")

            # main stats table
            w.write("\t\t\t<h2>Main statistics</h2>\n")
            w.write("\t\t\t<table id=\"mainStatsTable\">\n")
            w.write("\t\t\t\t<thead>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<th>Field</th>\n")
            w.write("\t\t\t\t\t\t<th>Value</th>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t</thead>\n")
            w.write("\t\t\t\t<tbody>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<td>Raw report filename</td>\n")
            w.write(f"\t\t\t\t\t\t<td><a href=\"{self.report_file}\">{self.report_file}</a></td>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<td>Raw report filetype</td>\n")
            if "bracken" in self.report_file:
                w.write("\t\t\t\t\t\t<td>Bracken report</td>\n")
            else:
                w.write("\t\t\t\t\t\t<td>Kraken2 report</td>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<td>Classification rate</td>\n")
            w.write(f"\t\t\t\t\t\t<td>{self.cl_rate}</td>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<td>Total number of reads in sample</td>\n")
            w.write(f"\t\t\t\t\t\t<td>{self.total_seq}</td>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<td>Kraken2 confidence threshold</td>\n")
            w.write(f"\t\t\t\t\t\t<td>0.05</td>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<td>Bracken threshold</td>\n")
            w.write(f"\t\t\t\t\t\t<td>10</td>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t</tbody>\n")
            w.write("\t\t\t</table>\n")

            # embed radial tree image
            w.write("\t\t\t<h2>Taxonomy tree of Kraken2-classified groups (after Bracken estimation)</h2>\n")
            w.write("\t\t\t<p>Note: The black bars represent Bracken-estimated species-level read counts.</p>\n")
            w.write(f"\t\t\t<img id=\"radialTree\" src=\"{self.tree_img}\" alt=\"radial tree image\">\n")
            
            # draw table of taxa results
            w.write(f"\t\t\t<h2>Detailed statistics for classified taxonomic groups (after Bracken estimation)</h2>\n")
            # header row
            w.write("\t\t\t<table id=\"taxonomyTable\" class=\"tablesorter\">\n")
            w.write("\t\t\t\t<thead>\n")
            w.write("\t\t\t\t\t<tr>\n")
            w.write("\t\t\t\t\t\t<th>Taxon Name</th>\n")
            w.write("\t\t\t\t\t\t<th>Taxonomic ID</th>\n")

            # Rank filter with dropdown menu
            w.write("\t\t\t\t\t\t<th>\n")
            w.write("\t\t\t\t\t\t\t<select name=\"rankList\" id=\"rankList\" class=\"form-control\">\n")
            w.write("\t\t\t\t\t\t\t\t<option selected disabled>Rank</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Domain\">Domain</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Kingdom\">Kingdom</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Phylum\">Phylum</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Class\">Class</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Order\">Order</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Family\">Family</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Genus\">Genus</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"Species\">Species</option>\n")
            w.write("\t\t\t\t\t\t\t\t<option value=\"All Ranks\">All Ranks</option>\n")
            w.write("\t\t\t\t\t\t\t</select>\n")
            w.write("\t\t\t\t\t\t</th>\n")

            w.write("\t\t\t\t\t\t<th id=\"3\" class=\"rankable\">Percentage of reads covered (%)</th>\n")
            w.write("\t\t\t\t\t\t<th id=\"4\" class=\"rankable\">Number of reads covered</th>\n")
            w.write("\t\t\t\t\t\t<th id=\"5\" class=\"rankable\">Number of reads directly assigned</th>\n")
            w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t</thead>\n")

            w.write("\t\t\t\t<tbody>\n")
            # result = (percentage_cover, num_cover, num_ass_direct, rank, taxid, sci_name)
            for result in self.taxa_results:
                w.write("\t\t\t\t\t<tr>\n")
                w.write(f"\t\t\t\t\t\t<td id=\"name\">{result[5]}</td>\n")
                w.write(f"\t\t\t\t\t\t<td id=\"taxid\">{result[4]}</td>\n")
                w.write(f"\t\t\t\t\t\t<td id=\"rank\">{result[3]}</td>\n")
                w.write(f"\t\t\t\t\t\t<td id=\"percentage\">{result[0]}</td>\n")
                w.write(f"\t\t\t\t\t\t<td id=\"num_cover\">{result[1]}</td>\n")
                w.write(f"\t\t\t\t\t\t<td id=\"num_direct\">{result[2]}</td>\n")
                w.write("\t\t\t\t\t</tr>\n")
            w.write("\t\t\t\t</tbody>\n")
            w.write("\t\t\t</table>\n")
            w.write("\t\t</div>\n")
            
            # embed javascript
            w.write("\t\t<script src=\"reportScript.js\"></script>\n")

            w.write("\t</body>\n")
            w.write("</html>\n")        

if __name__ == "__main__":
    main()