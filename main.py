# main.py

import logging
import json
from config import LOGGING_CONFIG
from gitlab_api import get_repo_id, find_repo_by_api_number, save_feature_file, fetch_payload_file, fetch_yaml_config
from feature_parser import parse_feature_for_testcase
from utils import log_missing_repo, parse_params, replace_uri_placeholders, generate_csv

# Configure logging
logging.basicConfig(**LOGGING_CONFIG)

def process_api_config(config):
    """
    Process a single API configuration from the JSON file.
    """
    api_number = config["api_number"]
    sc_no = config["sc_no"]
    logging.info(f"Processing API number: {api_number}")

    # Find repository by API number
    repo_name = find_repo_by_api_number(api_number)
    if not repo_name:
        logging.warning(f"Skipping API number '{api_number}' due to missing repo.")
        log_missing_repo(api_number)
        return

    # Determine repository type (corp or dmz)
    repo_type = "corp" if "-corp-" in repo_name else "dmz"
    logging.info(f"Repository type: {repo_type}")

    # Fetch repository ID
    repo_id = get_repo_id(repo_name)
    if not repo_id:
        logging.warning(f"Skipping API number '{api_number}' due to missing repo ID.")
        log_missing_repo(api_number)
        return

    # Save feature file
    feature_file = save_feature_file(repo_id, api_number, repo_type)
    if not feature_file:
        logging.warning(f"Skipping API number '{api_number}' due to missing feature file.")
        return

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
        return

    # Parse URI and query parameters
    uri_params_str = testcase_details.get("uriParams", "none")
    query_params_str = testcase_details.get("queryParams", "none")
    uri_params = parse_params(uri_params_str)
    query_params = parse_params(query_params_str)

    # Replace placeholders in the URI path
    uri_path = yaml_config['uri']  # Get the URI path from the YAML config
    updated_uri_path = replace_uri_placeholders(uri_path, uri_params, query_params)
    logging.info(f"Updated URI path: {updated_uri_path}")

    # Prepare CSV data
    csv_data = {
        "api_number": api_number,
        "service_name": yaml_config['kongConfig'][0]['serviceName'],
        "consumer_name": yaml_config['kongConfig'][0]['consumerName'],
        "tc_no": sc_no,
        "request_type": testcase_details.get("requestType", "UNKNOWN"),
        "content_type": testcase_details.get("contentType", "UNKNOWN"),
        "uri": updated_uri_path,  # Use the updated URI path
        "query_params": testcase_details.get("queryParams", "none"),
        "uri_params": testcase_details.get("uriParams", "none"),
        "headers": testcase_details.get("headers", "none"),
        "kong_config_id": testcase_details.get("kongId", "none"),
        "payload_file_path": payload_path,
        "expected_http_code": testcase_details.get("expectedHttpCode", "UNKNOWN")
    }

    # Generate or update CSV
    generate_csv(csv_data, repo_type)
    logging.info(f"Completed processing for API number: {api_number}")

if __name__ == "__main__":
    # Load API configurations from JSON file
    with open('api_with_scenarios.json', 'r') as file:
        repo_configs = json.load(file)

    # Process each API configuration
    for config in repo_configs:
        process_api_config(config)