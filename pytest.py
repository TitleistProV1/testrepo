import os
import random
import string
from azure.identity import DefaultAzureCredential
from azure.identity import ManagedIdentityCredential
from azure.graphrbac import GraphRbacManagementClient
from azure.mgmt.authorization import AuthorizationManagementClient
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
scope = f'/subscriptions/{subscription_id}/resourceGroups/{resource_group_name}'
managed_identity = ManagedIdentityCredential()

# Register an Azure AD app
app = graph_client.applications.create(
    display_name=app_display_name,
    password_credentials=[app_secret],
)

# Add the "SecurityEvents.ReadWrite.All" permission
app_id = app.app_id
principal_id = managed_identity.get_token("https://graph.microsoft.com/.default").token
role_definition_id = '/providers/Microsoft.Authorization/roleDefinitions/a15484ba-e580-490e-b712-07566ed7c2b2'
role_assignment_name = f'{managed_identity_name}-assignment'

role_assignment = RoleAssignmentCreateParameters(
    role_definition_id=role_definition_id,
    principal_id=principal_id,
)

authorization_client.role_assignments.create(scope, role_assignment_name, role_assignment)

# Print the app's client ID and app secret
print(f"Azure AD App Application ID: {app_id}")
print(f"Azure AD App Secret: {app_secret}")
