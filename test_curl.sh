#!/bin/bash

# Get the auth token from environment
AUTH_TOKEN="$(cat .env | grep SUNBIRD_API_KEY | cut -d '=' -f2)"

# Test root endpoint
echo "Testing root endpoint..."
curl -k -H "Authorization: $AUTH_TOKEN" -H "accept: application/json" https://api.sunbird.ai/

echo "\nTesting STT endpoint with POST..."
curl -k -X POST \
  -H "Authorization: $AUTH_TOKEN" \
  -H "accept: application/json" \
  -F "language=lug" \
  -F "adapter=lug" \
  -F "whisper=true" \
  https://api.sunbird.ai/tasks/stt
