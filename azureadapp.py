from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.identity import DefaultAzureCredential
from msal import ConfidentialClientApplication

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
