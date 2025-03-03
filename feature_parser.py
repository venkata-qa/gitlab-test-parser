# feature_parser.py

import logging

def parse_feature_for_testcase(file_path, sc_no):
    """
    Parse the feature file to extract details for a specific test case.
    Handles both direct values and placeholders for fields like HTTP status code.
    """
    logging.info(f"Parsing feature file '{file_path}' for test case '{sc_no}'")
    with open(file_path, "r") as file:
        lines = file.readlines()

    examples_section = False
    headers_row = []
    scenario_details = {}

    for line in lines:
        line = line.strip()

        # Detect the start of the Examples section
        if line.startswith("Examples:"):
            examples_section = True
            continue

        # Extract details from the "When" and "Then" steps
        if line.startswith("When I create a "):
            parts = line.split('"')
            scenario_details["requestType"] = parts[1].upper()  # Extract request type (e.g., POST, GET)

            # Initialize fields with placeholders or default values
            scenario_details["contentType"] = "none"  # Default value
            scenario_details["uriParams"] = "<uriParams>"  # Placeholder without double quotes
            scenario_details["queryParams"] = "<queryParams>"  # Placeholder without double quotes
            scenario_details["headers"] = "<headers>"  # Placeholder without double quotes
            scenario_details["kongId"] = "<kong-id>"  # Placeholder without double quotes
            scenario_details["payload"] = "none"

            # Extract specific fields from the "When" step
            if "content-type" in line:
                # Check if content-type is directly specified in the step
                for idx, part in enumerate(parts):
                    if "content-type" in part.lower() and idx + 1 < len(parts):
                        scenario_details["contentType"] = parts[idx + 1]  # Use the direct value
            if "uri params" in line:
                scenario_details["uriParams"] = line.split("uri params ")[1].split(" ")[0].strip('"')  # Remove double quotes
            if "query params" in line:
                scenario_details["queryParams"] = line.split("query params ")[1].split(" ")[0].strip('"')  # Remove double quotes
            if "headers" in line:
                scenario_details["headers"] = line.split("headers ")[1].split(" ")[0].strip('"')  # Remove double quotes
            if "kong-config-id" in line:
                scenario_details["kongId"] = line.split("kong-config-id ")[1].split(" ")[0].strip('"')  # Remove double quotes

        if line.startswith("Then I receive a response with HTTP status code "):
            parts = line.split('"')
            if len(parts) > 1:
                status_code = parts[1]
                if status_code.isdigit():  # Direct value (e.g., "200")
                    scenario_details["expectedHttpCode"] = status_code
                else:  # Placeholder (e.g., "<status code>")
                    scenario_details["expectedHttpCode"] = f"<{status_code}>"
            if "payload" in line:
                scenario_details["expectedPayload"] = line.split("payload ")[1].split(" ")[0].strip('"')  # Remove double quotes
            if "headers" in line:
                scenario_details["expectedHeaders"] = line.split("headers ")[1].split(" ")[0].strip('"')  # Remove double quotes
            if "content-type" in line:
                scenario_details["expectedContentType"] = line.split("content-type ")[1].split(" ")[0].strip('"')  # Remove double quotes

        # Parse the Examples table
        if examples_section and '|' in line:
            values = [v.strip() for v in line.split('|') if v.strip()]
            if not headers_row:
                headers_row = values  # First row is the headers
            else:
                example_dict = dict(zip(headers_row, values))
                if example_dict.get("tcNo", "").lower() == sc_no.lower():
                    logging.info(f"Test case '{sc_no}' found.")
                    # Debug: Print the example_dict before normalization
                    logging.debug(f"Example dict before normalization: {example_dict}")

                    # Debug: Print the example_dict after normalization
                    logging.debug(f"Example dict after normalization: {example_dict}")

                    # Replace placeholders in scenario_details with values from the Examples table
                    for key, value in example_dict.items():
                        # Debug: Print the key and value being processed
                        logging.debug(f"Processing key: {key}, value: {value}")
                        # Resolve placeholders like "<uriParams>", "<queryParams>", etc.
                        for scenario_key in scenario_details:
                            # Debug: Print the scenario_key and its current value
                            logging.debug(f"Checking scenario_key: {scenario_key}, current value: {scenario_details[scenario_key]}")
                            # Normalize the placeholder to match the key in scenario_details
                            placeholder = f"<{key}>"
                            if key == "kong-id":
                                placeholder = "<kong-id>"  # Match the placeholder in the feature file
                            logging.debug(f"Checking if '{scenario_details[scenario_key]}' matches placeholder '{placeholder}'")
                            if isinstance(scenario_details[scenario_key], str) and scenario_details[scenario_key] == placeholder:
                                logging.debug(f"Replacing placeholder '{scenario_details[scenario_key]}' with value '{value}'")
                                scenario_details[scenario_key] = value

                    # Debug: Print the final scenario_details
                    logging.debug(f"Scenario details after resolving placeholders: {scenario_details}")
                    return scenario_details

    logging.error(f"Test case '{sc_no}' not found in '{file_path}'")
    raise ValueError(f"Test case '{sc_no}' not found.")