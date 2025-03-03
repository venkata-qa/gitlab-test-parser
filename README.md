# GitLab API Test Data Generator

This repository contains a Python script that interacts with GitLab to fetch repository details, parse feature files, and generate test data in CSV format. The script is designed to automate the process of extracting test case details from GitLab repositories and organizing them into a structured format for further use.

## Table of Contents
- [Prerequisites](#prerequisites)
- [Repository Structure](#repository-structure)
- [How to Run the Script](#how-to-run-the-script)
- [Expected Outputs](#expected-outputs)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Support](#support)

## Prerequisites
Before running the script, ensure you have the following installed:

- **Python 3.7 or higher**
- Required Python packages:
  ```sh
  pip install requests pyyaml
  ```
- A **valid GitLab API token** with access to the repositories you want to query.
- A **JSON file (`api_with_scenarios.json`)** containing the API configurations to process.

## Repository Structure
The repository is organized as follows:

```
project/
├── main.py                  # Main script to execute the workflow
├── feature_parser.py        # Parses feature files to extract test case details
├── gitlab_api.py            # Handles GitLab API interactions
├── utils.py                 # Utility functions for logging, CSV generation, etc.
├── config.py                # Configuration constants (e.g., GitLab URL, API token)
├── README.md                # This file
└── api_with_scenarios.json  # Input JSON file containing API configurations
```

## How to Run the Script

### Clone the Repository:
```sh
git clone <repository-url>
cd <repository-folder>
```

### Install Dependencies:
```sh
pip install -r requirements.txt
```

### Prepare the Input JSON File:
Create a file named `api_with_scenarios.json` in the root directory and add API configurations in the following format:

```json
[
  {
    "api_number": "API123",
    "sc_no": "TC001"
  },
  {
    "api_number": "API456",
    "sc_no": "TC002"
  }
]
```

### Update Configuration:
Open `config.py` and update the following variables:

```python
GITLAB_URL = "https://gitlab.example.com"  # Replace with your GitLab instance URL
TOKEN = "your-gitlab-api-token"           # Replace with your GitLab API token
```

### Run the Script:
```sh
python main.py
```

## Expected Outputs
The script performs the following tasks and generates the following outputs:

### Logs:
All actions and errors are logged to the console in the following format:

```
2023-10-10 12:34:56 - INFO - Processing API number: API123
2023-10-10 12:34:58 - INFO - Repository found: API123-cucumber-test
```

### CSV Files:
For each repository type (corp or dmz), a CSV file is generated or updated in the `corp/csv` or `dmz/csv` directory.

**Example CSV file (`corp_test_data.csv`):**
```
api_number,service_name,consumer_name,tc_no,request_type,uri,content_type,query_params,uri_params,headers,kong_config_id,payload_file_path,expected_http_code
API123,ServiceA,ConsumerA,TC001,POST,/api/v1/resource,application/json,param1=value1,idType=nino,Authorization=Bearer token,kong-123,corp/apis/API123/payload/payload.json,200
```

### Feature and Payload Files:
Feature files and payload files are saved in the following directories:
```
corp/apis/API123/API123.feature
corp/apis/API123/payload/payload.json
```

### Error Logs:
If a repository or file is missing, it is logged in `missing_repos.csv` or `missing_params.csv`.

## Configuration

### `config.py`
Contains constants like `GITLAB_URL` and `TOKEN`. Update these values to match your GitLab instance and API token.

### `api_with_scenarios.json`
Contains the list of API numbers and test case numbers to process. Add or modify entries as needed.

## Troubleshooting

### Import Errors:
- Ensure all Python files are in the same directory.
- Check for typos in function or file names.

### GitLab API Errors:
- Verify that the GitLab URL and API token are correct.
- Ensure the token has sufficient permissions to access the repositories.

### Missing Files:
- Ensure `api_with_scenarios.json` exists and is properly formatted.
- Check the logs for missing repositories or files.

### CSV File Not Generated:
- Ensure the script has write permissions to the `corp/csv` and `dmz/csv` directories.

## Support
For any issues or questions, please open an issue in the repository or contact the maintainer.

