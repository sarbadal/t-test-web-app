"""Simple requests-based API example for end users.

Install once:
	pip install requests

Run:
	python programmatic_api_call.py
"""

import json
from pathlib import Path

import requests


BASE_URL = "http://localhost:5000"
USERNAME = "your_username"
PASSWORD = "your_password"
JSON_FILE = Path("sample_data/test_data_one_sample.json")


def main() -> None:
	session = requests.Session()

	# 1) Login (session cookie is stored in `session`)
	login_resp = session.post(
		f"{BASE_URL}/login",
		data={"username": USERNAME, "password": PASSWORD},
		timeout=30,
	)
	print("Login status:", login_resp.status_code)
	if login_resp.status_code >= 400:
		print("Login failed:", login_resp.text)
		return

	# 2) Upload JSON file to /analyze
	with JSON_FILE.open("rb") as fh:
		analyze_resp = session.post(
			f"{BASE_URL}/analyze",
			headers={"Accept": "application/json"},
			files={"file": (JSON_FILE.name, fh, "application/json")},
			data={
				"confidence": "0.95",
				"dataset_name": "api_dataset",
				"analysis_name": "api_analysis",
			},
			timeout=60,
		)

	print("Analyze status:", analyze_resp.status_code)
	try:
		print(json.dumps(analyze_resp.json(), indent=2))
	except ValueError:
		print(analyze_resp.text)
		return

	# 3) Get latest result as JSON
	latest_resp = session.get(f"{BASE_URL}/api/ttest-result", timeout=30)
	print("Latest result status:", latest_resp.status_code)
	try:
		print(json.dumps(latest_resp.json(), indent=2))
	except ValueError:
		print(latest_resp.text)


if __name__ == "__main__":
	main()
