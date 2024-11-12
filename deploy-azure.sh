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

# Wait a moment for cleanup
echo "Waiting for cleanup to complete..."
sleep 30

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
    --runtime "PYTHON|3.8"

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

# Configure the build command
echo "Configuring startup command..."
az webapp config set \
    --resource-group $RESOURCE_GROUP \
    --name $APP_NAME \
    --startup-file "build_script.sh"

# Deploy using local-git instead of zip deploy
echo "Configuring local git deployment..."
az webapp deployment source config-local-git \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP

# Get the git URL
GIT_URL=$(az webapp deployment source config-local-git \
    --name $APP_NAME \
    --resource-group $RESOURCE_GROUP \
    --query url -o tsv)

echo "Git deployment URL: $GIT_URL"
echo "To deploy your code, run:"
echo "git remote add azure $GIT_URL"
echo "git push azure main"

echo "Once deployed, your app will be available at: https://${APP_NAME}.azurewebsites.net"