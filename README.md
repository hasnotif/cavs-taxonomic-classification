# CAVS - Taxonomic Classification & Abundance Estimation Pipeline

Note: This pipeline is intended for use on the Centre for Animal and Veterinary Sciences (CAVS) network only.

## About The Pipeline

This pipeline performs taxonomic classification and species-level abundance estimation for query sequences from metagenomic samples. It produces a HTML report that contains a radial taxonomy tree of the classification results.

### Programs Used

_Note: The following programs are already installed on Atlantis and Shambhala._

* [Kraken2](https://github.com/DerrickWood/kraken2) (for taxonomic classification)
* [Bracken](https://github.com/jenniferlu717/Bracken) (for abundance estimation)

### Libraries Used

#### Python
* [ETE3](http://etetoolkit.org/)

  Please follow the instructions [here](http://10.10.1.5/wiki/Taxonomic_Classification_Pipeline#Phase_4:_Generate_HTML_Report) to install this library.

#### R
* [ggtree](https://bioconductor.org/packages/devel/bioc/vignettes/ggtree/inst/doc/ggtree.html)

  This library and its dependencies will be automatically installed upon running the R script for the first time.

### Other Prerequisites

* NCBI API key

  To facilitate parallel batch downloads, please [create an API key](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/) with your NCBI account (if you don't already have one).

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/hasnotif/cavs-taxonomic-classification.git
   ```

2. Make the Python scripts in the cloned repository executable:
   ```
   chmod +x cavs-taxonomic-classification/*.py
   ```
   
## Usage

Please refer to the [CAVS Wiki tutorial page](http://10.10.1.5/wiki/Taxonomic_Classification_Pipeline) to learn how to run the pipeline (ensure that you are connected to the CAVS network first!).

