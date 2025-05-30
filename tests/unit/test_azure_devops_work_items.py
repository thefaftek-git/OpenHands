"""Tests for Azure DevOps work items integration in suggested tasks."""

from unittest.mock import patch

import pytest
from pydantic import SecretStr

from openhands.integrations.azure_devops.azure_devops_service import (
    AzureDevOpsServiceImpl,
)
from openhands.integrations.service_types import ProviderType, TaskType


class TestAzureDevOpsWorkItems:
    """Test Azure DevOps work items functionality."""

    @pytest.fixture
    def ado_service(self):
        """Create an Azure DevOps service instance for testing."""
        return AzureDevOpsServiceImpl(
            token=SecretStr('test_token'), base_domain='https://test.visualstudio.com'
        )

    @pytest.mark.asyncio
    async def test_get_suggested_tasks_empty_when_no_work_items(self, ado_service):
        """Test that empty list is returned when no work items exist."""
        with patch.object(ado_service, '_make_request') as mock_request:
            # Mock user API call
            mock_request.side_effect = [
                # Connection data for user
                (
                    {
                        'authenticatedUser': {
                            'id': 'test-user',
                            'providerDisplayName': 'test@example.com',
                        }
                    },
                    {},
                ),
                # Projects API call
                ({'value': [{'name': 'TestProject'}]}, {}),
                # WIQL query returns no work items
                ({'workItems': []}, {}),
            ]

            tasks = await ado_service.get_suggested_tasks()
            assert tasks == []

    @pytest.mark.asyncio
    async def test_get_suggested_tasks_with_work_items(self, ado_service):
        """Test that work items are correctly converted to suggested tasks."""
        with patch.object(ado_service, '_make_request') as mock_request:
            # Mock the sequence of API calls
            mock_request.side_effect = [
                # Connection data for user
                (
                    {
                        'authenticatedUser': {
                            'id': 'test-user',
                            'providerDisplayName': 'test@example.com',
                        }
                    },
                    {},
                ),
                # Projects API call
                ({'value': [{'name': 'TestProject'}]}, {}),
                # WIQL query returns work items
                ({'workItems': [{'id': 123}, {'id': 456}]}, {}),
                # Work item details call
                (
                    {
                        'value': [
                            {
                                'id': 123,
                                'fields': {
                                    'System.Title': 'Fix bug in login',
                                    'System.WorkItemType': 'Bug',
                                },
                                'relations': [],
                            },
                            {
                                'id': 456,
                                'fields': {
                                    'System.Title': 'Add new feature',
                                    'System.WorkItemType': 'User Story',
                                },
                                'relations': [],
                            },
                        ]
                    },
                    {},
                ),
                # Repository list for fallback association
                ({'value': [{'name': 'test-repo'}]}, {}),
                # Repository list for second work item
                ({'value': [{'name': 'test-repo'}]}, {}),
            ]

            tasks = await ado_service.get_suggested_tasks()

            assert len(tasks) == 2

            # Check first task (bug)
            assert tasks[0].git_provider == ProviderType.AZURE_DEVOPS
            assert tasks[0].task_type == TaskType.OPEN_ISSUE
            assert tasks[0].issue_number == 123
            assert tasks[0].title == 'Fix bug in login'
            assert 'test/TestProject/test-repo' in tasks[0].repo

            # Check second task (user story)
            assert tasks[1].git_provider == ProviderType.AZURE_DEVOPS
            assert tasks[1].task_type == TaskType.OPEN_ISSUE
            assert tasks[1].issue_number == 456
            assert tasks[1].title == 'Add new feature'
            assert 'test/TestProject/test-repo' in tasks[1].repo

    @pytest.mark.asyncio
    async def test_work_item_with_git_relation(self, ado_service):
        """Test work item with direct Git commit relation."""
        with patch.object(ado_service, '_make_request') as mock_request:
            mock_request.side_effect = [
                # Connection data for user
                (
                    {
                        'authenticatedUser': {
                            'id': 'test-user',
                            'providerDisplayName': 'test@example.com',
                        }
                    },
                    {},
                ),
                # Projects API call
                ({'value': [{'name': 'TestProject'}]}, {}),
                # WIQL query returns work item with Git relation
                ({'workItems': [{'id': 789}]}, {}),
                # Work item details with Git relation
                (
                    {
                        'value': [
                            {
                                'id': 789,
                                'fields': {
                                    'System.Title': 'Task with Git link',
                                    'System.WorkItemType': 'Task',
                                },
                                'relations': [
                                    {
                                        'rel': 'ArtifactLink',
                                        'url': 'https://test.visualstudio.com/TestProject/_apis/git/repositories/repo-123/commits/abc123',
                                    }
                                ],
                            }
                        ]
                    },
                    {},
                ),
                # Repository name lookup
                ({'name': 'linked-repo'}, {}),
            ]

            tasks = await ado_service.get_suggested_tasks()

            assert len(tasks) == 1
            assert tasks[0].issue_number == 789
            assert tasks[0].title == 'Task with Git link'
            assert 'test/TestProject/linked-repo' in tasks[0].repo

    def test_map_work_item_type_to_task_type(self, ado_service):
        """Test work item type mapping."""
        # Test bug mapping
        assert (
            ado_service._map_work_item_type_to_task_type('Bug') == TaskType.OPEN_ISSUE
        )
        assert (
            ado_service._map_work_item_type_to_task_type('Defect')
            == TaskType.OPEN_ISSUE
        )

        # Test user story mapping
        assert (
            ado_service._map_work_item_type_to_task_type('User Story')
            == TaskType.OPEN_ISSUE
        )
        assert (
            ado_service._map_work_item_type_to_task_type('Story') == TaskType.OPEN_ISSUE
        )
        assert (
            ado_service._map_work_item_type_to_task_type('Feature')
            == TaskType.OPEN_ISSUE
        )

        # Test task mapping
        assert (
            ado_service._map_work_item_type_to_task_type('Task') == TaskType.OPEN_ISSUE
        )
        assert (
            ado_service._map_work_item_type_to_task_type('Work Item')
            == TaskType.OPEN_ISSUE
        )

        # Test unknown type defaults to OPEN_ISSUE
        assert (
            ado_service._map_work_item_type_to_task_type('Custom Type')
            == TaskType.OPEN_ISSUE
        )

    @pytest.mark.asyncio
    async def test_error_handling_in_get_suggested_tasks(self, ado_service):
        """Test error handling in get_suggested_tasks."""
        with patch.object(ado_service, '_make_request') as mock_request:
            # Mock authentication failure
            mock_request.side_effect = Exception('Authentication failed')

            tasks = await ado_service.get_suggested_tasks()

            # Should return empty list on error, not raise exception
            assert tasks == []

    @pytest.mark.asyncio
    async def test_multiple_projects_with_work_items(self, ado_service):
        """Test work items from multiple projects."""
        with patch.object(ado_service, '_make_request') as mock_request:
            mock_request.side_effect = [
                # Connection data for user
                (
                    {
                        'authenticatedUser': {
                            'id': 'test-user',
                            'providerDisplayName': 'test@example.com',
                        }
                    },
                    {},
                ),
                # Projects API call - multiple projects
                ({'value': [{'name': 'Project1'}, {'name': 'Project2'}]}, {}),
                # WIQL query for Project1
                ({'workItems': [{'id': 111}]}, {}),
                # Work item details for Project1
                (
                    {
                        'value': [
                            {
                                'id': 111,
                                'fields': {
                                    'System.Title': 'Project1 Task',
                                    'System.WorkItemType': 'Task',
                                },
                                'relations': [],
                            }
                        ]
                    },
                    {},
                ),
                # Repository list for Project1
                ({'value': [{'name': 'project1-repo'}]}, {}),
                # WIQL query for Project2
                ({'workItems': [{'id': 222}]}, {}),
                # Work item details for Project2
                (
                    {
                        'value': [
                            {
                                'id': 222,
                                'fields': {
                                    'System.Title': 'Project2 Task',
                                    'System.WorkItemType': 'Bug',
                                },
                                'relations': [],
                            }
                        ]
                    },
                    {},
                ),
                # Repository list for Project2
                ({'value': [{'name': 'project2-repo'}]}, {}),
            ]

            tasks = await ado_service.get_suggested_tasks()

            assert len(tasks) == 2

            # Verify tasks from both projects
            project1_task = next(task for task in tasks if task.issue_number == 111)
            project2_task = next(task for task in tasks if task.issue_number == 222)

            assert project1_task.title == 'Project1 Task'
            assert 'Project1/project1-repo' in project1_task.repo

            assert project2_task.title == 'Project2 Task'
            assert 'Project2/project2-repo' in project2_task.repo
