# main.py

import logging
import json
from config import LOGGING_CONFIG
from gitlab_api import get_repo_id, find_repo_by_api_number, save_feature_file, fetch_payload_file, fetch_yaml_config
from feature_parser import parse_feature_for_testcase
from utils import log_missing_repo, parse_params, replace_uri_placeholders, generate_csv

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)

if __name__ == "__main__":
    with open('api_with_scenarios.json', 'r') as file:
        repo_configs = json.load(file)

    for config in repo_configs:
        api_number = config["api_number"]
        sc_no = config["sc_no"]
        logging.info(f"Processing API number: {api_number}")

        # Find repository by API number
        repo_name = find_repo_by_api_number(api_number)
        if not repo_name:
            logging.warning(f"Skipping API number '{api_number}' due to missing repo.")
            log_missing_repo(api_number)
            continue

        # Determine repository type (corp or dmz)
        repo_type = "corp" if "-corp-" in repo_name else "dmz"
        logging.info(f"Repository type: {repo_type}")

        # Fetch repository ID
        repo_id = get_repo_id(repo_name)
        if not repo_id:
            logging.warning(f"Skipping API number '{api_number}' due to missing repo ID.")
            log_missing_repo(api_number)
            continue

        # Save feature file
        feature_file = save_feature_file(repo_id, api_number, repo_type)
        if not feature_file:
            logging.warning(f"Skipping API number '{api_number}' due to missing feature file.")
            continue

        # Parse feature file for test case details
        testcase_details = parse_feature_for_testcase(feature_file, sc_no)
        logging.info(f"Test case details: {testcase_details}")

        # Fetch payload file if required
        payload_filename = testcase_details.get("payload")
        payload_path = fetch_payload_file(repo_id, api_number, payload_filename, repo_type)
        logging.info(f"Payload file path: {payload_path}")

        # Fetch YAML configuration
        yaml_config = fetch_yaml_config(repo_id, api_number)
        if not yaml_config:
            logging.warning(f"Skipping API number '{api_number}' due to missing YAML config.")
            continue
    
        uri_params_str = testcase_details.get("uriParams", "none")
        query_params_str = testcase_details.get("queryParams", "none")
        
        # Parse into dictionaries
        uri_params = parse_params(uri_params_str)
        query_params = parse_params(query_params_str)
        
        logging.info(f"Test case details: {query_params}")

        # Replace placeholders in the URI path
        uri_path = yaml_config['uri']  # Get the URI path from the YAML config
        updated_uri_path = replace_uri_placeholders(uri_path, uri_params, query_params)

        # Log or use the updated URI path
        logging.info(f"Updated URI path: {updated_uri_path}")

        #