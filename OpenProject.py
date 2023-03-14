import json
import os

import requests
from dotenv import load_dotenv

BASE_URL = "https://openproject.ksat-stuttgart.de/api/v3/"
NEEDED_FIELDS = ["id", "dueDate", "subject", "description"]
REJECTED_STATUSES = ["Closed", "On hold", "Rejected"]


def get_work_packages():
    # load api key
    load_dotenv()
    api_key = os.environ.get("OPENPROJECT_API_KEY")

    # request data
    data = [{"assigneeOrGroup": {"operator": "=", "values": ["me"]}}]
    url = BASE_URL + "work_packages?filters=" + json.dumps(data)
    r = requests.get(url, auth=("apikey", api_key))
    j = r.json()

    # check for errors
    if j["_type"] == "Error":
        raise RuntimeError(j["message"])

    wps = r.json()["_embedded"]["elements"]
    return [wp for wp in wps if wp["_links"]["status"]["title"] not in REJECTED_STATUSES]
