## -------------------------------------------------------------------------------------
## Created By: Irsyaad Hasif (hasifirsyaad@gmail.com)
## Created On: 26 Apr 2022 
## Version: 1.0
## -------------------------------------------------------------------------------------
## This script visualises the input Newick tree as a radial taxonomy tree in svg format.
## -------------------------------------------------------------------------------------

# Setting installation folder
dir.create(Sys.getenv("R_LIBS_USER"), recursive = TRUE)
.libPaths(Sys.getenv("R_LIBS_USER"))

# Installing required packages
packages = c("pacman", "BiocManager")
package.check <- lapply(
  packages,
  FUN = function(x) {
    if (!require(x, character.only = TRUE)) {
      install.packages(x, dependencies = TRUE, lib = Sys.getenv("R_LIBS_USER"))
    }
  }
)
pacman::p_load(rio, janitor, lubridate, epikit, skimr, ggplot2, ggtree, ggtreeExtra, plotly, svglite, tibble)
BiocManager::install("treeio", force = TRUE, lib = Sys.getenv("R_LIBS_USER"))

args <- commandArgs(trailingOnly = TRUE) # requires ETE3-generated newick tree + Kraken2/Bracken report

if (length(args) == 0) {
  stop("No input tree file found. Please specify an input tree file.", call. = FALSE)
} else if (length(args) == 1) {
  stop("No input Kraken2/Bracken report file found. Please specify an input Kraken2/Bracken report file.", call. = FALSE)
} else if (length(args) == 2) {
  args[3] = "radial_tree.svg"
}

# Importing Kraken2/Bracken sample report output format and ETE3-generated Newick taxonomy tree
tree <- treeio::read.nhx(args[1])
report <- import(args[2])
colnames(report) <- c("percentage_cover", "num_cover", "num_direct", "rank_code", "ncbi_taxid", "sci_name")
report <- select(report, ncbi_taxid, sci_name, rank_code, num_direct)

# Filtering phyla data
tibble <- as_tibble(tree)
tibble_phyla <- filter(tibble, tibble$rank == "phylum")
colnames(tibble_phyla)[7] <- "Phyla"

# Visualising radial tree
p <- ggtree(tree, layout = "circular", branch.length = "none") +
     geom_tippoint(color = "black", size = 1) +
     geom_hilight(data = tibble_phyla, mapping = aes(node = node, fill = Phyla), alpha = 0.5) +
     geom_fruit(
      data = report,
      mapping = aes(x = num_direct, y = ncbi_taxid),
      geom = geom_bar,
      orientation = "y",
      stat = "identity",
      fill = "black") +
     theme(
      legend.position = "right",
      legend.title = element_text(face = "bold", size = 10),
      legend.text = element_text(size = 8))

ggsave(args[3])