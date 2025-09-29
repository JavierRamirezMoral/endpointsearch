#!/usr/bin/env python3
"""
Azure Application Gateway Hostname Checker

This script searches for hostnames in all Application Gateways of an Azure tenant
using DefaultAzureCredential for authentication.
"""

import argparse
import json
import logging
import sys
from typing import Dict, List, Optional, Set

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient


class AzureGatewayChecker:
    """Azure Application Gateway hostname checker."""
    
    def __init__(self, subscription_id: Optional[str] = None):
        """
        Initialize the Azure Gateway Checker.
        
        Args:
            subscription_id: Azure subscription ID. If None, will use default subscription.
        """
        self.credential = DefaultAzureCredential()
        self.subscription_id = subscription_id
        self.network_client = None
        self.resource_client = None
        
        if subscription_id:
            self._initialize_clients()
    
    def _initialize_clients(self):
        """Initialize Azure management clients."""
        self.network_client = NetworkManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
        self.resource_client = ResourceManagementClient(
            credential=self.credential,
            subscription_id=self.subscription_id
        )
    
    def get_subscriptions(self) -> List[Dict]:
        """Get all available subscriptions."""
        from azure.mgmt.resource import SubscriptionClient
        
        subscription_client = SubscriptionClient(credential=self.credential)
        subscriptions = []
        
        for subscription in subscription_client.subscriptions.list():
            subscriptions.append({
                'id': subscription.subscription_id,
                'name': subscription.display_name,
                'state': subscription.state
            })
        
        return subscriptions
    
    def get_application_gateways(self) -> List[Dict]:
        """Get all Application Gateways in the subscription."""
        if not self.network_client:
            raise ValueError("Network client not initialized. Please provide a subscription ID.")
        
        gateways = []
        
        try:
            for gateway in self.network_client.application_gateways.list_all():
                gateways.append({
                    'name': gateway.name,
                    'resource_group': gateway.id.split('/')[4],
                    'location': gateway.location,
                    'id': gateway.id,
                    'gateway_object': gateway
                })
        except Exception as e:
            logging.error(f"Error retrieving Application Gateways: {e}")
            raise
        
        return gateways
    
    def extract_hostnames_from_gateway(self, gateway_obj) -> Set[str]:
        """Extract all hostnames from an Application Gateway."""
        hostnames = set()
        
        # Extract hostnames from HTTP listeners
        if gateway_obj.http_listeners:
            for listener in gateway_obj.http_listeners:
                if listener.host_name:
                    hostnames.add(listener.host_name)
                if listener.host_names:
                    hostnames.update(listener.host_names)
        
        # Extract hostnames from request routing rules
        if gateway_obj.request_routing_rules:
            for rule in gateway_obj.request_routing_rules:
                if hasattr(rule, 'host_name') and rule.host_name:
                    hostnames.add(rule.host_name)
        
        # Extract hostnames from URL path maps
        if gateway_obj.url_path_maps:
            for path_map in gateway_obj.url_path_maps:
                if hasattr(path_map, 'default_backend_address_pool'):
                    # Additional hostname extraction logic can be added here
                    pass
        
        return hostnames
    
    def search_hostname(self, hostname: str) -> List[Dict]:
        """
        Search for a specific hostname across all Application Gateways.
        
        Args:
            hostname: Hostname to search for
            
        Returns:
            List of dictionaries containing gateway information where hostname was found
        """
        results = []
        gateways = self.get_application_gateways()
        
        for gateway in gateways:
            gateway_hostnames = self.extract_hostnames_from_gateway(
                gateway['gateway_object']
            )
            
            if hostname in gateway_hostnames:
                results.append({
                    'gateway_name': gateway['name'],
                    'resource_group': gateway['resource_group'],
                    'location': gateway['location'],
                    'found_hostname': hostname,
                    'all_hostnames': list(gateway_hostnames)
                })
        
        return results
    
    def get_all_hostnames(self) -> Dict[str, List[str]]:
        """
        Get all hostnames from all Application Gateways.
        
        Returns:
            Dictionary mapping gateway names to their hostnames
        """
        all_hostnames = {}
        gateways = self.get_application_gateways()
        
        for gateway in gateways:
            gateway_hostnames = self.extract_hostnames_from_gateway(
                gateway['gateway_object']
            )
            all_hostnames[gateway['name']] = list(gateway_hostnames)
        
        return all_hostnames


def setup_logging(verbose: bool = False):
    """Set up logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )


def main():
    """Main function to run the Azure Gateway Checker."""
    parser = argparse.ArgumentParser(
        description='Search for hostnames in Azure Application Gateways'
    )
    parser.add_argument(
        '--subscription-id',
        help='Azure subscription ID'
    )
    parser.add_argument(
        '--hostname',
        help='Specific hostname to search for'
    )
    parser.add_argument(
        '--list-subscriptions',
        action='store_true',
        help='List all available subscriptions'
    )
    parser.add_argument(
        '--all-hostnames',
        action='store_true',
        help='Get all hostnames from all Application Gateways'
    )
    parser.add_argument(
        '--output-format',
        choices=['json', 'table'],
        default='table',
        help='Output format (default: table)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    try:
        checker = AzureGatewayChecker(args.subscription_id)
        
        if args.list_subscriptions:
            subscriptions = checker.get_subscriptions()
            if args.output_format == 'json':
                print(json.dumps(subscriptions, indent=2))
            else:
                print("Available Subscriptions:")
                print("-" * 50)
                for sub in subscriptions:
                    print(f"ID: {sub['id']}")
                    print(f"Name: {sub['name']}")
                    print(f"State: {sub['state']}")
                    print("-" * 50)
            return
        
        if not args.subscription_id:
            print("Error: --subscription-id is required for gateway operations")
            sys.exit(1)
        
        if args.hostname:
            results = checker.search_hostname(args.hostname)
            if args.output_format == 'json':
                print(json.dumps(results, indent=2))
            else:
                if results:
                    print(f"Hostname '{args.hostname}' found in the following gateways:")
                    print("-" * 60)
                    for result in results:
                        print(f"Gateway: {result['gateway_name']}")
                        print(f"Resource Group: {result['resource_group']}")
                        print(f"Location: {result['location']}")
                        print(f"All hostnames: {', '.join(result['all_hostnames'])}")
                        print("-" * 60)
                else:
                    print(f"Hostname '{args.hostname}' not found in any Application Gateway")
        
        elif args.all_hostnames:
            all_hostnames = checker.get_all_hostnames()
            if args.output_format == 'json':
                print(json.dumps(all_hostnames, indent=2))
            else:
                print("All hostnames by Application Gateway:")
                print("=" * 60)
                for gateway_name, hostnames in all_hostnames.items():
                    print(f"Gateway: {gateway_name}")
                    if hostnames:
                        for hostname in hostnames:
                            print(f"  - {hostname}")
                    else:
                        print("  - No hostnames configured")
                    print("-" * 40)
        
        else:
            parser.print_help()
    
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()