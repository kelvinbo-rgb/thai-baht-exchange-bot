# Deployment script for Thai Baht Exchange Bot

$PROJECT_ID = "thai-baht-exchange-bot" # You might need to change this if you have a different project ID preference or let it auto-create
$SERVICE_NAME = "thai-baht-exchange-bot"
$REGION = "asia-southeast1" # Bangkok region usually slightly more expensive or unavailable, Singapore (asia-southeast1) is standard good choice

# Check if logged in
Write-Host "Checking gcloud auth..."
gcloud auth list

# Set project (optional, or rely on current config)
# gcloud config set project $PROJECT_ID

# Build and Submit
Write-Host "Building and submitting to Cloud Build..."
gcloud builds submit --tag gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy
Write-Host "Deploying to Cloud Run..."
gcloud run deploy $SERVICE_NAME `
  --image gcr.io/$PROJECT_ID/$SERVICE_NAME `
  --platform managed `
  --region $REGION `
  --allow-unauthenticated `
  --memory 512Mi `
  --concurrency 80 
