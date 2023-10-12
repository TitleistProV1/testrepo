import subprocess

# Define the packages to install
packages_to_install = ["azure-keyvault-secrets", "azure-identity"]

# Run the pip install command
for package in packages_to_install:
    install_command = f"pip install {package}"
    subprocess.run(install_command, shell=True, check=True)

# The script will continue after the installation is complete
print("Installation is complete, and the script can continue.")

import os

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
