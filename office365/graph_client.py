from office365.directory.applications.application import Application
from office365.directory.applications.application_template import ApplicationTemplate
from office365.directory.audit.audit_log_root import AuditLogRoot
from office365.directory.directory import Directory
from office365.directory.directory_object_collection import DirectoryObjectCollection
from office365.directory.groups.group_lifecycle_policy import GroupLifecyclePolicy
from office365.directory.groups.group_setting_template import GroupSettingTemplate
from office365.directory.groups.group_collection import GroupCollection
from office365.directory.identities.identity_container import IdentityContainer
from office365.directory.identities.identity_provider import IdentityProvider
from office365.directory.organizations.organization import Organization
from office365.directory.applications.service_principal import ServicePrincipal
from office365.directory.licenses.subscribed_sku import SubscribedSku
from office365.directory.subscription import Subscription
from office365.directory.users.user import User
from office365.directory.users.user_collection import UserCollection
from office365.entity_collection import EntityCollection
from office365.onedrive.drives.drive import Drive
from office365.onedrive.shares.shares_collection import SharesCollection
from office365.onedrive.sites.sites_with_root import SitesWithRoot
from office365.outlook.contacts.contact import Contact
from office365.runtime.auth.token_response import TokenResponse
from office365.runtime.client_runtime_context import ClientRuntimeContext
from office365.runtime.http.http_method import HttpMethod
from office365.runtime.http.request_options import RequestOptions
from office365.runtime.odata.odata_request import ODataRequest
from office365.runtime.odata.odata_v4_batch_request import ODataV4BatchRequest
from office365.runtime.odata.v4_json_format import V4JsonFormat
from office365.runtime.queries.batch_query import BatchQuery
from office365.runtime.queries.delete_entity_query import DeleteEntityQuery
from office365.runtime.queries.update_entity_query import UpdateEntityQuery
from office365.runtime.resource_path import ResourcePath
from office365.teams.chats.chat import Chat
from office365.communications.cloud_communication import CloudCommunication
from office365.teams.team_collection import TeamCollection
from office365.teams.teams_template import TeamsTemplate


class GraphClient(ClientRuntimeContext):
    """Graph client"""

    def __init__(self, acquire_token_callback):
        """

        :param () -> dict acquire_token_callback: Acquire token function
        """
        super(GraphClient, self).__init__()
        self._pending_request = ODataRequest(self, V4JsonFormat("minimal"))
        self._pending_request.beforeExecute += self._build_specific_query
        self._resource = "https://graph.microsoft.com"
        self._authority_host_url = "https://login.microsoftonline.com"
        self._acquire_token_callback = acquire_token_callback

    def build_single_request(self, query):
        """
        :type: office365.runtime.queries.client_query.ClientQuery
        """
        request = super(GraphClient, self).build_single_request(query)
        self._build_specific_query(request)
        return request

    def execute_batch(self):
        """Construct and submit a batch request"""
        batch_request = ODataV4BatchRequest(self)
        queries = [qry for qry in self.pending_request().get_next_query()]
        batch_request.add_query(BatchQuery(self, queries))  # Aggregate requests into batch request
        batch_request.execute_query()

    def pending_request(self):
        return self._pending_request

    def service_root_url(self):
        return "https://graph.microsoft.com/v1.0"

    def _build_specific_query(self, request):
        """
        Builds Graph specific request

        :type request: RequestOptions
        """
        query = self.current_query
        if isinstance(query, UpdateEntityQuery):
            request.method = HttpMethod.Patch
        elif isinstance(query, DeleteEntityQuery):
            request.method = HttpMethod.Delete

    def authenticate_request(self, request):
        """

        :type request: RequestOptions
        """
        token_json = self._acquire_token_callback()
        token = TokenResponse.from_json(token_json)
        request.set_header('Authorization', 'Bearer {0}'.format(token.accessToken))

    def execute_request(self, url_or_options):
        """
        Constructs and submits request directly

        :type url_or_options: str or RequestOptions
        """
        if not isinstance(url_or_options, RequestOptions):
            url_or_options = RequestOptions("{0}/{1}".format(self.service_root_url(), url_or_options))
        return self.execute_request_direct(url_or_options)

    @property
    def me(self):
        """The Me endpoint is provided as a shortcut for specifying the current user"""
        return User(self, ResourcePath("me"))

    @property
    def drives(self):
        """Get one drives"""
        return EntityCollection(self, Drive, ResourcePath("drives"))

    @property
    def users(self):
        """Get users"""
        return UserCollection(self, ResourcePath("users"))

    @property
    def groups(self):
        """Get groups"""
        return GroupCollection(self, ResourcePath("groups"))

    @property
    def sites(self):
        """Get sites"""
        return SitesWithRoot(self, ResourcePath("sites"))

    @property
    def shares(self):
        """Get shares"""
        return SharesCollection(self, ResourcePath("shares"))

    @property
    def directory_objects(self):
        """Get Directory Objects"""
        return DirectoryObjectCollection(self, ResourcePath("directoryObjects"))

    @property
    def teams(self):
        """Get teams"""
        return TeamCollection(self, ResourcePath("teams"))

    @property
    def chats(self):
        """Get teams"""
        return EntityCollection(self, Chat, ResourcePath("chats"))

    @property
    def group_setting_templates(self):
        """Get teams"""
        return EntityCollection(self, GroupSettingTemplate, ResourcePath("groupSettingTemplates"))

    @property
    def contacts(self):
        """o get all the contacts in a user's mailbox"""
        return EntityCollection(self, Contact, ResourcePath("contacts"))

    @property
    def directory(self):
        """Represents a deleted item in the directory"""
        return Directory(self, ResourcePath("directory"))

    @property
    def identity_providers(self):
        return EntityCollection(self, IdentityProvider, ResourcePath("identityProviders"))

    @property
    def identity(self):
        return IdentityContainer(self, ResourcePath("identity"))

    @property
    def application_templates(self):
        """Get the list of application templates in this organization."""
        return EntityCollection(self, ApplicationTemplate, ResourcePath("applicationTemplates"))

    @property
    def applications(self):
        """Get the list of applications in this organization."""
        return EntityCollection(self, Application, ResourcePath("applications"))

    @property
    def service_principals(self):
        """Retrieve a list of servicePrincipal objects."""
        return EntityCollection(self, ServicePrincipal, ResourcePath("servicePrincipals"))

    @property
    def organization(self):
        return Organization(self, ResourcePath("organization"))

    @property
    def subscribed_skus(self):
        """Retrieve a list of servicePrincipal objects."""
        return EntityCollection(self, SubscribedSku, ResourcePath("subscribedSkus"))

    @property
    def group_lifecycle_policies(self):
        return EntityCollection(self, GroupLifecyclePolicy, ResourcePath("groupLifecyclePolicies"))

    @property
    def communications(self):
        return EntityCollection(self, CloudCommunication, ResourcePath("communications"))

    @property
    def subscriptions(self):
        """
        Retrieve the properties and relationships of webhook subscriptions,
        based on the app ID, the user, and the user's role with a tenant.
        """
        return EntityCollection(self, Subscription, ResourcePath("subscriptions"))

    @property
    def audit_logs(self):
        """
        Get the list of audit logs generated by Azure Active Directory.
        """
        return AuditLogRoot(self, ResourcePath("auditLogs"))

    @property
    def teams_templates(self):
        """
        Get the list of teams templates.
        """
        return EntityCollection(self, TeamsTemplate, ResourcePath("teamsTemplates"))
