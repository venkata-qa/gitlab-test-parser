# utils.py

import os
import csv
import logging
import urllib.parse
from urllib.parse import urlparse, urlunparse, parse_qs, urlencode

def log_missing_repo(api_number, missing_repos_csv='missing_repos.csv'):
    """
    Log missing repositories to a CSV file.
    """
    file_exists = os.path.exists(missing_repos_csv)
    with open(missing_repos_csv, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['API Number', 'Status'])
        writer.writerow([api_number, "Repository Not Found"])
    logging.info(f"Logged missing repo for API number '{api_number}'")

def parse_params(params_str):
    """
    Convert a string of key-value pairs (e.g., "idType=nino,idValue=SC012822") into a dictionary.
    """
    if not params_str or params_str.lower() == "none":
        return {}
    return dict(pair.split("=") for pair in params_str.split(","))

def replace_uri_placeholders(uri_path, uri_params, query_params):
    """
    Replace placeholders in the URI path with values from uri_params and query_params.
    Remove query parameters that don't have values.
    """
    # Mapping between placeholders in the URI and keys in query_params
    placeholder_mapping = {
        "esn": "empSeqNo",  # Map {empSeqNo} in URI to "esn" in query_params
        # Add other mappings if needed
    }

    # Replace URI path placeholders (e.g., {idType}, {idValue})
    for key, value in uri_params.items():
        placeholder = f"{{{key}}}"  # Placeholder format: {key}
        uri_path = uri_path.replace(placeholder, value)

    # Replace query parameter placeholders (e.g., {taxYear}, {fromDate})
    for key, value in query_params.items():
        # Check if the key has a mapped placeholder name
        mapped_placeholder = f"{{{placeholder_mapping.get(key, key)}}}"
        if mapped_placeholder in uri_path:
            uri_path = uri_path.replace(mapped_placeholder, value)

    # Remove query parameters that don't have values
    parsed_url = urlparse(uri_path)
    query_dict = parse_qs(parsed_url.query)

    # Filter out query parameters that don't have values
    filtered_query_dict = {k: v for k, v in query_dict.items() if k in query_params}

    # Rebuild the URI path
    updated_query = urlencode(filtered_query_dict, doseq=True)
    updated_uri = urlunparse(parsed_url._replace(query=updated_query))

    return updated_uri

def generate_csv(data, repo_type):
    """
    Generate or update a CSV file with the test data.
    """
    fields = [
        "api_number", "service_name", "consumer_name", "tc_no", "request_type", "uri", "content_type", "query_params",
        "uri_params", "headers", "kong_config_id", "payload_file_path", "expected_http_code"
    ]
    local_dir = f"{repo_type}/csv"
    os.makedirs(local_dir, exist_ok=True)
    csv_path = os.path.join(local_dir, f"{repo_type}_test_data.csv")

    write_header = not os.path.exists(csv_path)
    with open(csv_path, "a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fields)
        if write_header:
            writer.writeheader()
        writer.writerow(data)

    logging.info(f"CSV updated at: {csv_path}")