#!/usr/bin/env python3
# filter_parasite_taxonomy.py ver 0.1
# Parses the NCBI taxonomy as a tree, then filters out all parasite groups
# Original credits to romainstuder @ https://github.com/romainstuder/evosite3d for the tree parsing

import logging
import random
from typing import Dict, List, Tuple

LOGGER = logging.getLogger()
LOGGER.setLevel(0)

def main():
    name_dict, name_dict_reverse = load_ncbi_names(filename="names.dmp")
    ncbi_taxonomy, nodes_dmp_dict = load_ncbi_taxonomy(filename="nodes.dmp", name_dict=name_dict)

    parasite_taxids = ["554915", "543769", "2611352", "2611341", "2795258", "2686027", "33634", "33630", "33154", "5878", "5794",
                        "6157", "6231", "10232", "85819", "7524", "7147", "7509", "7041", "7399"]
    
    print("Getting all descendant nodes of parasite groups")
    all_descendants = []
    for taxid in parasite_taxids:
        all_descendants += _get_all_descendant_nodes(ncbi_taxonomy, taxid)
    print("Total number of descendant nodes = " + str(len(all_descendants)))

    int_all_descendants = list(map(int, all_descendants))
    sorted_all_descendants = sorted(int_all_descendants)
    sorted_all_descendants = list(map(str, sorted_all_descendants))

    with open('nodes2.dmp', 'w') as w:
        for desc in sorted_all_descendants:
            w.write(nodes_dmp_dict[desc])

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


def get_genealogy(name_object, leaf_node: str) -> List[str]:
    """ Trace genealogy from root to leaf """
    ancestors = []  # Initialise the list of all nodes from root to leaf.
    gen_tax_id = leaf_node  # Define leaf
    while 1:
        if gen_tax_id in name_object:
            ancestors.append(gen_tax_id)
            gen_tax_id = name_object[gen_tax_id].parent  # Move up to parents
        else:
            break
        if gen_tax_id == "1":
            # If it is the root, we reached the end.
            # Add it to the list and break the loop
            ancestors.append(gen_tax_id)
            break
    return ancestors  # Return the list


def _get_all_descendant_nodes(name_object, taxid: str) -> List[str]:
    """ Get all descendant of a node """
    descendant_nodes: List[str] = [taxid]
    if len(name_object[taxid].children) > 0:
        for child in name_object[taxid].children:
            descendant_nodes = descendant_nodes + _get_all_descendant_nodes(name_object, child)
    return descendant_nodes


def _keep_terminal(name_object, nodes_list) -> List[str]:
    """ Keep only terminal nodes """
    terminal_nodes = [x for x in nodes_list if name_object[x].is_tip]
    return terminal_nodes


def _keep_division(name_object, nodes_list, target_division) -> List[str]:
    """ Keep only division nodes """
    division_nodes = [x for x in nodes_list if name_object[x].division == target_division]
    return division_nodes


def get_all_descendants(name_object, target_division: str, taxid: str) -> List[str]:
    """ Get all taxa of a node """

    terminal_nodes = _get_all_descendant_nodes(name_object, taxid)
    terminal_nodes = _keep_division(name_object, terminal_nodes, target_division)

    return terminal_nodes  # Return a list


def get_common_ancestor(name_object, node_list: List[str]):
    """
    Function to find common ancestor between two nodes or more

    Args:
        name_object (name_object): taxonomy to use
        node_list (list): list of node

    Returns:
        node (str): node of the common ancestor between nodes
    """

    # global name_object
    list1 = get_genealogy(
        name_object, node_list[0]
    )  # Define the whole genealogy of the first node
    ancestral_list: List[str] = []
    for node in node_list:
        list2 = get_genealogy(
            name_object, node
        )  # Define the whole genealogy of the second node
        ancestral_list = []
        for taxid in list1:
            if taxid in list2:  # Identify common nodes between the two genealogy
                ancestral_list.append(taxid)
        list1 = ancestral_list  # Reassigning ancestral_list to list 1.
    last_common_ancestor = ancestral_list[
        0
    ]  # Finally, the first node of the ancestral_list is the common ancestor of all nodes.
    return last_common_ancestor  # Return a node


def load_ncbi_names(filename: str = "names.dmp") -> Tuple[Dict, Dict]:
    """Load NCBI names definition ("names.dmp")

    Args:
        filename (str): filename of NCBI names

    Returns:
        name_dict, name_dict_reverse

    """

    name_dict = {}  # Initialise dictionary with TAX_ID:NAME
    name_dict_reverse = {}  # Initialise dictionary with NAME:TAX_ID

    LOGGER.warning(f"Load {filename}")
    name_file = open(filename, "r")
    while 1:
        line = name_file.readline()
        if line == "":
            break
        line = line.rstrip()
        line = line.replace("\t", "")
        tab = line.split("|")
        if tab[3] == "scientific name":
            tax_id, name = tab[0], tab[1]  # Assign tax_id and name ...
            name_dict[tax_id] = name  # ... and load them
            name_dict_reverse[name] = str(tax_id)  # ... into dictionaries
    name_file.close()
    return name_dict, name_dict_reverse


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

    LOGGER.warning(f"Load {filename}")
    taxonomy_file = open(filename, "r")
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
            children_list = name_object[
                tax_id_parent
            ].children  # If parent is in the object
        else:
            name_object[tax_id_parent] = Node()
            name_object[tax_id_parent].tax_id = tax_id_parent  # Assign tax_id
        children_list.append(tax_id)  # ... we found its children.
        name_object[
            tax_id_parent
        ].children = children_list  # ... so add them to the parent

        # As the parent node is found, it is not a terminal node then
        name_object[tax_id_parent].is_tip = False

    taxonomy_file.close()

    return name_object, nodes_dmp_dict

if __name__ == "__main__":
    main()
