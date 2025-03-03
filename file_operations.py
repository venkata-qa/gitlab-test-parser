import os
import csv
import requests
import urllib.parse
import logging
import yaml
from config import HEADERS, GITLAB_URL

def log_missing_repo(api_number, file_path='missing_repos.csv'):
    """Logs missing repositories to a CSV file."""
    file_exists = os.path.exists(file_path)
    with open(file_path, 'a', newline='') as csvfile:
        writer = csv.writer(csvfile)
        if not file_exists:
            writer.writerow(['API Number', 'Status'])
        writer.writerow([api_number, "Repository Not Found"])
    logging.info(f"Logged missing repo for API number '{api_number}'")

def save_feature_file(repo_id, api_number, repo_type):
    """Fetches and saves feature file."""
    feature_path = f"src/test/resources/features/{api_number}.feature"
    encoded_path = urllib.parse.quote(feature_path, safe="")
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
