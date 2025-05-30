from __future__ import annotations

import base64
from typing import Any
from urllib.parse import quote

import httpx
from pydantic import SecretStr

from openhands.core.logger import openhands_logger as logger
from openhands.integrations.service_types import (
    AuthenticationError,
    BaseGitService,
    Branch,
    ProviderType,
    Repository,
    RequestMethod,
    SuggestedTask,
    TaskType,
    User,
)
from openhands.server.types import AppMode


class AzureDevOpsServiceImpl(BaseGitService):
    """Azure DevOps API service implementation"""

    def __init__(
        self,
        user_id: str | None = None,
        token: SecretStr | None = None,
        external_auth_id: str | None = None,
        external_auth_token: SecretStr | None = None,
        external_token_manager: bool = False,
        base_domain: str | None = None,
    ):
        self.user_id = user_id
        self.token = token
        self.external_auth_id = external_auth_id
        self.external_auth_token = external_auth_token
        self.external_token_manager = external_token_manager

        # Support custom Azure DevOps instances
        if base_domain:
            if base_domain.startswith('http'):
                # Extract organization URL from URLs like https://org.visualstudio.com/project
                base_url = base_domain.rstrip('/')
                # If URL contains a project path, extract just the organization part
                if '/' in base_url.split('://', 1)[1]:
                    url_parts = base_url.split('/')
                    self.base_url = '/'.join(
                        url_parts[:3]
                    )  # https://org.visualstudio.com
                else:
                    self.base_url = base_url
            else:
                self.base_url = f'https://{base_domain}'
        else:
            self.base_url = 'https://dev.azure.com'

    @property
    def provider(self) -> str:
        return 'Azure DevOps'

    async def get_latest_token(self) -> SecretStr | None:
        """Get latest working token of the user"""
        return self.token

    def _get_auth_headers(self) -> dict[str, str]:
        """Get authentication headers for Azure DevOps API"""
        if not self.token:
            raise AuthenticationError('No Azure DevOps token provided')

        # Azure DevOps uses Basic Auth with PAT
        # Username can be empty, password is the PAT
        credentials = f':{self.token.get_secret_value()}'
        encoded_credentials = base64.b64encode(credentials.encode()).decode()

        return {
            'Authorization': f'Basic {encoded_credentials}',
            'Content-Type': 'application/json',
        }

    async def _make_request(
        self,
        url: str,
        params: dict | None = None,
        method: RequestMethod = RequestMethod.GET,
    ) -> tuple[Any, dict]:
        """Make authenticated request to Azure DevOps API"""
        headers = self._get_auth_headers()

        async with httpx.AsyncClient() as client:
            try:
                response = await self.execute_request(
                    client, url, headers, params, method
                )
                response.raise_for_status()

                # Parse link header if present for pagination
                link_header = response.headers.get('Link', '')

                return response.json(), {'link': link_header}
            except httpx.HTTPStatusError as e:
                raise self.handle_http_status_error(e)
            except httpx.HTTPError as e:
                raise self.handle_http_error(e)

    async def get_user(self) -> User:
        """Get the authenticated user's information"""
        # Try different approaches for different Azure DevOps setups

        # First try the visual studio API for custom instances
        if self.base_url != 'https://dev.azure.com':
            try:
                # For custom instances, try the connection data API
                url = f'{self.base_url}/_apis/connectionData?api-version=7.1-preview.1'
                data, _ = await self._make_request(url)

                authenticated_user = data.get('authenticatedUser', {})
                if authenticated_user:
                    return User(
                        id=hash(authenticated_user.get('id', '')) & 0x7FFFFFFF,
                        login=authenticated_user.get('providerDisplayName', ''),
                        avatar_url='',
                        name=authenticated_user.get('providerDisplayName', ''),
                        email=authenticated_user.get(
                            'providerDisplayName', ''
                        ),  # Often email for ADO
                    )
            except Exception as e:
                logger.warning(f'Failed to get user from connection data: {e}')

        # Fallback to profile API (works for dev.azure.com)
        try:
            url = 'https://app.vssps.visualstudio.com/_apis/profile/profiles/me?api-version=7.1-preview.3'
            data, _ = await self._make_request(url)

            return User(
                id=hash(data.get('id', '')) & 0x7FFFFFFF,
                login=data.get('emailAddress', ''),
                avatar_url=data.get('coreAttributes', {})
                .get('Avatar', {})
                .get('value', {})
                .get('value', ''),
                name=data.get('displayName', ''),
                email=data.get('emailAddress', ''),
            )
        except Exception as e:
            logger.warning(f'Failed to get user info from profile API: {e}')

        # Final fallback - create a minimal user from token validation
        try:
            # Just validate the token works by calling a simple API
            if self.base_url != 'https://dev.azure.com':
                url = f'{self.base_url}/_apis/projects?$top=1&api-version=7.1-preview.4'
            else:
                url = f'{self.base_url}/_apis/accounts?$top=1&api-version=7.1-preview.1'

            await self._make_request(url)

            # If the request succeeds, return a basic user
            return User(
                id=1,
                login='ado-user',
                avatar_url='',
                name='Azure DevOps User',
                email='ado-user@example.com',
            )
        except Exception as e:
            logger.warning(f'Failed to validate Azure DevOps token: {e}')
            raise AuthenticationError('Invalid Azure DevOps token')

    async def search_repositories(
        self,
        query: str,
        per_page: int,
        sort: str,
        order: str,
    ) -> list[Repository]:
        """Search for repositories in Azure DevOps"""
        # For now, return empty list as Azure DevOps search is more complex
        # Would need organization context to properly search
        return []

    async def _process_projects(
        self, projects_data: dict, repositories: list, base_org_url: str
    ):
        """Helper method to process projects and extract repositories"""
        for project in projects_data.get('value', []):
            project_id = project.get('id')
            project_name = project.get('name')

            if not project_id or not project_name:
                continue

            # Extract organization name from URL
            org_name = (
                base_org_url.split('/')[-1]
                if base_org_url != self.base_url
                else 'DefaultCollection'
            )
            if self.base_url != 'https://dev.azure.com':
                # For custom URLs like https://njohnson3163.visualstudio.com, extract org name from domain
                from urllib.parse import urlparse

                parsed = urlparse(base_org_url)
                org_name = (
                    parsed.hostname.split('.')[0]
                    if parsed.hostname
                    else 'DefaultCollection'
                )

            # Get repositories for this project
            repos_url = f'{base_org_url}/{project_name}/_apis/git/repositories?api-version=7.1-preview.1'
            try:
                repos_data, _ = await self._make_request(repos_url)

                for repo in repos_data.get('value', []):
                    # Convert UUID string to integer using hash
                    repo_id_str = repo.get('id', '')
                    repo_id = (
                        hash(repo_id_str) & 0x7FFFFFFF
                    )  # Ensure positive 32-bit int

                    repositories.append(
                        Repository(
                            id=repo_id,
                            full_name=f'{org_name}/{project_name}/{repo.get("name", "")}',
                            git_provider=ProviderType.AZURE_DEVOPS,
                            is_public=False,  # Azure DevOps repos are typically private
                        )
                    )
            except Exception as e:
                logger.warning(
                    f'Failed to get repositories for project {project_name}: {e}'
                )
                continue

    async def _get_work_items_for_organization(
        self, org_url: str, user_email: str, suggested_tasks: list[SuggestedTask]
    ) -> None:
        """Helper method to get work items for an organization that are linked to repositories"""
        try:
            # Get projects for this organization
            projects_url = f'{org_url}/_apis/projects?api-version=7.1-preview.4'
            projects_data, _ = await self._make_request(projects_url)

            for project in projects_data.get('value', []):
                project_name = project.get('name')
                if not project_name:
                    continue

                # Query work items assigned to the user that are active
                # Using WIQL (Work Item Query Language) to find work items
                wiql_query = {
                    'query': f"""
                        SELECT [System.Id], [System.Title], [System.WorkItemType], [System.State]
                        FROM WorkItems
                        WHERE [System.AssignedTo] = '{user_email}'
                        AND [System.State] NOT IN ('Closed', 'Done', 'Removed', 'Resolved')
                        ORDER BY [System.ChangedDate] DESC
                    """
                }

                wiql_url = f'{org_url}/{quote(project_name)}/_apis/wit/wiql?api-version=7.1-preview.2'

                try:
                    wiql_response, _ = await self._make_request(
                        wiql_url, params=wiql_query, method=RequestMethod.POST
                    )

                    work_items = wiql_response.get('workItems', [])
                    if not work_items:
                        continue

                    # Get detailed work item information
                    work_item_ids = [str(wi['id']) for wi in work_items]
                    if work_item_ids:
                        await self._process_work_items(
                            org_url, project_name, work_item_ids, suggested_tasks
                        )

                except Exception as e:
                    logger.warning(
                        f'Failed to query work items for project {project_name}: {e}'
                    )
                    continue

        except Exception as e:
            logger.warning(f'Failed to get work items for organization {org_url}: {e}')

    async def _process_work_items(
        self,
        org_url: str,
        project_name: str,
        work_item_ids: list[str],
        suggested_tasks: list[SuggestedTask],
    ) -> None:
        """Process work items and filter those linked to repositories"""
        try:
            # Get work item details
            ids_param = ','.join(work_item_ids)
            work_items_url = f'{org_url}/{quote(project_name)}/_apis/wit/workitems?ids={ids_param}&$expand=relations&api-version=7.1-preview.3'

            work_items_response, _ = await self._make_request(work_items_url)
            work_items = work_items_response.get('value', [])

            # Extract organization name from URL
            org_name = (
                org_url.split('/')[-1]
                if org_url != self.base_url
                else 'DefaultCollection'
            )
            if self.base_url != 'https://dev.azure.com':
                # For custom URLs like https://njohnson3163.visualstudio.com, extract org name from domain
                from urllib.parse import urlparse

                parsed = urlparse(org_url)
                org_name = (
                    parsed.hostname.split('.')[0]
                    if parsed.hostname
                    else 'DefaultCollection'
                )

            for work_item in work_items:
                try:
                    work_item_id = work_item.get('id')
                    fields = work_item.get('fields', {})
                    title = fields.get('System.Title', 'Untitled Work Item')
                    work_item_type = fields.get('System.WorkItemType', 'Work Item')

                    # Check if work item has repository associations
                    repo_name = await self._get_work_item_repository_association(
                        work_item, org_url, project_name, org_name
                    )

                    if repo_name:
                        # Create suggested task for this work item
                        task_type = self._map_work_item_type_to_task_type(
                            work_item_type
                        )

                        suggested_task = SuggestedTask(
                            git_provider=ProviderType.AZURE_DEVOPS,
                            task_type=task_type,
                            repo=repo_name,
                            issue_number=work_item_id,
                            title=title,
                        )

                        suggested_tasks.append(suggested_task)

                except Exception as e:
                    logger.warning(
                        f'Failed to process work item {work_item.get("id", "unknown")}: {e}'
                    )
                    continue

        except Exception as e:
            logger.warning(f'Failed to process work items: {e}')

    async def _get_work_item_repository_association(
        self, work_item: dict, org_url: str, project_name: str, org_name: str
    ) -> str | None:
        """Check if work item is associated with a repository and return repo name"""
        try:
            relations = work_item.get('relations', [])

            # Look for Git commit relations
            for relation in relations:
                rel_type = relation.get('rel', '')
                if 'ArtifactLink' in rel_type:
                    url = relation.get('url', '')
                    # Check if this is a Git commit link
                    if 'git/repositories' in url and 'commits' in url:
                        # Extract repository name from commit URL
                        # URL format: https://org.visualstudio.com/project/_apis/git/repositories/repo-id/commits/commit-id
                        url_parts = url.split('/')
                        if 'repositories' in url_parts:
                            repo_idx = url_parts.index('repositories')
                            if repo_idx + 1 < len(url_parts):
                                repo_id = url_parts[repo_idx + 1]
                                # Get repository name from ID
                                repo_name = await self._get_repository_name_from_id(
                                    org_url, project_name, repo_id
                                )
                                if repo_name:
                                    return f'{org_name}/{project_name}/{repo_name}'

            # If no direct Git relations found, associate with the first repository in the project
            # This is a fallback for work items that don't have explicit Git links
            repos = await self._get_project_repositories(org_url, project_name)
            if repos:
                # Use the first repository as a default association
                first_repo = repos[0]
                return f'{org_name}/{project_name}/{first_repo}'

        except Exception as e:
            logger.warning(f'Failed to get repository association for work item: {e}')

        return None

    async def _get_repository_name_from_id(
        self, org_url: str, project_name: str, repo_id: str
    ) -> str | None:
        """Get repository name from repository ID"""
        try:
            repo_url = f'{org_url}/{quote(project_name)}/_apis/git/repositories/{quote(repo_id)}?api-version=7.1-preview.1'
            repo_data, _ = await self._make_request(repo_url)
            return repo_data.get('name')
        except Exception as e:
            logger.warning(f'Failed to get repository name for ID {repo_id}: {e}')
            return None

    async def _get_project_repositories(
        self, org_url: str, project_name: str
    ) -> list[str]:
        """Get list of repository names for a project"""
        try:
            repos_url = f'{org_url}/{quote(project_name)}/_apis/git/repositories?api-version=7.1-preview.1'
            repos_data, _ = await self._make_request(repos_url)

            repo_names = []
            for repo in repos_data.get('value', []):
                repo_name = repo.get('name')
                if repo_name:
                    repo_names.append(repo_name)

            return repo_names
        except Exception as e:
            logger.warning(
                f'Failed to get repositories for project {project_name}: {e}'
            )
            return []

    def _map_work_item_type_to_task_type(self, work_item_type: str) -> TaskType:
        """Map Azure DevOps work item types to OpenHands task types"""
        work_item_type_lower = work_item_type.lower()

        # Map common ADO work item types to appropriate task types
        if work_item_type_lower in ['bug', 'defect']:
            return TaskType.OPEN_ISSUE
        elif work_item_type_lower in ['user story', 'story', 'feature']:
            return TaskType.OPEN_ISSUE
        elif work_item_type_lower in ['task', 'work item']:
            return TaskType.OPEN_ISSUE
        else:
            # Default to OPEN_ISSUE for unknown work item types
            return TaskType.OPEN_ISSUE

    async def get_repositories(self, sort: str, app_mode: AppMode) -> list[Repository]:
        """Get repositories for the authenticated user"""
        try:
            repositories: list[Repository] = []

            # Check if we're using a custom organization URL vs generic dev.azure.com
            if self.base_url != 'https://dev.azure.com':
                # Direct organization access - get projects directly
                projects_url = (
                    f'{self.base_url}/_apis/projects?api-version=7.1-preview.4'
                )
                try:
                    projects_data, _ = await self._make_request(projects_url)
                    await self._process_projects(
                        projects_data, repositories, self.base_url
                    )
                except Exception as e:
                    logger.warning(f'Failed to get projects from {self.base_url}: {e}')
            else:
                # Generic Azure DevOps - get organizations first
                orgs_url = f'{self.base_url}/_apis/accounts?api-version=7.1-preview.1'
                orgs_data, _ = await self._make_request(orgs_url)

                for org in orgs_data.get('value', []):
                    org_name = org.get('accountName')
                    if not org_name:
                        continue

                    # Get projects for this organization
                    projects_url = f'{self.base_url}/{org_name}/_apis/projects?api-version=7.1-preview.4'
                    try:
                        projects_data, _ = await self._make_request(projects_url)
                        await self._process_projects(
                            projects_data, repositories, f'{self.base_url}/{org_name}'
                        )
                    except Exception as e:
                        logger.warning(f'Failed to get projects from {org_name}: {e}')
                        continue

            return repositories

        except Exception as e:
            logger.warning(f'Failed to get repositories from Azure DevOps: {e}')
            return []

    async def get_suggested_tasks(self) -> list[SuggestedTask]:
        """Get suggested tasks for the authenticated user across all repositories"""
        try:
            suggested_tasks: list[SuggestedTask] = []

            # Get user info to find work items assigned to the current user
            user = await self.get_user()
            user_email = user.email

            if not user_email:
                logger.warning('No user email found, cannot fetch work items')
                return []

            # Get all organizations and projects to search for work items
            if self.base_url != 'https://dev.azure.com':
                # Direct organization access
                await self._get_work_items_for_organization(
                    self.base_url, user_email, suggested_tasks
                )
            else:
                # Generic Azure DevOps - get organizations first
                orgs_url = f'{self.base_url}/_apis/accounts?api-version=7.1-preview.1'
                try:
                    orgs_data, _ = await self._make_request(orgs_url)

                    for org in orgs_data.get('value', []):
                        org_name = org.get('accountName')
                        if org_name:
                            org_url = f'{self.base_url}/{org_name}'
                            await self._get_work_items_for_organization(
                                org_url, user_email, suggested_tasks
                            )
                except Exception as e:
                    logger.warning(f'Failed to get organizations: {e}')

            return suggested_tasks

        except Exception as e:
            logger.warning(f'Failed to get suggested tasks from Azure DevOps: {e}')
            return []

    async def get_repository_details_from_repo_name(
        self, repository: str
    ) -> Repository:
        """Gets all repository details from repository name"""
        # Parse repository name format: org/project/repo
        parts = repository.split('/')
        if len(parts) != 3:
            raise ValueError(
                'Azure DevOps repository format should be: organization/project/repository'
            )

        org_name, project_name, repo_name = parts

        url = f'{self.base_url}/{quote(org_name)}/{quote(project_name)}/_apis/git/repositories/{quote(repo_name)}?api-version=7.1-preview.1'

        try:
            data, _ = await self._make_request(url)

            return Repository(
                id=data.get('id', ''),
                full_name=repository,
                git_provider=ProviderType.AZURE_DEVOPS,
                is_public=False,  # Azure DevOps repos are typically private
            )
        except Exception as e:
            logger.warning(f'Failed to get repository details for {repository}: {e}')
            raise AuthenticationError(f'Cannot access repository {repository}')

    async def get_branches(self, repository: str) -> list[Branch]:
        """Get branches for a repository"""
        # Parse repository name format: org/project/repo
        parts = repository.split('/')
        if len(parts) != 3:
            raise ValueError(
                'Azure DevOps repository format should be: organization/project/repository'
            )

        org_name, project_name, repo_name = parts

        # For custom instances like visualstudio.com, the URL format is different
        if self.base_url != 'https://dev.azure.com':
            # Custom instance: https://instance.com/project/_apis/git/repositories/repo/refs
            url = f'{self.base_url}/{quote(project_name)}/_apis/git/repositories/{quote(repo_name)}/refs?filter=heads/&api-version=7.1-preview.1'
        else:
            # Azure DevOps cloud: https://dev.azure.com/org/project/_apis/git/repositories/repo/refs
            url = f'{self.base_url}/{quote(org_name)}/{quote(project_name)}/_apis/git/repositories/{quote(repo_name)}/refs?filter=heads/&api-version=7.1-preview.1'

        try:
            data, _ = await self._make_request(url)

            branches = []
            for ref in data.get('value', []):
                branch_name = ref.get('name', '').replace('refs/heads/', '')
                if branch_name:
                    branches.append(
                        Branch(
                            name=branch_name,
                            commit_sha=ref.get('objectId', ''),
                            protected=False,  # Would need additional API call to determine
                        )
                    )

            return branches

        except Exception as e:
            logger.warning(f'Failed to get branches for {repository}: {e}')
            return []
