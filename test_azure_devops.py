#!/usr/bin/env python3

import sys
import os
sys.path.insert(0, '/workspace/OpenHands')

async def test_azure_devops():
    """Test Azure DevOps integration functionality"""
    try:
        from openhands.integrations.azure_devops.azure_devops_service import AzureDevOpsServiceImpl
        from openhands.integrations.service_types import ProviderType
        
        # Get the PAT token from environment
        pat_token = os.environ.get('ADO_PAT')
        if not pat_token:
            print("ERROR: ADO_PAT environment variable not set")
            return
            
        print(f"Found ADO_PAT token: {pat_token[:4]}...")
        
        # Create the Azure DevOps service
        from pydantic import SecretStr
        from openhands.server.types import AppMode
        
        service = AzureDevOpsServiceImpl(
            token=SecretStr(pat_token),
            base_domain="https://njohnson3163.visualstudio.com"
        )
        
        # Test get_repositories
        print("Testing get_repositories...")
        repos = await service.get_repositories(
            sort="pushed",
            app_mode=AppMode.OSS
        )
        
        print(f"Found {len(repos)} repositories:")
        for repo in repos:
            print(f"  - {repo.full_name}")
            
        # Test get_branches for first repo if available
        if repos:
            first_repo = repos[0]
            print(f"\nTesting get_branches for {first_repo.full_name}...")
            branches = await service.get_branches(repository=first_repo.full_name)
            
            print(f"Found {len(branches)} branches:")
            for branch in branches:
                print(f"  - {branch.name}")
        
        print("Azure DevOps integration test completed successfully!")
        
    except ImportError as e:
        print(f"Import error: {e}")
    except Exception as e:
        print(f"Error testing Azure DevOps integration: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(test_azure_devops())