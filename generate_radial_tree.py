#!/usr/bin/env python3

import os
import argparse
from ete3 import NCBITaxa, TreeStyle, NodeStyle, faces, AttrFace

def main():
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
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
    classified_taxids2name = ncbi.get_taxid_translator(classified_taxids)
    for leaf in tree.traverse():
        if leaf.name in classified_taxids2name:
            leaf.add_feature(sci_name = classified_taxids2name[leaf.name])

    # Tree style
    ts = TreeStyle()
    ts.layout_fn = layout  
    ts.show_leaf_name = False
    ts.mode = "c"
    ts.arc_start = -180
    ts.arc_span = 359

    # Node style
    style2 = NodeStyle()
    style2["fgcolor"] = "#000000"
    style2["shape"] = "circle"
    style2["vt_line_color"] = "#0000aa"
    style2["hz_line_color"] = "#0000aa"
    style2["vt_line_width"] = 2
    style2["hz_line_width"] = 2
    style2["vt_line_type"] = 1
    style2["hz_line_type"] = 1
    for l in tree.iter_leaves():
        l.img_style = style2       

    tree.render("test_tree.svg", w = 183, units = "mm", tree_style = ts)

def layout(node):
    if node.is_leaf():
        N = AttrFace("sci_name", fsize = 30)
        faces.add_face_to_node(N, node, column = 0, position = "aligned")
    
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

