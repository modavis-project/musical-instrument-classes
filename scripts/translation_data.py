#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: translation_data.py

Description: This script generates a JSON with translations for 2724 musical instruments based on current vocabulary data provided by MIMO (Musical Instrument Museums Online).

Author: Dominik Ukolov
Institution: Research Center DIGITIAL ORGANOLOGY, Leipzig University
Date Created: 11-Aug-2023
Last Updated: 11-Aug-2023
"""

import json
import random
import requests
import time

from lxml import etree

BASE_URL = "https://vocabulary.mimo-international.com/rest/v1/InstrumentsKeywords"
NAMESPACE = {
    "skos": "http://www.w3.org/2004/02/skos/core#",
    "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"
}
MAX_COUNT = -1 # Maximum requests to be processed: Set to -1 for processing all available input data.
WAIT_RANGE = [0.714, 1.273] # Waiting time range in Seconds (s) for next request: prevents high server load.


def get_page_number_from_uri(uri):
    """Extracts the page number from a given URI."""
    return uri.split('/')[-1]

def get_translations(page):
    """Retrieve translations for a given page."""
    translations = {}
    url = f"{BASE_URL}/data?uri=http%3A%2F%2Fwww.mimo-db.eu%2FInstrumentsKeywords%2F{page}&format=application/rdf%2Bxml"
    response = requests.get(url)

    if response.status_code != 200:
        print(f"Failed to retrieve data for URL {url}. Status code: {response.status_code}")
        failed_urls.append(url)
        return None
    else:
        rdf = response.content
        tree = etree.fromstring(rdf)
        namespace = {"skos": "http://www.w3.org/2004/02/skos/core#", "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#"}
        specific_concept = tree.xpath(f'//skos:Concept[@rdf:about="http://www.mimo-db.eu/InstrumentsKeywords/{page}"]', namespaces=namespace)

        if not specific_concept:
            print("No matching concept found")
        else:
            # Only consider direct children of the specific_concept node
            for label in specific_concept[0].xpath('./skos:prefLabel', namespaces=namespace):
                lang = label.get("{http://www.w3.org/XML/1998/namespace}lang")
                value = label.text
                translations[lang] = value
    print(translations)

    return translations

def fetch_hierarchy(page):
    """Fetch the hierarchy data for a given MIMO page number."""
    url = f"{BASE_URL}/hierarchy?uri=http%3A%2F%2Fwww.mimo-db.eu%2FInstrumentsKeywords%2F{page}&lang=en"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for URL {url}. Status code: {response.status_code}")
        failed_urls.append(url)
        return None
    
    return response.json()

def process_hierarchy(hierarchy_data, depth=0, uri=None, page=None):
    """Processes the hierarchy data recursively."""
    if MAX_COUNT != -1 and counter['count'] >= MAX_COUNT:
        return
    if 'broaderTransitive' not in hierarchy_data:
        print('"broaderTransitive" not in hierarchy_data')
        return

    indentation = "-" * depth # indicates current depth level for processing print statement

    uris = hierarchy_data['broaderTransitive'].keys() if uri is None else [uri]
    
    for current_uri in uris:
        if 'narrower' in hierarchy_data['broaderTransitive'][current_uri].keys():
            for child_entry in hierarchy_data['broaderTransitive'][current_uri]['narrower']:
                child_uri = child_entry['uri']
                if 'prefLabel' in child_entry.keys():
                    child_label = child_entry['prefLabel']
                else:
                    child_label = child_entry['label']
                child_page = get_page_number_from_uri(child_uri)
                
                print(f"{indentation} Processing: {child_label}")

                time.sleep(random.uniform(*WAIT_RANGE))

                results.append({
                    'Label': child_label,
                    'Translations': get_translations(child_page),
                    'MIMOPage': child_page
                })

                if MAX_COUNT != -1:
                    counter['count'] += 1
                    if counter['count'] >= MAX_COUNT:
                        print("reached: MAX_COUNT")
                        break

                if child_entry['hasChildren'] == True:
                    child_hierarchy_data = fetch_hierarchy(child_page)
                    process_hierarchy(child_hierarchy_data, depth + 1, child_uri, child_page)
        else:
            child_entry = hierarchy_data['broaderTransitive'][current_uri]
            if 'prefLabel' in child_entry.keys():
                child_label = child_entry['prefLabel']
            else:
                child_label = child_entry['label']

            child_uri = child_entry['uri']
            child_page = get_page_number_from_uri(child_uri)
            
            results.append({
                    'Label': child_label,
                    'Translations': get_translations(child_page),
                    'MIMOPage': child_page
                })
            if child_entry['hasChildren'] == True:
                child_hierarchy_data = fetch_hierarchy(child_page)
                process_hierarchy(child_hierarchy_data, depth + 1, child_uri, child_page)
            
def remove_duplicates(sorted_results):
    """Removes exactly similar entries from list of dictionaries and returns it with unique ones only."""
    seen = set()
    unique_data = []
    for entry in sorted_results:
        serialized = json.dumps(entry, sort_keys=True)

        if serialized not in seen:
            seen.add(serialized)
            unique_data.append(entry)
    return unique_data

def save_json(output_data, filepath='translationsMIMO.json'):
    """Save the provided data as a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(output_data, json_file, indent=4, ensure_ascii=False)


def main():
    """Main script execution."""
    initial_page = '2208' # first page in hierarchy = 2208
    hierarchy_data = fetch_hierarchy(initial_page)
    for i in hierarchy_data['broaderTransitive'].keys():
        uri = hierarchy_data['broaderTransitive'][i]['uri']
        page = get_page_number_from_uri(uri)
        results.append({
                            'Label': hierarchy_data['broaderTransitive'][uri]['prefLabel'],
                            'Translations': get_translations(page),
                            'MIMOPage': page
                        })
        process_hierarchy(hierarchy_data, uri=uri, page=page)

    sorted_results = sorted(results, key=lambda x: x['Label'])
    cleaned_results = remove_duplicates(sorted_results)
    save_json(cleaned_results)
    print("Failed URLs:", failed_urls)

if __name__ == "__main__":
    counter = {'count': 0}  # mutable to maintain state across recursive calls
    failed_urls = []
    results = []
    main()