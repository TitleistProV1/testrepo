import random
import string
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties
from azure.mgmt.authorization.models import RoleDefinition
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from azure.graphrbac import GraphRbacManagementClient

# Specify your Azure subscription ID and resource group name
subscription_id = '4a11049c-f1ef-4b33-8fdc-000845f3b37c'
resource_group_name = 'gtg'

# Generate a random password for the Azure AD app
app_secret = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

# Initialize the DefaultAzureCredential, which will use Managed Identity if available
credential = DefaultAzureCredential()

# Initialize the AuthorizationManagementClient and GraphRbacManagementClient
authorization_client = AuthorizationManagementClient(credential, subscription_id)
graph_client = GraphRbacManagementClient(credential, subscription_id)

# Create a Managed Identity
managed_identity_name = 'gtgidentity'
managed_identity = authorization_client.role_assignments.create(
    scope=f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}',
    role_assignment_name=managed_identity_name,
    parameters=RoleAssignmentCreateParameters(
        principal_id=graph_client.service_principals.list(filter=f"displayName eq '{managed_identity_name}'").next().object_id,
        role_definition_id=RoleDefinition(
            id='/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/IDENTITY_ASSIGNMENTS',
        ),
    )
)

# Register an Azure AD app
app_display_name = 'gtgapp'
app = graph_client.applications.create(
    display_name=app_display_name,
    password_credentials=[app_secret],
)

# Add the required permission (SecurityEvents.ReadWrite.All)
app_id = app.app_id
permission = graph_client.oauth2PermissionGrants.create(
    filter=f"clientId eq '{app_id}' and resourceAppId eq '00000003-0000-0ff1-ce00-000000000000'",
    consent_type="Principal",
    principal_id=managed_identity.principal_id,
    resource_access=[{
        "resourceAppId": "00000003-0000-0ff1-ce00-000000000000",
        "resource_access": [
            {"id": "a15484ba-e580-490e-b712-07566ed7c2b2", "type": "Scope"},
        ],
    }],
)

# Print the app's client ID and secret
print(f"Azure AD App Application ID: {app_id}")
print(f"Azure AD App Secret: {app_secret}")