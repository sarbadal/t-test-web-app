gcloud auth login
gcloud config set project named-dialect-470311-m3

gcloud functions deploy t-test-analysis \
  --gen2 \
  --region us-central1 \
  --runtime python311 \
  --trigger-http \
  --allow-unauthenticated \
  --entry-point entry_point \
  --source .