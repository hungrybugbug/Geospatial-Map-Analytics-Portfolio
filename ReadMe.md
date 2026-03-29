Markdown
# Geospatial Map Analytics Portfolio

## Overview
This repository contains a comprehensive geospatial data analysis portfolio built entirely in Python. The project demonstrates the ability to ingest, clean, project, and visualize spatial data across various geometries (Polygons, Points, Flows/Lines, and Continuous Fields). 

It highlights cartographic theory, illustrating not just *how* to build maps, but answering the conceptual questions of *when* specific map types (Choropleths, Proportional Symbols, Cartograms, etc.) are appropriate and when they are misleading.

## Project Structure
The project is organized into modular scripts and output directories to ensure reproducibility and clean code execution.

```text
main_folder/
│
├── README.md                      # Project documentation
├── Geospatial_Report.pdf          # 8-12 page PDF detailing spatial critiques and justifications
│
├── scripts/                       # Python source code
│   ├── 01_data_and_projections.py # Part 0 (Data ingestion/joins) & Part 1 (Projections)
│   ├── 02_thematic_and_flow_maps.py # Parts 2, 3, & 4 (Choropleth, Proportional, Flow/Network)
│   └── 03_advanced_spatial_analysis.py # Parts 5, 6, & 7 (Interpolation, Cartogram, Scenarios)
│
└── output/                        # Generated deliverables
    ├── figures/                   # High-resolution static maps (.png)
    │   ├── Task1_Projection_Comparison.png
    │   ├── Task2_Choropleth_Comparison.png
    │   ├── Task3_Proportional_Symbols_Static.png
    │   ├── Task4_Flow_Map.png
    │   ├── Task5_Continuous_Field.png
    │   ├── Task6_Area_Correction.png
    │   └── Task7_Scenarios.png
    │
    └── interactive/               # Live web map outputs (.html)
        └── Task3_Proportional_Symbols_Interactive_Bonus.html
Requirements and Installation
To run the scripts in this repository, you will need Python 3.8+ and the following libraries installed.

You can install all dependencies via pip:

Bash
pip install pandas geopandas matplotlib scipy networkx folium mapclassify numpy shapely
How to Run the Code
The scripts are designed to be run sequentially, though they can operate independently as they pull base datasets directly from stable web sources (e.g., Natural Earth) and utilize mock arrays to ensure the pipeline never breaks due to missing local CSV files.

Navigate to the scripts/ directory in your terminal and execute them in order:

python 01_data_and_projections.py

python 02_thematic_and_flow_maps.py

python 03_advanced_spatial_analysis.py

Note: The scripts will automatically output the network summary tables (NetworkX) directly to the console during the execution of script 02.

Features & Extra Credit Implementations
Multiple Geometries: Handles polygon boundaries, point coordinates, origin-destination LineStrings, and rasterized grids.

Network Graphing: Uses networkx to calculate hub centrality, inflows, and outflows.

SciPy Interpolation: Calculates continuous regional thermal fields using cubic grid interpolation.

Interactive Web Mapping: Implements a folium map with hover tooltips and dynamic basemap toggles (Light/Dark mode).

Advanced Binning: Utilizes hexagonal binning (hexbin) for public health density mapping.