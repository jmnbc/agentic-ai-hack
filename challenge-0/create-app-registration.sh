#!/bin/bash
set -e

APP_NAME="$1"
if [ -z "$APP_NAME" ]; then
  echo "Usage: $0 <app-name>"
  exit 1
fi

echo "Creating Azure AD app registration: $APP_NAME"
APP_REG=$(az ad app create --display-name "$APP_NAME")
CLIENT_ID=$(echo "$APP_REG" | jq -r '.appId')

echo "Creating service principal for app registration..."
az ad sp create --id "$CLIENT_ID" >/dev/null

# Wait for service principal to be available
for i in {1..12}; do  # up to 1 minute
  SP_SHOW=$(az ad sp show --id "$CLIENT_ID" 2>/dev/null || echo "")
  OBJECT_ID=$(echo "$SP_SHOW" | jq -r '.id')
  if [ "$OBJECT_ID" != "null" ] && [ -n "$OBJECT_ID" ]; then
    break
  fi
  echo "Waiting for service principal to propagate..."
  sleep 5
done

# Fallback: Try to retrieve by display name if still not found
if [ "$OBJECT_ID" == "null" ] || [ -z "$OBJECT_ID" ]; then
  echo "Trying fallback method using display name..."
  OBJECT_ID=$(az ad sp list --filter "displayName eq '$APP_NAME'" --query ".id" -o tsv)
fi

echo "Client ID: $CLIENT_ID"
echo "Service Principal Object ID: $OBJECT_ID"

TENANT_ID=$(az account show | jq -r '.tenantId')

echo "App Registration created."
echo "Client ID: $CLIENT_ID"
echo "Service Principal Object ID: $OBJECT_ID"
echo "Directory (tenant) ID: $TENANT_ID"
