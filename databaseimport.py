import mysql.connector
from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient

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
