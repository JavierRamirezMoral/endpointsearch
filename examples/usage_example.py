"""
Example usage of endpointSearch.py as a module.

This script demonstrates how to import and use the main function programmatically.
Requires Azure CLI authentication.
"""
import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from endpointSearch import get_app_gateways_with_endpoint_all_subs

if __name__ == "__main__":
    # Example call (will prompt for Azure authentication if not already logged in)
    get_app_gateways_with_endpoint_all_subs("/myapi")
    print("This example shows how to use get_app_gateways_with_endpoint_all_subs from code. Modify as needed for your environment.")
