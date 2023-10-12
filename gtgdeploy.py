from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
import os
from azure.identity import DefaultAzureCredential
from msal import ConfidentialClientApplication
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters, RoleDefinition
from azure.mgmt.compute import ComputeManagementClient
import mysql.connector
from azure.mgmt.mysql import MySQLManagementClient



# Define the Key Vault URL and the name for the secret that will store the tenant ID
KEY_VAULT_URL = "https://gtgkeyvault.vault.azure.net"
TENANT_ID_SECRET_NAME = "azure-ad-tenant-id"

# Use Managed Identity to authenticate to Azure Key Vault
credential = DefaultAzureCredential()
secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

# Capture the Azure AD Tenant ID for the current subscription
try:
    tenant_id = os.environ["AZURE_TENANT_ID"]
    print(f"Captured Azure AD Tenant ID: {tenant_id}")

    # Store the Tenant ID in the Key Vault as a secret
    secret_client.set_secret(TENANT_ID_SECRET_NAME, tenant_id)
    print(f"Tenant ID stored in Key Vault as secret: {TENANT_ID_SECRET_NAME}")
except KeyError:
    print("Azure AD Tenant ID is not available in the environment variables.")

# Capture the Azure AD Tenant Name for the current subscription
try:
    tenant_name = os.environ["AZURE_AD_TENANT_NAME"]
    print(f"Captured Azure AD Tenant Name: {tenant_name}")

    # Store the Tenant Name in the Key Vault as a secret
    secret_name = "azure-ad-tenant-name"  # Name for the secret
    secret_client.set_secret(secret_name, tenant_name)
    print(f"Tenant Name stored in Key Vault as secret: {secret_name}")
except KeyError:
    print("Azure AD Tenant Name is not available in the environment variables.")

# You can now retrieve the Tenant ID and Tenant Name from the Key Vault as needed.

# Azure AD Application Details
application_name = "gtgapplication"
desired_permission = "SecurityEvents.ReadWrite.All"
key_vault_name = "gtgkeyvault"

# Initialize Azure credentials
credential = DefaultAzureCredential()

# Define Azure AD Application registration parameters
tenant_id = "<Your Azure AD Tenant ID>"  # Replace with your Azure AD Tenant ID
authority_uri = f"https://login.microsoftonline.com/{tenant_id}"

# Define the resource (Graph API) and scope (desired permission)
resource_uri = "https://graph.microsoft.com"
scopes = [f"{resource_uri}/.default"]

# Generate a random client ID and client secret
import random
import string

client_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))
client_secret = ''.join(random.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(64))

# Register the Azure AD application
app = ConfidentialClientApplication(
    client_id=client_id,
    client_credential=client_secret,
    authority=authority_uri
)

# Register the application
app_registration_result = app.register_scope("api://" + client_id + "/access_as_user")
app_registration_result = app.register_scope(desired_permission)

# Obtain an Azure AD token
result = app.acquire_token_silent(scopes, account=None)
if not result:
    result = app.acquire_token_for_client(scopes=scopes)

# Check if the token was successfully obtained
if "access_token" in result:
    access_token = result["access_token"]

    # Get the object ID of the registered application
    from azure.identity import ManagedIdentityCredential
    from azure.graphrbac import GraphRbacManagementClient

    managed_identity_credential = ManagedIdentityCredential()
    graph_client = GraphRbacManagementClient(managed_identity_credential, tenant_id)
    application = graph_client.applications.get(client_id)
    object_id = application.object_id

    # Store Object ID, Client ID, Client Secret, and Azure AD Token in Key Vault
    key_vault_uri = f"https://{key_vault_name}.vault.azure.net"
    secret_client = SecretClient(vault_url=key_vault_uri, credential=credential)

    secret_name_object_id = "gtgapplication-objectid"
    secret_name_client_id = "gtgapplication-clientid"
    secret_name_client_secret = "gtgapplication-clientsecret"
    secret_name_ad_token = "gtgapplication-adtoken"

    # Store secrets in Key Vault
    secret_client.set_secret(secret_name_object_id, object_id)
    secret_client.set_secret(secret_name_client_id, client_id)
    secret_client.set_secret(secret_name_client_secret, client_secret)
    secret_client.set_secret(secret_name_ad_token, access_token)

    print(f"Azure AD Application '{application_name}' registered with Object ID: {object_id}")
    print(f"Client ID, Client Secret, and Azure AD Token stored in Key Vault '{key_vault_name}'")
else:
    print("Failed to obtain Azure AD token.")
    
# Define your Azure subscription ID and resource group and names
subscription_id = "YOUR_SUBSCRIPTION_ID"
resource_group_name = "gtg"
identity_name = "gtgidentity"
app_server_name = "gtgappserver"
key_vault_name = "gtgkeyvault"
mysql_server_name = "gtgmysql"

# Initialize Azure credentials
credential = DefaultAzureCredential()

# Create Managed Identity
identity_client = ManagedIdentityClient(credential)
identity = identity_client.create_managed_identity(resource_group_name, identity_name)

# Assign the Managed Identity to the App Service (gtgappserver)
compute_client = ComputeManagementClient(credential, subscription_id)
app_server = compute_client.virtual_machines.get(resource_group_name, app_server_name)

app_server.identity = {
    "type": "SystemAssigned"
}
compute_client.virtual_machines.create_or_update(resource_group_name, app_server_name, app_server)

# Assign permissions to the Managed Identity
authorization_client = AuthorizationManagementClient(credential, subscription_id)

# Assign permissions to Key Vault (gtgkeyvault)
key_vault_scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.KeyVault/vaults/{key_vault_name}"
role_assignment_key_vault = RoleAssignmentCreateParameters(
    role_definition_id="/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7",  # Reader Role ID
    principal_id=identity.principal_id,
)
authorization_client.role_assignments.create(key_vault_scope, uuid.uuid4(), role_assignment_key_vault)

# Assign permissions to MySQL Server (gtgmysql)
mysql_scope = f"/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}/providers/Microsoft.DBforMySQL/servers/{mysql_server_name}"
role_assignment_mysql = RoleAssignmentCreateParameters(
    role_definition_id="/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/acdd72a7-3385-48ef-bd42-f606fba81ae7",  # Reader Role ID
    principal_id=identity.principal_id,
)
authorization_client.role_assignments.create(mysql_scope, uuid.uuid4(), role_assignment_mysql)

print(f"Managed Identity '{identity_name}' created and assigned to '{app_server_name}' with permissions to Key Vault and MySQL Server.")

# Azure Key Vault configuration
key_vault_url = 'https://gtgkeyvault.vault.azure.net'
secret_name = 'mysql-admin-password'

# Define the MySQL database connection configuration
db_config = {
    "host": "gtgmysql",
    "user": "gtgmysql_admin",
    "password": "mysql-admin-password"
    "database": "gtgmysql",
}

try:
    # Initialize the Azure Key Vault client
    credential = DefaultAzureCredential()
    secret_client = SecretClient(vault_url=key_vault_url, credential=credential)

    # Retrieve the MySQL admin password from the Key Vault
    db_config["password"] = secret_client.get_secret(secret_name).value

    # Connect to the MySQL database
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    # Import SQL files (e.g., gtgaccountstore.sql and gtgapp.sql)
    with open("gtgaccountstore.sql", "r") as sql_file:
        sql_script = sql_file.read()
        cursor.execute(sql_script)

    with open("gtgapp.sql", "r") as sql_file:
        sql_script = sql_file.read()
        cursor.execute(sql_script)

    connection.commit()
    print("SQL files imported successfully.")

except mysql.connector.Error as error:
    print(f"MySQL Error: {error}")
except Exception as e:
    print(f"Error: {e}")
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("Database connection closed.")

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

