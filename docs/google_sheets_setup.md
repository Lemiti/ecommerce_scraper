# Google Sheets API Setup Guide

## Step 1: Enable Google Sheets API

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Google Sheets API
   - Google Drive API

## Step 2: Create Service Account Credentials

1. In Google Cloud Console, go to "IAM & Admin" → "Service Accounts"
2. Click "Create Service Account"
3. Enter a name (e.g., "Ecommerce Scraper")
4. Click "Create and Continue"
5. Add role "Editor" (or more restricted roles if preferred)
6. Click "Continue" and then "Done"
7. Click on the newly created service account
8. Go to "Keys" tab
9. Click "Add Key" → "Create New Key"
10. Select "JSON" format and download the key file

## Step 3: Configure the Scraper

1. Create a `configs` folder in your project root if it doesn't exist
2. Place the downloaded JSON file in the `configs` folder
3. Rename it to `credentials.json`

Your project structure should look like: