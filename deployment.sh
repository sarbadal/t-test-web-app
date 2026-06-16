gcloud auth login
gcloud config set project <my-project-id>

gcloud functions deploy <function-name> \
  --gen2 \
  --region <region> \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point entry_point \
  --source .

# Programmatically get the result of the t-test
# This app currently supports:

# 1. Login to get a session cookie
# 2. POST /analyze with multipart form data and a JSON file
# 3. GET endpoints to fetch result/history as JSON

# How to call it from curl

# Login and save cookie

curl -i -c cookies.txt -X POST http://localhost:5000/login
-d "username=your_username"
-d "password=your_password"

# Run analysis by uploading JSON file

curl -i -b cookies.txt -X POST http://localhost:5000/analyze
-H "Accept: application/json"
-F "file=@sample_data/test_data_one_sample.json;type=application/json"
-F "confidence=0.95"
-F "dataset_name=my_dataset"
-F "analysis_name=my_analysis"

# Get latest analysis result payload (full wrapper response)

curl -i -b cookies.txt http://localhost:5000/api/ttest-result

# Optional: list analyses

curl -i -b cookies.txt "http://localhost:5000/api/analyses?limit=20"