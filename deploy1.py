import os
import random
import string
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.graphrbac import GraphRbacManagementClient
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties
from azure.mgmt.authorization.models import RoleDefinition
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters

# Replace these values with your specific Azure information
subscription_id = '4a11049c-f1ef-4b33-8fdc-000845f3b37c'
resource_group_name = 'gtg'
managed_identity_name = 'gtgidentity'
app_display_name = 'gtgapplication'

# Generate a random app secret
app_secret = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(32))

# Initialize DefaultAzureCredential
credential = DefaultAzureCredential()

# Initialize clients
authorization_client = AuthorizationManagementClient(credential, subscription_id)
graph_client = GraphRbacManagementClient(credential, subscription_id)

# Create a Managed Identity
scope = '/subscriptions/' + subscription_id + '/resourceGroups/' + resource_group_name
managed_identity = authorization_client.role_assignments.create(
    scope=scope,
    role_assignment_name=managed_identity_name,
    parameters=RoleAssignmentCreateParameters(
        principal_id=graph_client.service_principals.list(filter=f"displayName eq '{managed_identity_name}'").next().object_id,
        role_definition_id=RoleDefinition(
            id='/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/IDENTITY_ASSIGNMENTS',
        ),
    )
)

# Find the service principal with the given display name
service_principal = next(sp for sp in graph_client.service_principals.list() if sp.display_name == managed_identity_name)

# Get the object_id from the service principal
principal_id = service_principal.object_id

# Register an Azure AD app
app = graph_client.applications.create(
    display_name=app_display_name,
    password_credentials=[app_secret],
)

# Add the "SecurityEvents.ReadWrite.All" permission
app_id = app.app_id
permission = graph_client.oauth2PermissionGrants.create(
    filter=f"clientId eq '{app_id}' and resourceAppId eq '00000003-0000-0ff1-ce00-000000000000'",
    consent_type="Principal",
    principal_id=principal_id,
    resource_access=[{
        "resourceAppId": "00000003-0000-0ff1-ce00-000000000000",
        "resource_access": [
            {"id": "a15484ba-e580-490e-b712-07566ed7c2b2", "type": "Scope"},
        ],
    },
    ]
)

# Print the app's client ID and app secret
print(f"Azure AD App Application ID: {app_id}")
print(f"Azure AD App Secret: {app_secret}")
