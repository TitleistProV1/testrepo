import subprocess

# Define the packages you want to install
packages_to_install = ["azure-keyvault-secrets", "azure-identity"]

# Run the pip install command
for package in packages_to_install:
    install_command = f"pip install {package}"
    subprocess.run(install_command, shell=True, check=True)

# The script will continue after the installation is complete
print("Installation is complete, and the script can continue.")

from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

credential = DefaultAzureCredential()

secret_client = SecretClient(vault_url="https://my-key-vault.vault.azure.net/", credential=credential)
secret = secret_client.set_secret("secret-name", "secret-value")

print(secret.name)
print(secret.value)
print(secret.properties.version)
