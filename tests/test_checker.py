import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pytest
from unittest.mock import patch, MagicMock
import builtins

import endpointSearch

def test_get_app_gateways_with_endpoint_all_subs_found(capsys):
    """
    Test that the function prints found endpoints when present in mocked Application Gateways.
    """
    # Patch Azure SDK clients and their methods
    with patch("endpointSearch.AzureCliCredential"), \
         patch("endpointSearch.SubscriptionClient") as mock_sub_client, \
         patch("endpointSearch.NetworkManagementClient") as mock_net_client:

        # Mock subscriptions
        mock_sub = MagicMock()
        mock_sub.subscription_id = "sub-id"
        mock_sub.display_name = "Test Subscription"
        mock_sub_client.return_value.subscriptions.list.return_value = [mock_sub]

        # Mock Application Gateway with a matching path
        appgw = MagicMock()
        appgw.id = "/subscriptions/sub-id/resourceGroups/rg-test/providers/Microsoft.Network/applicationGateways/appgw-test"
        appgw.name = "appgw-test"
        appgw.url_path_maps = [MagicMock()]
        appgw.url_path_maps[0].name = "pathmap1"
        appgw.url_path_maps[0].path_rules = [MagicMock()]
        appgw.url_path_maps[0].path_rules[0].name = "rule1"
        appgw.url_path_maps[0].path_rules[0].paths = ["/myapi"]
        appgw.http_listeners = []
        appgw.request_routing_rules = []
        mock_net_client.return_value.application_gateways.list_all.return_value = [appgw]

        # Run function
        endpointSearch.get_app_gateways_with_endpoint_all_subs("/myapi")
        out = capsys.readouterr().out
        assert "Found in App GW" in out
        assert "appgw-test" in out

def test_get_app_gateways_with_endpoint_all_subs_not_found(capsys):
    """
    Test that the function prints not found message when no endpoints match.
    """
    # Patch Azure SDK clients and their methods
    with patch("endpointSearch.AzureCliCredential"), \
         patch("endpointSearch.SubscriptionClient") as mock_sub_client, \
         patch("endpointSearch.NetworkManagementClient") as mock_net_client:

        # Mock subscriptions
        mock_sub = MagicMock()
        mock_sub.subscription_id = "sub-id"
        mock_sub.display_name = "Test Subscription"
        mock_sub_client.return_value.subscriptions.list.return_value = [mock_sub]

        # Application Gateway with no matching endpoints
        appgw = MagicMock()
        appgw.id = "/subscriptions/sub-id/resourceGroups/rg-test/providers/Microsoft.Network/applicationGateways/appgw-test"
        appgw.name = "appgw-test"
        appgw.url_path_maps = []
        appgw.http_listeners = []
        appgw.request_routing_rules = []
        mock_net_client.return_value.application_gateways.list_all.return_value = [appgw]

        # Run function
        endpointSearch.get_app_gateways_with_endpoint_all_subs("/notfound")
        out = capsys.readouterr().out
        assert "Endpoint not found" in out
