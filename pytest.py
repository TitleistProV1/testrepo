import os
import random
import string
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.authorization.models import RoleAssignmentProperties
from azure.mgmt.authorization.models import RoleDefinition
from azure.mgmt.authorization.models import RoleAssignmentCreateParameters
from azure.mgmt.graphrbac import GraphRbacManagementClient
from azure.mgmt.graphrbac.models import ApplicationCreateParameters
from azure.mgmt.graphrbac.models import PasswordCredential

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
scope = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}'
managed_identity = ManagedIdentityCredential()

# Register an Azure AD app
app_create_params = ApplicationCreateParameters(
    display_name=app_display_name
)
app = graph_client.applications.create(app_create_params)

# Create a password credential for the app (app secret)
password_credential = PasswordCredential(
    start_date="2022-01-01T00:00:00Z",
    end_date="2099-12-31T23:59:59Z",
    value=app_secret
)

graph_client.service_principals.add_password(
    object_id=app.object_id,
    value=password_credential
)

# Assign the role to the Managed Identity
role_definition_id = f'/subscriptions/{subscription_id}/providers/Microsoft.Authorization/roleDefinitions/IDENTITY_ASSIGNMENTS'
role_assignment_name = managed_identity_name
role_assignment = RoleAssignmentCreateParameters(
    role_definition_id=role_definition_id,
    principal_id=managed_identity.principal_id,
)
authorization_client.role_assignments.create(scope, role_assignment_name, role_assignment)

# Grant the "SecurityEvents.ReadWrite.All" permission
permission = graph_client.oauth2PermissionGrants.create(
    filter=f"clientId eq '{app.app_id}' and resourceAppId eq '00000003-0000-0ff1-ce00-000000000000'",
    consent_type="Principal",
    principal_id=managed_identity.principal_id,
    resource_access=[
        {
            "resourceAppId": "00000003-0000-0ff1-ce00-000000000000",
            "resource_access": [{"id": "a15484ba-e580-490e-b712-07566ed7c2b2", "type": "Scope"}],
        }
    ]
)

# Print the app's client ID and app secret
print(f"Azure AD App Application ID (Client ID): {app.app_id}")
print(f"Azure AD App Secret: {app_secret}")
