import mysql.connector
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

# Azure Key Vault settings
key_vault_name = "gtgkeyvault"

# Initialize Azure credentials
credential = DefaultAzureCredential()

# Initialize Key Vault client
key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

# Retrieve MySQL database name and admin password from Key Vault
mysql_database_secret = secret_client.get_secret("gtgmysql-database")
mysql_admin_password_secret = secret_client.get_secret("gtgmysql-admin-password")

# Assign the MySQL database name to mysql_host
mysql_host = mysql_database_secret.value + ".mysql.database.azure.com"
mysql_admin_password = mysql_admin_password_secret.value

# Microsoft Graph API settings
resource_url = "https://graph.microsoft.com/"
api_version = "v1.0"
scopes = [resource_url]

# Initialize the MySQL database connection
mysql_connection = mysql.connector.connect(
    host=mysql_host,
    user=mysql_user,
    password=mysql_admin_password,
    database=mysql_database_name,
)

# Rest of your script
# ...

# Close the MySQL connection when done
mysql_connection.close()
