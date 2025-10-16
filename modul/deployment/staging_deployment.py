"""
Staging Deployment Script
========================

Script untuk deployment enhanced services ke staging environment.

Author: AI Assistant
Date: 2025-01-17
"""

import os
import sys
import shutil
import logging
from datetime import datetime
from typing import Dict, List, Any
import json

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class StagingDeployment:
    """
    Staging Deployment untuk enhanced services
    """
    
    def __init__(self):
        self.staging_path = "staging"
        self.backend_services_path = "modul/backend_services"
        self.staging_services_path = f"{self.staging_path}/backend_services"
        
        # Enhanced services to deploy
        self.enhanced_services = [
            'enhanced_trading_service_v2.py',
            'enhanced_market_data_service_v2.py',
            'enhanced_portfolio_optimization_service.py',
            'enhanced_fundamental_analysis_service.py',
            'enhanced_earnings_service.py',
            'enhanced_economic_calendar_service.py',
            'enhanced_notifications_service.py',
            'enhanced_watchlist_service.py'
        ]
        
        # Deployment configuration
        self.deployment_config = {
            'environment': 'staging',
            'version': '1.0.0',
            'deployment_date': datetime.now().isoformat(),
            'services_count': len(self.enhanced_services)
        }
    
    async def deploy_to_staging(self) -> Dict[str, Any]:
        """Deploy enhanced services ke staging environment"""
        try:
            print("Starting Staging Deployment...")
            print("=" * 60)
            
            # Step 1: Create staging directory
            print("\nStep 1: Creating staging directory...")
            staging_result = await self._create_staging_directory()
            if not staging_result['success']:
                return staging_result
            
            # Step 2: Copy enhanced services
            print("\nStep 2: Copying enhanced services...")
            copy_result = await self._copy_enhanced_services()
            if not copy_result['success']:
                return copy_result
            
            # Step 3: Create deployment configuration
            print("\nStep 3: Creating deployment configuration...")
            config_result = await self._create_deployment_config()
            if not config_result['success']:
                return config_result
            
            # Step 4: Validate deployment
            print("\nStep 4: Validating deployment...")
            validation_result = await self._validate_deployment()
            if not validation_result['success']:
                return validation_result
            
            # Step 5: Create deployment report
            print("\nStep 5: Creating deployment report...")
            report_result = await self._create_deployment_report()
            
            print("\n" + "=" * 60)
            print("Staging Deployment Completed Successfully!")
            print("=" * 60)
            
            return {
                'success': True,
                'message': 'Staging deployment completed successfully',
                'deployment_config': self.deployment_config,
                'deployed_services': self.enhanced_services,
                'staging_path': self.staging_path
            }
            
        except Exception as e:
            logger.error(f"Error in staging deployment: {e}")
            return {'error': str(e)}
    
    async def _create_staging_directory(self) -> Dict[str, Any]:
        """Create staging directory structure"""
        try:
            # Create staging directory
            if not os.path.exists(self.staging_path):
                os.makedirs(self.staging_path)
                print(f"Created staging directory: {self.staging_path}")
            
            # Create backend_services directory in staging
            if not os.path.exists(self.staging_services_path):
                os.makedirs(self.staging_services_path)
                print(f"Created backend_services directory: {self.staging_services_path}")
            
            # Create other necessary directories
            directories = [
                f"{self.staging_path}/config",
                f"{self.staging_path}/logs",
                f"{self.staging_path}/data",
                f"{self.staging_path}/tests"
            ]
            
            for directory in directories:
                if not os.path.exists(directory):
                    os.makedirs(directory)
                    print(f"Created directory: {directory}")
            
            return {'success': True, 'message': 'Staging directory structure created'}
            
        except Exception as e:
            logger.error(f"Error creating staging directory: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _copy_enhanced_services(self) -> Dict[str, Any]:
        """Copy enhanced services to staging"""
        try:
            copied_services = []
            failed_services = []
            
            for service in self.enhanced_services:
                try:
                    source_path = f"{self.backend_services_path}/{service}"
                    destination_path = f"{self.staging_services_path}/{service}"
                    
                    if os.path.exists(source_path):
                        shutil.copy2(source_path, destination_path)
                        copied_services.append(service)
                        print(f"Copied {service} to staging")
                    else:
                        failed_services.append(f"{service} - Source file not found")
                        print(f"Failed to copy {service} - Source file not found")
                        
                except Exception as e:
                    failed_services.append(f"{service} - {str(e)}")
                    print(f"Failed to copy {service}: {str(e)}")
            
            if failed_services:
                return {
                    'success': False,
                    'error': f'Failed to copy {len(failed_services)} services',
                    'failed_services': failed_services,
                    'copied_services': copied_services
                }
            
            return {
                'success': True,
                'message': f'Successfully copied {len(copied_services)} services',
                'copied_services': copied_services
            }
            
        except Exception as e:
            logger.error(f"Error copying enhanced services: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _create_deployment_config(self) -> Dict[str, Any]:
        """Create deployment configuration"""
        try:
            config_data = {
                'deployment': self.deployment_config,
                'services': self.enhanced_services,
                'environment': {
                    'name': 'staging',
                    'description': 'Staging environment for enhanced services',
                    'created_at': datetime.now().isoformat()
                },
                'monitoring': {
                    'enabled': True,
                    'log_level': 'INFO',
                    'metrics_collection': True
                }
            }
            
            config_path = f"{self.staging_path}/config/deployment_config.json"
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config_data, f, indent=2)
            
            print(f"Created deployment configuration: {config_path}")
            
            return {'success': True, 'message': 'Deployment configuration created'}
            
        except Exception as e:
            logger.error(f"Error creating deployment configuration: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _validate_deployment(self) -> Dict[str, Any]:
        """Validate staging deployment"""
        try:
            validation_results = []
            
            # Check if all services are copied
            for service in self.enhanced_services:
                service_path = f"{self.staging_services_path}/{service}"
                if os.path.exists(service_path):
                    # Check file size
                    file_size = os.path.getsize(service_path)
                    if file_size > 1000:  # Minimum file size
                        validation_results.append({
                            'service': service,
                            'status': 'PASSED',
                            'file_size': file_size
                        })
                    else:
                        validation_results.append({
                            'service': service,
                            'status': 'FAILED',
                            'error': 'File too small'
                        })
                else:
                    validation_results.append({
                        'service': service,
                        'status': 'FAILED',
                        'error': 'File not found'
                    })
            
            # Check configuration file
            config_path = f"{self.staging_path}/config/deployment_config.json"
            if os.path.exists(config_path):
                validation_results.append({
                    'service': 'deployment_config',
                    'status': 'PASSED',
                    'file_size': os.path.getsize(config_path)
                })
            else:
                validation_results.append({
                    'service': 'deployment_config',
                    'status': 'FAILED',
                    'error': 'Configuration file not found'
                })
            
            # Count results
            passed = sum(1 for result in validation_results if result['status'] == 'PASSED')
            failed = sum(1 for result in validation_results if result['status'] == 'FAILED')
            
            if failed == 0:
                return {
                    'success': True,
                    'message': f'All {passed} validations passed',
                    'validation_results': validation_results
                }
            else:
                return {
                    'success': False,
                    'error': f'{failed} validations failed',
                    'validation_results': validation_results
                }
            
        except Exception as e:
            logger.error(f"Error validating deployment: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _create_deployment_report(self) -> Dict[str, Any]:
        """Create deployment report"""
        try:
            report_data = {
                'deployment_summary': {
                    'environment': 'staging',
                    'deployment_date': datetime.now().isoformat(),
                    'services_deployed': len(self.enhanced_services),
                    'deployment_status': 'SUCCESS'
                },
                'deployed_services': self.enhanced_services,
                'deployment_config': self.deployment_config,
                'staging_path': self.staging_path
            }
            
            report_path = f"{self.staging_path}/deployment_report.json"
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report_data, f, indent=2)
            
            print(f"Created deployment report: {report_path}")
            
            return {'success': True, 'message': 'Deployment report created'}
            
        except Exception as e:
            logger.error(f"Error creating deployment report: {e}")
            return {'success': False, 'error': str(e)}

async def main():
    """Main function untuk menjalankan staging deployment"""
    try:
        deployment = StagingDeployment()
        result = await deployment.deploy_to_staging()
        
        if result.get('success'):
            print("\nSTAGING DEPLOYMENT RESULTS:")
            print("=" * 60)
            print(f"Status: SUCCESS")
            print(f"Services Deployed: {len(result['deployed_services'])}")
            print(f"Staging Path: {result['staging_path']}")
            print(f"Deployment Date: {result['deployment_config']['deployment_date']}")
            
            print("\nDeployed Services:")
            for service in result['deployed_services']:
                print(f"- {service}")
        else:
            print(f"\nSTAGING DEPLOYMENT FAILED:")
            print(f"Error: {result.get('error', 'Unknown error')}")
        
        return result
        
    except Exception as e:
        logger.error(f"Error in main: {e}")
        return {'error': str(e)}

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
