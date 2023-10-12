import subprocess

# Install .NET Core
def install_dotnet_core():
    print("Installing .NET Core...")
    try:
        subprocess.run(
            ["sudo", "apt-get", "update"], check=True
        )
        subprocess.run(
            ["sudo", "apt-get", "install", "dotnet-sdk-3.1", "-y"], check=True
        )
    except Exception as e:
        print(f"Error installing .NET Core: {e}")

# Install Python 3.11
def install_python_311():
    print("Installing Python 3.11...")
    try:
        subprocess.run(
            ["sudo", "add-apt-repository", "ppa:deadsnakes/ppa", "-y"], check=True
        )
        subprocess.run(
            ["sudo", "apt-get", "update"], check=True
        )
        subprocess.run(
            ["sudo", "apt-get", "install", "python3.11", "-y"], check=True
        )
    except Exception as e:
        print(f"Error installing Python 3.11: {e}")

# Install Azure CLI
def install_azure_cli():
    print("Installing Azure CLI...")
    try:
        subprocess.run(
            ["curl", "-sL", "https://aka.ms/InstallAzureCLIDeb | sudo bash"], check=True, shell=True
        )
    except Exception as e:
        print(f"Error installing Azure CLI: {e}")

# Install Azure SDK for Python
def install_azure_sdk_for_python():
    print("Installing Azure SDK for Python...")
    try:
        subprocess.run(
            ["pip3", "install", "azure-mgmt-compute", "azure-mgmt-keyvault", "azure-identity"], check=True
        )
    except Exception as e:
        print(f"Error installing Azure SDK for Python: {e}")

if __name__ == "__main__":
    install_dotnet_core()
    install_python_311()
    install_azure_cli()
    install_azure_sdk_for_python()

    print("Installation completed.")
