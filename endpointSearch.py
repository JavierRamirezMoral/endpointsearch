
"""
Author: Javier Ramírez Moral
Date: 2025-05-16

Purpose:
--------
This script is designed to help when handling Azure incidents.
Its goal is to speed up and simplify the search for specific endpoints (e.g., a path like '/myapi' or a hostname like 'api.mydomain.com') across all Application Gateways in all subscriptions of the tenant.
This way, you can quickly identify where an endpoint is configured and act more efficiently for any request or incident.

Main features:
- Uses Azure CLI credentials for authentication.
- Iterates all available subscriptions in the tenant.
- Searches for matches of the provided endpoint in:
    - Path Maps of each Application Gateway.
    - HTTP listeners of each Application Gateway.
    - Request routing rules (`request_routing_rules`), including possible redirects.
- Shows detailed information about where the endpoint was found, including the Application Gateway name, subscription, resource group, Path Map, rule, redirect, or listener.
- Includes a direct link to the resource in the Azure Portal for quick access.
- If the endpoint is not found, it informs the user.

Requirements:
- Python 3.8 or higher installed.
  Download: https://www.python.org/downloads/
- Install the required packages by running:
    pip install azure-identity azure-mgmt-network azure-mgmt-resource
- Azure CLI installed and authenticated (`az login`).

Usage:
    python endpointSearch.py

The script will prompt for the endpoint to search in the console.

Versions:
    1.0.0 - 2025-05-16 - Script creation.
    1.1.0 - 2025-05-16 - Added direct link to the resource in Azure Portal.
    1.2.0 - 2025-05-16 - Added search in request routing rules (`request_routing_rules`).
"""

from azure.identity import AzureCliCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import SubscriptionClient


def get_app_gateways_with_endpoint_all_subs(endpoint_to_find):
    credential = AzureCliCredential()
    subscription_client = SubscriptionClient(credential)

    print(f"\n🔍 Searching for endpoint '{endpoint_to_find}' in all Application Gateways of the tenant...\n")

    found = False

    for sub in subscription_client.subscriptions.list():
        subscription_id = sub.subscription_id
        print(f"📦 Checking subscription: {sub.display_name} ({subscription_id})")
        network_client = NetworkManagementClient(credential, subscription_id)

        try:
            app_gateways = list(network_client.application_gateways.list_all())
        except Exception as e:
            print(f"⚠️  Could not access App Gateways in subscription {subscription_id}: {e}")
            continue

        for appgw in app_gateways:
            rg_name = appgw.id.split("/")[4]
            portal_link = f"https://portal.azure.com/#@/resource/subscriptions/{subscription_id}/resourceGroups/{rg_name}/providers/Microsoft.Network/applicationGateways/{appgw.name}"

            # Search in Path Maps
            for path_map in appgw.url_path_maps or []:
                for path_rule in path_map.path_rules or []:
                    for path in path_rule.paths or []:
                        if endpoint_to_find in path:
                            print(f"✅ Found in App GW: {appgw.name}")
                            print(f"   - Subscription: {sub.display_name}")
                            print(f"   - Resource Group: {rg_name}")
                            print(f"   - Path Map: {path_map.name}")
                            print(f"   - Rule: {path_rule.name}")
                            print(f"   - Path: {path}")
                            print(f"   - 🔗 Azure Portal: {portal_link}\n")
                            found = True

            # Search in Listeners
            for listener in appgw.http_listeners or []:
                if (listener.host_name and endpoint_to_find in listener.host_name) or \
                   (listener.name and endpoint_to_find in listener.name):
                    print(f"✅ Possible match in Listener of App GW: {appgw.name}")
                    print(f"   - Subscription: {sub.display_name}")
                    print(f"   - Resource Group: {rg_name}")
                    print(f"   - Listener Name: {listener.name}")
                    print(f"   - Hostname: {listener.host_name}")
                    print(f"   - 🔗 Azure Portal: {portal_link}\n")
                    found = True

            # Search in Request Routing Rules
            for rule in appgw.request_routing_rules or []:
                if rule.rule_type == "Basic":
                    if rule.name and endpoint_to_find in rule.name:
                        print(f"✅ Match in basic rule of App GW: {appgw.name}")
                        print(f"   - Rule: {rule.name}")
                        print(f"   - Subscription: {sub.display_name}")
                        print(f"   - Resource Group: {rg_name}")
                        print(f"   - 🔗 Azure Portal: {portal_link}\n")
                        found = True

                if rule.redirect_configuration and endpoint_to_find in rule.redirect_configuration.id:
                    print(f"✅ Possible match in redirect of App GW: {appgw.name}")
                    print(f"   - Rule: {rule.name}")
                    print(f"   - Redirect (ID): {rule.redirect_configuration.id}")
                    print(f"   - Subscription: {sub.display_name}")
                    print(f"   - Resource Group: {rg_name}")
                    print(f"   - 🔗 Azure Portal: {portal_link}\n")
                    found = True

                if rule.url_path_map and endpoint_to_find in rule.url_path_map.id:
                    print(f"✅ Possible match in URL Path Map ID of App GW: {appgw.name}")
                    print(f"   - Rule: {rule.name}")
                    print(f"   - URL Path Map ID: {rule.url_path_map.id}")
                    print(f"   - Subscription: {sub.display_name}")
                    print(f"   - Resource Group: {rg_name}")
                    print(f"   - 🔗 Azure Portal: {portal_link}\n")
                    found = True


    if not found:
        print("\n❌ Endpoint not found in any Application Gateway of the tenant.")

if __name__ == "__main__":
    endpoint = input("🔎 Enter the endpoint to search (e.g., /myapi or api.mydomain.com): ").strip()
    get_app_gateways_with_endpoint_all_subs(endpoint)
