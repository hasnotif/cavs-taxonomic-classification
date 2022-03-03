#!/usr/bin/env python3

import os
import argparse
from ete3 import NCBITaxa, TreeStyle, NodeStyle, CircleFace, TextFace

def main():
    os.environ['QT_QPA_PLATFORM'] = 'offscreen' # must include this line if running on headless server 
    cwd = os.getcwd()
    res_dir = os.path.join(cwd, "results")
    if os.path.exists(res_dir):
        os.chdir(res_dir)
    else:
        os.mkdir(res_dir)
        os.chdir(res_dir)

    colours = ["IndianRed", "Pink", "LightSalmon", "Gold", "Thistle", "GreenYellow", "Aqua", "Bisque", "Gainsboro",
                "HotPink", "OrangeRed", "Yellow", "Violet", "LimeGreen", "LightCyan", "BurlyWood", "Gray", "Red", "MediumVioletRed", "DarkOrange",
                "Khaki", "DarkViolet", "SeaGreen", "Turquoise", "RosyBrown", "SlateGray"]

    parser = argparse.ArgumentParser(description = "Reads in Kraken2 classification output and produces a radial tree of the identified taxonomic groups")
    parser.add_argument("i", help = "specify Kraken2 classification output file")
    parser.add_argument("-o", "--output_tree", help = "specify filename of output tree image (default filetype = .svg)", default = "tree.svg")
    parser.add_argument("-u", "--update_taxonomy", help = "update NCBI taxonomy files", action = "store_true")
    args = parser.parse_args()

    # obtain classified taxids from Kraken2 output file
    with open(args.i, "r") as r:
        classified_taxids = []
        for line in r:
            tab = line.split("\t")
            if "R" in tab[3] or "U" in tab[3]:
                continue
            else:
                classified_taxids.append(tab[4])

    # Prune NCBI taxonomy tree & annotate each leaf with sci name and taxonomic rank
    ncbi = NCBITaxa()
    if args.update_taxonomy:
        ncbi.update_taxonomy_database()
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
    ts.legend.add_face(TextFace("Phyla", fsize = 100, bold = True), column = 0)
    ts.legend.add_face(CircleFace(0, "White", style = "circle"), column = 1)
    ts.legend_position = 4

    # Colouring phyla and adding legend
    idx = 0
    for node in tree.search_nodes(rank = "phylum"): 
        style = NodeStyle()
        style["bgcolor"] = colours[idx]
        node.set_style(style)

        ts.legend.add_face(CircleFace(100, colours[idx]), column = 0)
        ts.legend.add_face(TextFace(f" {node.sci_name}", fsize = 100), column = 1)
        idx += 1

    tree.render("tree.svg", w = 180, units = "mm", tree_style = ts)
 
def layout(node):
    style2 = NodeStyle()
    style2["fgcolor"] = "darkred"
    style2["shape"] = "sphere"
    style2["size"] = 50

    if node.is_leaf():
        node.set_style(style2)
    
if __name__ == "__main__":
    main()

