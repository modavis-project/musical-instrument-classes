# Hornbostel-Sachs Classifications and Musical Instruments Translation Database (JSON) 

This repository offers a structured representation of the Hornbostel-Sachs Classification System for Musical Instruments in a JSON format, primarily designed to facilitate advanced integration with Large Language Models (LLMs) and Prompt-Based Segmentation Models. The database is augmented with multilingual translations of 2724 instrument names, sourced from [MIMO (Musical Instrument Museums Online)](https://mimo-international.com/MIMO/).

## Features:

- **Structured Hornbostel-Sachs Classification**: A detailed JSON representation of the current Hornbostel-Sachs classification system, allowing for structured data queries and integration. Each classification contains:
  - **Label**: Name of classification.
  - **Instruments**: List of class-related instruments.
  - **Description**: Description of the classification.
  - **MIMOPage**: Reference page to the source on MIMO.
   
- **Multilingual Translation Data**: The database encompasses multilingual translations of instrument names, ensuring its utility for international academic and research endeavors, especially for text-based provenance research activities. Each entry contains:
  - **Label**: Primary name of the instrument in the source language.
  - **Translations**: Dictionary containing translations of the instrument name in multiple languages (e.g., "zh", "sv", "en").
  - **MIMOPage**: Reference page to the source on MIMO.

- **Data Retrieval Scripts**: The repository incorporates scripts to retrieve the current state of classifications or translations based on MIMO. This ensures transparency and offers researchers the possibility to replicate or adapt the data collection process.


## Data Source:

All data within this repository has been responsibly retrieved from [MIMO](https://mimo-international.com/MIMO/), which is a consortium of musical instrument museums and a provider for the [Europeana](https://europeana.eu/).

## Potential Applications:

- Augmenting Large Language Models (LLMs) with specialized knowledge of musical instrument classifications.
- Augmenting Prompt-Based Visual Segmentation by detailed Class Descriptions.
- Structured data extraction tasks for academic projects and research studies.
- Provenance research, working with multilingual data on text-based sources for object provenances.
- Tools and platforms aiming to foster a nuanced understanding of global musical heritage, leveraging multilingual data.
