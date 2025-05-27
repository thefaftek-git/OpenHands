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
                    self.base_url = '/'.join(url_parts[:3])  # https://org.visualstudio.com
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
        # Azure DevOps uses a different endpoint for user profile
        url = f'{self.base_url}/_apis/profile/profiles/me?api-version=7.1-preview.3'

        try:
            data, _ = await self._make_request(url)

            return User(
                id=data.get('id', ''),
                login=data.get('emailAddress', ''),
                avatar_url=data.get('coreAttributes', {})
                .get('Avatar', {})
                .get('value', {})
                .get('value', ''),
                name=data.get('displayName', ''),
                email=data.get('emailAddress', ''),
            )
        except Exception as e:
            logger.warning(f'Failed to get user info from Azure DevOps: {e}')
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

    async def _process_projects(self, projects_data: dict, repositories: list, base_org_url: str):
        """Helper method to process projects and extract repositories"""
        for project in projects_data.get('value', []):
            project_id = project.get('id')
            project_name = project.get('name')

            if not project_id or not project_name:
                continue

            # Extract organization name from URL
            org_name = base_org_url.split('/')[-1] if base_org_url != self.base_url else 'DefaultCollection'
            if self.base_url != 'https://dev.azure.com':
                # For custom URLs like https://njohnson3163.visualstudio.com, extract org name from domain
                from urllib.parse import urlparse
                parsed = urlparse(base_org_url)
                org_name = parsed.hostname.split('.')[0] if parsed.hostname else 'DefaultCollection'

            # Get repositories for this project
            repos_url = f'{base_org_url}/{project_name}/_apis/git/repositories?api-version=7.1-preview.1'
            try:
                repos_data, _ = await self._make_request(repos_url)

                for repo in repos_data.get('value', []):
                    # Convert UUID string to integer using hash
                    repo_id_str = repo.get('id', '')
                    repo_id = hash(repo_id_str) & 0x7FFFFFFF  # Ensure positive 32-bit int
                    
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

    async def get_repositories(self, sort: str, app_mode: AppMode) -> list[Repository]:
        """Get repositories for the authenticated user"""
        try:
            repositories: list[Repository] = []

            # Check if we're using a custom organization URL vs generic dev.azure.com
            if self.base_url != 'https://dev.azure.com':
                # Direct organization access - get projects directly
                projects_url = f'{self.base_url}/_apis/projects?api-version=7.1-preview.4'
                try:
                    projects_data, _ = await self._make_request(projects_url)
                    await self._process_projects(projects_data, repositories, self.base_url)
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
                        await self._process_projects(projects_data, repositories, f'{self.base_url}/{org_name}')
                    except Exception as e:
                        logger.warning(f'Failed to get projects from {org_name}: {e}')
                        continue

            return repositories

        except Exception as e:
            logger.warning(f'Failed to get repositories from Azure DevOps: {e}')
            return []

    async def get_suggested_tasks(self) -> list[SuggestedTask]:
        """Get suggested tasks for the authenticated user across all repositories"""
        # For now, return empty list as this would require complex Azure DevOps API calls
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
