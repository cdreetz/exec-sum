#!/bin/bash

# Login to Azure (if not already logged in)
az login

# Variables
RESOURCE_GROUP="doc-sum-rg"
APP_NAME="doc-sum-app"
LOCATION="westus"
SKU="F1"

# Clean up existing resources first
echo "Cleaning up existing resources..."
az group delete --name $RESOURCE_GROUP --yes || true

# Create new resource group
echo "Creating resource group..."
az group create --name $RESOURCE_GROUP --location $LOCATION

# Create App Service plan for Linux
echo "Creating App Service plan..."
az appservice plan create \
    --name ${APP_NAME}-plan \
    --resource-group $RESOURCE_GROUP \
    --sku $SKU \
    --is-linux

# Create web app with Python runtime
echo "Creating web app..."
az webapp create \
    --resource-group $RESOURCE_GROUP \
    --plan ${APP_NAME}-plan \
    --name $APP_NAME \
    --runtime "PYTHON|3.8" \
    --startup-file "./build_script.sh"

# Configure environment variables
echo "Configuring environment variables..."
az webapp config appsettings set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --settings \
    AZURE_ENDPOINT="your-azure-endpoint" \
    AZURE_API_KEY="your-azure-api-key" \
    OPENAI_ENDPOINT="your-openai-endpoint" \
    AZURE_OPENAI_API_KEY="your-openai-api-key" \
    SCM_DO_BUILD_DURING_DEPLOYMENT="true" \
    WEBSITES_PORT="8000"

# Deploy the code
echo "Deploying application..."
az webapp up \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --runtime "PYTHON:3.8" \
    --os-type linux

echo "Deployment complete! Your app should be available at: https://${APP_NAME}.azurewebsites.net"