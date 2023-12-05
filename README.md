# GLEIF
Python utilities for Legal Entity Identifiers (LEI).  Includes method for validating a LEI including the checksum, and enriching the BIC-LEI mapping csv with additional LEI fields.

## Table of Contents
- [Prerequisites](#prerequisities)
- [Installation](#installation)
- [Usage](#usage)
- [Examples](#examples)

## Prerequisites
- Python 3.10 or higher
- PIP pandas, pprint
- Windows operating system

## Installation
1. Clone the repository:  git clone https://github.com/domdigby/GLEIF.git
2. Run in python venv or python IDE

## Usage

To use the GLEIF utilties, follow these steps:

1. In main.py, below line "if __name__ == '__main__':", uncomment the line of code to run.
2. When running "enrich_bic_lei_csv_map", change the filepath to your location of the lei-bic csv file.
3. For the other methods, use the relevant BIC, LEI or LEI field value you wish to check or process.

## Examples
- The lei-bic mapping csv file, available from https://www.gleif.org/en/lei-data/lei-mapping/download-bic-to-lei-relationship-files
currently has 22447 rows of mapped BIC/LEI (as at Nov 2023).  If using a BIC to get the LEI, the mapping could be many-to-many and therefore
it may return multiple LEIs for the given BIC.

- The mapping csv file only has the LEI itself and therefore if multiple are returned for the BIC, it is not easy to know which LEI to use.
The "enrich_bic_lei_csv_map" method therefore creates a new csv and adds 6 additional columns for each LEI to help identify the organasition for the LEI.
The 6 additional fields are, legal name, legal address (address1, city, country & postal code) and status of the LEI.
These additional fields provide a clearer difference between LEIs when more than one are returned for the BIC.

To create an enriched lei-bic mapping csv file (change the path to your own location of the original lei-bic csv mapping file:

enrich_bic_lei_csv_map(r'C:\Users\domdi\Documents\My Work Files\SWIFT\LEI\lei-bic-20231124T000000.csv', batch_size=100)
