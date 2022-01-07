#!/usr/bin/env python3
# filter_ncbi_taxonomy.py v0.4 - to be executed in same directory as taxdump.tar and input .txt file
# Parses the NCBI taxonomy as a tree, then filters out all descendant nodes of user-defined taxonomic groups
# Original credits to romainstuder @ https://github.com/romainstuder/evosite3d for the tree parsing

import os
import argparse
import tarfile
from typing import Dict, List, Tuple

def main():
    cwd = os.getcwd()

    parser = argparse.ArgumentParser(description = "Filter NCBI taxonomy")
    parser.add_argument('i', help = "specify input file in .txt format - taxon names must be newline-separated")
    parser.add_argument('-o', '--output_directory', help = "specify output directory of filtered nodes.dmp", default = cwd)
    args = parser.parse_args()

    # open input .txt file -> [taxon names]
    with open(args.i, 'r') as r:
        hi_taxnames = r.readlines()
    hi_taxnames2 = []
    for taxname in hi_taxnames:
        hi_taxnames2.append(taxname.strip("\n"))

    # extract taxdump.tar.gz
    try:
        file = tarfile.open('taxdump.tar.gz')
        print('Extracting taxdump files into your current directory')
        file.extractall(cwd)
    except FileNotFoundError:
        print('Error: taxdump.tar.gz is not found in your current directory. Please ensure you have downloaded it before running this script again.')
        exit()

    # parse NCBI taxonomy
    print("Parsing NCBI taxonomy")
    name_dict, name_dict_reverse, names_dmp_dict = load_ncbi_names(filename="names.dmp")
    ncbi_taxonomy, nodes_dmp_dict = load_ncbi_taxonomy(filename="nodes.dmp", name_dict=name_dict)
    
    # fetch descendant nodes of input taxons
    print("Fetching all descendant nodes of your input taxons")
    all_descendants = []
    for taxname in hi_taxnames2:
        if isinstance(name_dict_reverse[taxname], list): # input name in hi_taxnames2 found to be a duplicate in taxonomy
            taxid_list = name_dict_reverse[taxname]
            print("Multiple taxIDs found for " + taxname + ": " + ", ".join(taxid_list))
            print("Please check which taxID is correct and type your chosen taxID(s) - if more than 1 taxID, separate them with a space")
            chosen_taxid = input("Enter your chosen taxID(s): ")
            chosen_taxid_list = chosen_taxid.split(" ")
            for taxid in chosen_taxid_list:
                all_descendants += _get_all_descendant_nodes(ncbi_taxonomy, taxid)
        else:
            taxid = name_dict_reverse[taxname]
            all_descendants += _get_all_descendant_nodes(ncbi_taxonomy, taxid)
    
    int_all_descendants = list(map(int, all_descendants))
    sorted_all_descendants = sorted(int_all_descendants)
    sorted_all_descendants = list(map(str, sorted_all_descendants))
    sorted_all_descendants = list(dict.fromkeys(sorted_all_descendants))
    print("Total number of descendant nodes = " + str(len(sorted_all_descendants)))

    # write to nodes2.dmp and names2.dmp
    with open(os.path.join(args.output_directory, 'nodes2.dmp'), 'w') as w1, open(os.path.join(args.output_directory, 'names2.dmp'), 'w') as w2:
        for desc in sorted_all_descendants:
            w1.write(nodes_dmp_dict[desc])
            w2.write(names_dmp_dict[desc])

    print("Successfully obtained descendants")

class Node:
    """ Definition of the class Node """
    def __init__(self):
        self.tax_id = "0"     # Number of the tax id.
        self.parent = "0"     # Number of the parent of this node
        self.children = []    # List of the children of this node
        self.division = None  # Division.
        self.is_tip = True    # Tip = True if it's a terminal node, False if not.
        self.name = ""        # Name of the node: taxa if it's a terminal node, number if not.

def _get_all_descendant_nodes(name_object, taxid: str) -> List[str]:
    """ Get all descendant of a node """
    descendant_nodes: List[str] = [taxid]
    if len(name_object[taxid].children) > 0:
        for child in name_object[taxid].children:
            descendant_nodes = descendant_nodes + _get_all_descendant_nodes(name_object, child)
    return descendant_nodes

def load_ncbi_names(filename: str = "names.dmp") -> Tuple[Dict, Dict, Dict]:
    """Load NCBI names definition ("names.dmp")

    Args:
        filename (str): filename of NCBI names

    Returns:
        name_dict, name_dict_reverse

    """
    name_dict = {}  # key = taxid, value = name
    name_dict_reverse = {}  # key = name, value = taxid
    names_dmp_dict = {}  # key = taxid, value = corresponding line in names.dmp

    with open(filename, 'r') as name_file:
        while 1:
            line = name_file.readline()
            if line == "":
                break
            line2 = line.rstrip()
            line2 = line2.replace("\t", "")
            tab = line2.split("|")
            if tab[3] == "scientific name":
                tax_id, name = tab[0], tab[1]

                # load name_dict 
                name_dict[tax_id] = name

                # load names_dmp_dict
                names_dmp_dict[tax_id] = line

                # load name_dict_reverse 
                if name in name_dict_reverse: # duplicate name found
                    if isinstance(name_dict_reverse[name], list): # name already has a list of taxids
                        taxid_list = name_dict_reverse[name]
                        taxid_list.append(str(tax_id))
                        name_dict_reverse[name] = taxid_list
                    else: # name currently assigned to one taxid 
                        new_taxid_list = [name_dict_reverse[name]]
                        new_taxid_list.append(str(tax_id))
                        name_dict_reverse[name] = new_taxid_list
                else:
                    name_dict_reverse[name] = str(tax_id)  

    return name_dict, name_dict_reverse, names_dmp_dict

def load_ncbi_taxonomy(name_dict, filename: str = "nodes.dmp") -> Tuple[Dict, Dict]:
    """Load taxonomy NCBI file ("nodes.dmp")

    Args:
        filename (str): filename of ncbi taxonomy
        name_dict (dict): name_dict

    Returns:
        name_object, nodes_dmp_dict

    """

    # Define taxonomy variable
    # global name_object
    name_object: Dict = {} # key = tax_id, value = node object
    nodes_dmp_dict : Dict = {} # key = tax_id, value = corresponding line in nodes.dmp

    with open(filename, "r") as taxonomy_file:
        while 1:
            line = taxonomy_file.readline()
            if line == "":
                break
            line2 = line.replace("\t", "")
            tab = line2.split("|")

            tax_id = str(tab[0])
            tax_id_parent = str(tab[1])
            division = str(tab[2])
            
            # Populate nodes_dmp_dict
            nodes_dmp_dict[tax_id] = line

            # Define name of the taxonomy id
            name = "unknown"
            if tax_id in name_dict:
                name = name_dict[tax_id]

            if tax_id not in name_object:
                name_object[tax_id] = Node()
            name_object[tax_id].tax_id = tax_id  # Assign tax_id
            name_object[tax_id].parent = tax_id_parent  # Assign tax_id parent
            name_object[tax_id].name = name  # Assign name
            name_object[tax_id].division = division  # Assign name

            # Add it has children to parents
            children_list = []
            if tax_id_parent in name_object:
                children_list = name_object[tax_id_parent].children  # If parent is in the object
            else:
                name_object[tax_id_parent] = Node()
                name_object[tax_id_parent].tax_id = tax_id_parent  # Assign tax_id
            children_list.append(tax_id)  # ... we found its children.
            name_object[tax_id_parent].children = children_list  # ... so add them to the parent

            # As the parent node is found, it is not a terminal node then
            name_object[tax_id_parent].is_tip = False

    return name_object, nodes_dmp_dict

if __name__ == "__main__":
    main()
