#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Filename: hornbostelSachs_data.py

Description: This script generates a JSON of the Hornbostel-Sachs classification system for musical instruments based on the current conventional state provided by MIMO (Musical Instrument Museums Online).

Author: Dominik Ukolov
Institution: Research Center DIGITAL ORGANOLOGY, Leipzig University
Date Created: 11-Aug-2023
Last Updated: 11-Aug-2023
"""

import json
import random
import requests
import time

from lxml import html

BASE_URL = "https://vocabulary.mimo-international.com/rest/v1/HornbostelAndSachs"
MAX_COUNT = -1 # Maximum requests to be processed: Set to -1 for processing all available input data.
WAIT_RANGE = [0.714, 1.273] # Waiting time range in Seconds (s) for next request: prevents high server load.

def get_page_number_from_uri(uri):
    """Extracts the page number from a given URI."""
    return uri.split('/')[-1]

def get_description_from_uri(uri):
    """Returns the description of a class."""
    html_response = requests.get(uri)
    if html_response.status_code == 200:
        web_tree = html.fromstring(html_response.content)
        li_texts = web_tree.xpath('//div[contains(@class, "property-value-wrapper")]/ul/li/span/text()')
    return sorted(li_texts, key=len)[-1]

def get_instrument_names_for_page(page):
    """Returns the instruments that are related to the current class."""
    url = f"{BASE_URL}/mappings?uri=http%3A%2F%2Fwww.mimo-db.eu%2FHornbostelAndSachs%2F{page}&lang=en&clang=en"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for URL {url}. Status code: {response.status_code}")
        failed_urls.append(url)
        return []
    
    data = response.json()
    instrument_names = []
    
    if data['mappings'] is not None:
        for i in data['mappings']:
            instrument_names.append(i['prefLabel'])
            
    return instrument_names

def fetch_hierarchy(page):
    """Fetch the hierarchy data for a given MIMO page number."""
    url = f"{BASE_URL}/hierarchy?uri=http%3A%2F%2Fwww.mimo-db.eu%2FHornbostelAndSachs%2F{page}&lang=en"
    response = requests.get(url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve data for URL {url}. Status code: {response.status_code}")
        failed_urls.append(url)
        return None
    
    return response.json()

def process_hierarchy(hierarchy_data, depth=0, uri=None):
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
                child_label = child_entry['label']
                child_notation = child_entry['notation']
                child_description = get_description_from_uri(child_uri)
                child_page = get_page_number_from_uri(child_uri)
                child_instrument_names = get_instrument_names_for_page(child_page)
                print(f"{indentation} Processing: {child_notation}")

                time.sleep(random.uniform(*WAIT_RANGE))

                results[child_notation] = {
                    'Label': child_label,
                    'Instruments': child_instrument_names,
                    'Description': child_description,
                    'MIMOPage': child_page
                }

                if MAX_COUNT != -1:
                    counter['count'] += 1
                    if counter['count'] >= MAX_COUNT:
                        break

                if child_entry['hasChildren'] == True:
                    child_hierarchy_data = fetch_hierarchy(child_page)
                    process_hierarchy(child_hierarchy_data, depth + 1, child_uri)

def sort_results(results):
    """Sorts the results lexicographically by its keys."""
    return dict(sorted(results.items(), key=lambda x: sorted(list(results.keys())).index(x[0])))

def save_json(output_data, filepath='hornbostelSachs.json'):
    """Save the provided data as a JSON file."""
    with open(filepath, 'w', encoding='utf-8') as json_file:
        json.dump(output_data, json_file, indent=4, ensure_ascii=False)


def main():
    """Main script execution."""
    initial_url = f"{BASE_URL}/topConcepts?lang=en"
    response = requests.get(initial_url)

    if response.status_code != 200:
        print(f"Failed to retrieve data for URL {initial_url}. Status code: {response.status_code}")

    data = response.json()
    results = {}

    for item in data['topconcepts']:
        if item['hasChildren'] == True:
            page = get_page_number_from_uri(item['uri'])
            instrument_names = get_instrument_names_for_page(page)
            description = get_description_from_uri(item['uri'])
            notation = item['notation']
            print(" Processing: " + notation)

            results[notation] = {
                                'Label': item['label'],
                                'Instruments': instrument_names,
                                'Description': description,
                                'MIMOPage': page
                            }

            if MAX_COUNT != -1:
                counter['count'] += 1
                if counter['count'] >= MAX_COUNT:
                    break
            hierarchy_data = fetch_hierarchy(page)
            process_hierarchy(hierarchy_data)

    sorted_results = sort_results(results)
    save_json(sorted_results)
    print("Failed URLs:", failed_urls)

if __name__ == "__main__":
    counter = {'count': 0}  # mutable to maintain state across recursive calls
    failed_urls = []
    results = []
    main()