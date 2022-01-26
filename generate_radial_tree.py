#!/usr/bin/env python3

import os
import argparse
import re
from ete3 import NCBITaxa, TreeStyle, NodeStyle, faces, AttrFace, CircleFace, TextFace, Tree

def main():
    os.environ['QT_QPA_PLATFORM'] = 'offscreen' # must include this line if running on headless server 
    cwd = os.getcwd() # must be in $DB_NAME/

    colours = ["IndianRed", "Pink", "LightSalmon", "Gold", "Thistle", "GreenYellow", "Aqua", "Bisque", "Gainsboro",
                "HotPink", "OrangeRed", "Yellow", "Violet", "LimeGreen", "LightCyan", "BurlyWood", "Gray"]

    parser = argparse.ArgumentParser(description = "Reads in Kraken2 classification output and produces a radial tree of the identified taxonomic groups")
    parser.add_argument("i", help = "specify Kraken2 classification output file")
    parser.add_argument("-o", "--output_tree", help = "specify filename of output tree image (default filetype = .svg)", default = "tree.svg")
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

    # Prune NCBI taxonomy tree & annotate each leaf with sci name and taxonomic rank
    ncbi = NCBITaxa()
    tree = ncbi.get_topology(classified_taxids)
    classified_taxids2name = ncbi.get_taxid_translator(classified_taxids)
    classified_taxids2rank = ncbi.get_rank(classified_taxids)
    for leaf in tree.traverse():
        if leaf.name in classified_taxids2name:
            leaf.add_feature(sci_name = classified_taxids2name[leaf.name])
            leaf.add_feature(rank = classified_taxids2rank[leaf.name])

    # Tree style
    ts = TreeStyle()
    ts.layout_fn = layout  
    ts.show_leaf_name = False
    ts.mode = "c"
    ts.arc_start = -180
    ts.arc_span = 359

    idx = 0
    for node in tree.search_nodes(rank = "phylum"):
        style = NodeStyle()
        style["bgcolor"] = colours[idx]
        node.set_style(style)
        ts.legend.add_face(CircleFace(300, colours[idx]), column=0)
        ts.legend.add_face(TextFace(f" {node.sci_name}", fsize = 200), column=1)
        idx += 1

    tree.render("tree.png", w = 183, units = "mm", tree_style = ts, dpi = 300)
 
def layout(node):
    style2 = NodeStyle()
    style2["fgcolor"] = "darkred"
    style2["shape"] = "sphere"
    style2["size"] = 50

    if node.is_leaf():
        node.set_style(style2)
    
# eg. Streptococcus agalactiae (taxid 2754)
def extract_taxid(name):
    p1 = re.compile(r"taxid (\d+)")
    m1 = p1.search(name).group()
    idx1 = m1.index(" ")
    idx2 = len(m1)
    taxid = m1[idx1+1:idx2]
    return taxid

if __name__ == "__main__":
    main()

