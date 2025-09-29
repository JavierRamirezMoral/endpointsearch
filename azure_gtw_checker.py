"""Azure Application Gateway hostname searcher.

Script that searches for a given hostname across all Application Gateways in a tenant.
Uses DefaultAzureCredential from azure-identity for authentication.
"""
from typing import List, Dict
import sys

try:
    from azure.identity import DefaultAzureCredential
    from azure.mgmt.network import NetworkManagementClient
except Exception:
    # Allow the repo to be browsed/tested without installing Azure packages.
    DefaultAzureCredential = None
    NetworkManagementClient = None

def get_credentials():
    """Return DefaultAzureCredential instance.

    Raises:
        RuntimeError: if azure-identity is not installed.
    """
    if DefaultAzureCredential is None:
        raise RuntimeError("azure-identity is required. Install with: pip install -r requirements.txt")
    return DefaultAzureCredential()

def list_application_gateways(subscription_id: str, credential) -> List[Dict]:
    """List Application Gateways for a subscription.

    Returns a list of dictionaries with keys: name, resource_group, backend_http_settings, http_listeners, request_routing_rules, ssl_certificates, custom_error_config
    """
    if NetworkManagementClient is None:
        raise RuntimeError("azure-mgmt-network is required. Install with: pip install -r requirements.txt")
    client = NetworkManagementClient(credential, subscription_id)
    ags = []
    for ag in client.application_gateways.list_all():
        ags.append(ag.as_dict())
    return ags

def search_hostname_in_ag(ag: Dict, hostname: str) -> bool:
    """Search for hostname in an Application Gateway resource dict.

    Inspects http_listeners and host_names under request routing rules.
    """
    # Check listeners
    for listener in ag.get('http_listeners') or []:
        host_name = listener.get('host_name')
        if host_name and host_name.lower() == hostname.lower():
            return True
    # Check frontend IP configs / backend settings as fallback (some configs contain hostnames)
    # Check request_routing_rules -> http_listener -> host_name (if present)
    for rule in ag.get('request_routing_rules') or []:
        listener = rule.get('http_listener') or {}
        host_name = listener.get('host_name') or listener.get('name')
        if host_name and hostname.lower() in host_name.lower():
            return True
    # Some configs have ssl_certificates with hostnames in data (rare)
    return False

def search_hostname(subscription_id: str, hostname: str, credential=None):
    """Return list of application gateway names where hostname was found."""
    if credential is None:
        credential = get_credentials()
    ags = list_application_gateways(subscription_id, credential)
    found = []
    for ag in ags:
        if search_hostname_in_ag(ag, hostname):
            found.append({'name': ag.get('name'), 'resource_group': ag.get('resource_group')})
    return found

def main():
    """Interactive entrypoint."""
    if len(sys.argv) > 1:
        hostname = sys.argv[1]
    else:
        hostname = input("Ingrese el hostname a buscar: ").strip()
    subscription_id = input("Ingrese el Subscription ID (o pulse Enter para usar AZURE_SUBSCRIPTION_ID env): ").strip() or None
    if not subscription_id:
        print("Debe proporcionar un subscription_id. Alternativamente, exporte AZURE_SUBSCRIPTION_ID y modifique el script para usarlo.")
        return
    try:
        credential = get_credentials()
        results = search_hostname(subscription_id, hostname, credential=credential)
    except Exception as e:
        print(f"Error: {e}")
        return
    if results:
        print("Resultados:")
        for r in results:
            print(f"✔ Encontrado en Application Gateway: {r['name']} (Resource Group: {r.get('resource_group')})")
    else:
        print("No se han encontrado Application Gateways con ese hostname.")

if __name__ == '__main__':
    main()
