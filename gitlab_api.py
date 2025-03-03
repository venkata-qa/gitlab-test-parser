# gitlab_api.py

import requests
import logging
import time
from urllib.parse import quote
from config import GITLAB_URL, HEADERS

def get_repo_id(repo_name):
    """
    Fetch the repository ID for a given repository name from GitLab.
    """
    logging.info(f"Fetching repository ID for '{repo_name}'")
    response = requests.get(f"{GITLAB_URL}/api/v4/projects?search={repo_name}", headers=HEADERS)
    time.sleep(2)  # Add delay to avoid rate limiting
    if response.status_code == 200:
        repos = response.json()
        repo_id = next((repo['id'] for repo in repos if repo['name'] == repo_name), None)
        if repo_id:
            logging.info(f"Repository '{repo_name}' found with ID: {repo_id}")
        else:
            logging.error(f"Repository '{repo_name}' not found")
        return repo_id
    logging.error(f"Failed to fetch repository ID: {response.status_code}")
    return None

def find_repo_by_api_number(api_number):
    """
    Find a repository by searching for the API number in GitLab.
    """
    logging.info(f"Searching repository for API number '{api_number}'")
    response = requests.get(f"{GITLAB_URL}/api/v4/projects?search={api_number}", headers=HEADERS)
    time.sleep(2)  # Add delay to avoid rate limiting
    if response.status_code == 200:
        repos = response.json()
        repo_name = next((repo['name'] for repo in repos if repo['name'].startswith(api_number) and repo['name'].strip().endswith("-cucumber-test")), None)
        if repo_name:
            logging.info(f"Repository found: {repo_name}")
            return repo_name
    logging.warning(f"No repository found for API number '{api_number}'")
    return None

def save_feature_file(repo_id, api_number, repo_type):
    """
    Save the feature file from the GitLab repository to a local directory.
    """
    feature_path = f"src/test/resources/features/{api_number}.feature"
    encoded_path = quote(feature_path, safe="")
    feature_url = f"{GITLAB_URL}/api/v4/projects/{repo_id}/repository/files/{encoded_path}/raw?ref=master"
    response = requests.get(feature_url, headers=HEADERS)
    if response.status_code == 200:
        local_dir = f"{repo_type}/apis/{api_number}"
        os.makedirs(local_dir, exist_ok=True)
        local_feature_path = os.path.join(local_dir, f"{api_number}.feature")
        with open(local_feature_path, "w") as file:
            file.write(response.text)
        logging.info(f"Feature file saved at: {local_feature_path}")
        return local_feature_path
    logging.error(f"Failed to fetch feature file: {response.status_code}")
    return None

def fetch_payload_file(repo_id, api_number, payload_filename, repo_type):
    """
    Fetch the payload file from the GitLab repository if required.
    """
    if not payload_filename or payload_filename.lower() == "none":
        logging.info("No payload file required for GET request.")
        return "none"
    payload_path = f"src/test/resources/{api_number}/request/{payload_filename}"
    encoded_path = quote(payload_path, safe="")
    url = f"{GITLAB_URL}/api/v4/projects/{repo_id}/repository/files/{encoded_path}/raw?ref=master"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        local_dir = f"{repo_type}/apis/{api_number}/payload"
        os.makedirs(local_dir, exist_ok=True)
        local_payload_path = os.path.join(local_dir, payload_filename)
        with open(local_payload_path, 'w') as file:
            file.write(response.text)
        logging.info(f"Payload file saved: {local_payload_path}")
        return local_payload_path
    logging.error(f"Payload file '{payload_filename}' fetch failed: {response.status_code}")
    return "none"

def fetch_yaml_config(repo_id, api_number):
    """
    Fetch the YAML configuration file from the GitLab repository.
    """
    yaml_path = f"src/test/resources/{api_number}.yml"
    encoded_path = quote(yaml_path, safe="")
    url = f"{GITLAB_URL}/api/v4/projects/{repo_id}/repository/files/{encoded_path}/raw?ref=master"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        return yaml.safe_load(response.text)
    logging.error(f"YAML file fetch failed: {response.status_code}")
    return None