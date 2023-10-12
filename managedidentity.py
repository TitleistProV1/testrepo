from azure.identity import DefaultAzureCredential
from azure.keyvault.secrets import SecretClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters, RoleDefinition
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.mysql import MySQLManagementClient
from azure.identity import DefaultAzureCredential

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
