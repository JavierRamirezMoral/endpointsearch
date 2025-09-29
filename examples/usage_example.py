#!/usr/bin/env python3
"""
Usage example for Azure Application Gateway Hostname Checker

This example demonstrates how to use the azure_gtw_checker module
programmatically and via command line.
"""

import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_gtw_checker import AzureGatewayChecker


def example_programmatic_usage():
    """Example of using the checker programmatically."""
    print("=== Programmatic Usage Example ===")
    
    # Initialize the checker with a subscription ID
    # Replace with your actual subscription ID
    subscription_id = "your-subscription-id-here"
    
    try:
        checker = AzureGatewayChecker(subscription_id)
        
        # Get all available subscriptions
        print("1. Getting all available subscriptions...")
        subscriptions = checker.get_subscriptions()
        print(f"Found {len(subscriptions)} subscriptions")
        for sub in subscriptions[:3]:  # Show first 3
            print(f"   - {sub['name']} ({sub['id']})")
        
        # Get all Application Gateways
        print("\n2. Getting all Application Gateways...")
        gateways = checker.get_application_gateways()
        print(f"Found {len(gateways)} Application Gateways")
        for gw in gateways[:3]:  # Show first 3
            print(f"   - {gw['name']} in {gw['resource_group']}")
        
        # Get all hostnames
        print("\n3. Getting all hostnames...")
        all_hostnames = checker.get_all_hostnames()
        for gw_name, hostnames in list(all_hostnames.items())[:2]:  # Show first 2
            print(f"   Gateway '{gw_name}': {len(hostnames)} hostnames")
            for hostname in hostnames[:3]:  # Show first 3 hostnames
                print(f"     - {hostname}")
        
        # Search for specific hostname
        print("\n4. Searching for specific hostname...")
        search_hostname = "example.com"
        results = checker.search_hostname(search_hostname)
        if results:
            print(f"Hostname '{search_hostname}' found in {len(results)} gateways")
            for result in results:
                print(f"   - Gateway: {result['gateway_name']}")
        else:
            print(f"Hostname '{search_hostname}' not found")
            
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: This example requires valid Azure credentials and subscription ID")


def example_command_line_usage():
    """Example of command line usage."""
    print("\n=== Command Line Usage Examples ===")
    
    print("1. List all available subscriptions:")
    print("   python azure_gtw_checker.py --list-subscriptions")
    
    print("\n2. Get all hostnames from all Application Gateways:")
    print("   python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --all-hostnames")
    
    print("\n3. Search for a specific hostname:")
    print("   python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --hostname example.com")
    
    print("\n4. Get results in JSON format:")
    print("   python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --all-hostnames --output-format json")
    
    print("\n5. Enable verbose logging:")
    print("   python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --hostname example.com --verbose")


def main():
    """Run the usage examples."""
    print("Azure Application Gateway Hostname Checker - Usage Examples")
    print("=" * 60)
    
    # Show command line examples
    example_command_line_usage()
    
    # Show programmatic usage (will fail without valid credentials)
    example_programmatic_usage()
    
    print("\n" + "=" * 60)
    print("Setup Instructions:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Configure Azure authentication (Azure CLI login or environment variables)")
    print("3. Replace 'your-subscription-id-here' with your actual subscription ID")
    print("4. Run the script with your desired options")


if __name__ == "__main__":
    main()