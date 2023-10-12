import mysql.connector
import requests
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# MySQL database settings
mysql_host = "gtg-mysql-dev.mysql.database.azure.com"
mysql_database = "gtgaccountstore"
mysql_user = "<Your MySQL Username>"
mysql_password = "<Your MySQL Password>"

# Initialize the MySQL database connection
mysql_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_password,
    database=mysql_database,
)

# Query MySQL to retrieve email addresses with a license value of 1
cursor = mysql_connection.cursor()
query = "SELECT email FROM gtgaccountstore.licenses WHERE license = 1"
cursor.execute(query)
email_addresses = cursor.fetchall()
cursor.close()

# Azure Key Vault settings
key_vault_name = "gtgkeyvault"
secret_name_graph_api_token = "gtgapplication-adtoken"

# Initialize Azure credentials
credential = DefaultAzureCredential()

# Initialize Key Vault client
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Retrieve Graph API access token from Key Vault
access_token = secret_client.get_secret(secret_name_graph_api_token).value

# Create webhooks for each email address
for email in email_addresses:
    email = email[0]  # Extract the email address from the tuple

    # Define the webhook subscription payload
    subscription_payload = {
        "changeType": "created",
        "notificationUrl": "http://website.com:5000",  # Replace with your actual HTTP listener URL
        "resource": f"/users/{email}/messages",
        "expirationDateTime": "2023-12-31T00:00:00Z",
    }

    # Create the webhook subscription using the Microsoft Graph API
    webhook_url = f"https://graph.microsoft.com/v1.0/subscriptions"
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    response = requests.post(webhook_url, json=subscription_payload, headers=headers)

    if response.status_code == 201:
        print(f"Webhook created for email address: {email}")
    else:
        print(f"Failed to create webhook for email address: {email}")
        print(response.json())

# Close the MySQL database connection
mysql_connection.close()
