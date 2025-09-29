"""
Tests for Azure Application Gateway Hostname Checker
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from azure_gtw_checker import AzureGatewayChecker


class TestAzureGatewayChecker:
    """Test cases for AzureGatewayChecker class."""
    
    def test_init_without_subscription_id(self):
        """Test initialization without subscription ID."""
        with patch('azure_gtw_checker.DefaultAzureCredential'):
            checker = AzureGatewayChecker()
            assert checker.subscription_id is None
            assert checker.network_client is None
            assert checker.resource_client is None
    
    def test_init_with_subscription_id(self):
        """Test initialization with subscription ID."""
        with patch('azure_gtw_checker.DefaultAzureCredential'), \
             patch('azure_gtw_checker.NetworkManagementClient') as mock_network, \
             patch('azure_gtw_checker.ResourceManagementClient') as mock_resource:
            
            subscription_id = "test-subscription-id"
            checker = AzureGatewayChecker(subscription_id)
            
            assert checker.subscription_id == subscription_id
            assert checker.network_client is not None
            assert checker.resource_client is not None
            mock_network.assert_called_once()
            mock_resource.assert_called_once()
    
    def test_get_subscriptions(self):
        """Test getting subscriptions."""
        with patch('azure_gtw_checker.DefaultAzureCredential'), \
             patch('azure.mgmt.resource.SubscriptionClient') as mock_sub_client:
            
            # Mock subscription data
            mock_subscription = Mock()
            mock_subscription.subscription_id = "test-sub-id"
            mock_subscription.display_name = "Test Subscription"
            mock_subscription.state = "Enabled"
            
            mock_sub_client.return_value.subscriptions.list.return_value = [mock_subscription]
            
            checker = AzureGatewayChecker()
            subscriptions = checker.get_subscriptions()
            
            assert len(subscriptions) == 1
            assert subscriptions[0]['id'] == "test-sub-id"
            assert subscriptions[0]['name'] == "Test Subscription"
            assert subscriptions[0]['state'] == "Enabled"
    
    def test_get_application_gateways_without_client(self):
        """Test getting application gateways without initialized client."""
        with patch('azure_gtw_checker.DefaultAzureCredential'):
            checker = AzureGatewayChecker()
            
            with pytest.raises(ValueError, match="Network client not initialized"):
                checker.get_application_gateways()
    
    def test_get_application_gateways_success(self):
        """Test successfully getting application gateways."""
        with patch('azure_gtw_checker.DefaultAzureCredential'), \
             patch('azure_gtw_checker.NetworkManagementClient') as mock_network, \
             patch('azure_gtw_checker.ResourceManagementClient'):
            
            # Mock gateway data
            mock_gateway = Mock()
            mock_gateway.name = "test-gateway"
            mock_gateway.id = "/subscriptions/sub-id/resourceGroups/test-rg/providers/Microsoft.Network/applicationGateways/test-gateway"
            mock_gateway.location = "eastus"
            
            mock_network.return_value.application_gateways.list_all.return_value = [mock_gateway]
            
            checker = AzureGatewayChecker("test-subscription-id")
            gateways = checker.get_application_gateways()
            
            assert len(gateways) == 1
            assert gateways[0]['name'] == "test-gateway"
            assert gateways[0]['resource_group'] == "test-rg"
            assert gateways[0]['location'] == "eastus"
    
    def test_extract_hostnames_from_gateway(self):
        """Test extracting hostnames from gateway configuration."""
        with patch('azure_gtw_checker.DefaultAzureCredential'):
            checker = AzureGatewayChecker()
            
            # Mock gateway object with HTTP listeners
            mock_gateway = Mock()
            
            # Mock HTTP listeners
            mock_listener1 = Mock()
            mock_listener1.host_name = "api.example.com"
            mock_listener1.host_names = ["www.example.com", "admin.example.com"]
            
            mock_listener2 = Mock()
            mock_listener2.host_name = "portal.example.com"
            mock_listener2.host_names = None
            
            mock_gateway.http_listeners = [mock_listener1, mock_listener2]
            mock_gateway.request_routing_rules = []
            mock_gateway.url_path_maps = []
            
            hostnames = checker.extract_hostnames_from_gateway(mock_gateway)
            
            expected_hostnames = {
                "api.example.com", 
                "www.example.com", 
                "admin.example.com", 
                "portal.example.com"
            }
            assert hostnames == expected_hostnames
    
    def test_extract_hostnames_empty_gateway(self):
        """Test extracting hostnames from empty gateway configuration."""
        with patch('azure_gtw_checker.DefaultAzureCredential'):
            checker = AzureGatewayChecker()
            
            # Mock empty gateway object
            mock_gateway = Mock()
            mock_gateway.http_listeners = None
            mock_gateway.request_routing_rules = None
            mock_gateway.url_path_maps = None
            
            hostnames = checker.extract_hostnames_from_gateway(mock_gateway)
            
            assert hostnames == set()
    
    def test_search_hostname_found(self):
        """Test searching for a hostname that exists."""
        with patch.object(AzureGatewayChecker, 'get_application_gateways') as mock_get_gateways, \
             patch.object(AzureGatewayChecker, 'extract_hostnames_from_gateway') as mock_extract:
            
            # Mock gateway data
            mock_gateway_obj = Mock()
            mock_gateways = [{
                'name': 'test-gateway',
                'resource_group': 'test-rg',
                'location': 'eastus',
                'gateway_object': mock_gateway_obj
            }]
            
            mock_get_gateways.return_value = mock_gateways
            mock_extract.return_value = {"api.example.com", "www.example.com"}
            
            with patch('azure_gtw_checker.DefaultAzureCredential'):
                checker = AzureGatewayChecker()
                results = checker.search_hostname("api.example.com")
            
            assert len(results) == 1
            assert results[0]['gateway_name'] == 'test-gateway'
            assert results[0]['found_hostname'] == 'api.example.com'
            assert 'api.example.com' in results[0]['all_hostnames']
    
    def test_search_hostname_not_found(self):
        """Test searching for a hostname that doesn't exist."""
        with patch.object(AzureGatewayChecker, 'get_application_gateways') as mock_get_gateways, \
             patch.object(AzureGatewayChecker, 'extract_hostnames_from_gateway') as mock_extract:
            
            # Mock gateway data
            mock_gateway_obj = Mock()
            mock_gateways = [{
                'name': 'test-gateway',
                'resource_group': 'test-rg',
                'location': 'eastus',
                'gateway_object': mock_gateway_obj
            }]
            
            mock_get_gateways.return_value = mock_gateways
            mock_extract.return_value = {"api.example.com", "www.example.com"}
            
            with patch('azure_gtw_checker.DefaultAzureCredential'):
                checker = AzureGatewayChecker()
                results = checker.search_hostname("notfound.example.com")
            
            assert len(results) == 0
    
    def test_get_all_hostnames(self):
        """Test getting all hostnames from all gateways."""
        with patch.object(AzureGatewayChecker, 'get_application_gateways') as mock_get_gateways, \
             patch.object(AzureGatewayChecker, 'extract_hostnames_from_gateway') as mock_extract:
            
            # Mock gateway data
            mock_gateway_obj1 = Mock()
            mock_gateway_obj2 = Mock()
            mock_gateways = [
                {
                    'name': 'gateway1',
                    'resource_group': 'rg1',
                    'location': 'eastus',
                    'gateway_object': mock_gateway_obj1
                },
                {
                    'name': 'gateway2',
                    'resource_group': 'rg2',
                    'location': 'westus',
                    'gateway_object': mock_gateway_obj2
                }
            ]
            
            mock_get_gateways.return_value = mock_gateways
            mock_extract.side_effect = [
                {"api.example.com", "www.example.com"},
                {"dev.example.com"}
            ]
            
            with patch('azure_gtw_checker.DefaultAzureCredential'):
                checker = AzureGatewayChecker()
                all_hostnames = checker.get_all_hostnames()
            
            assert len(all_hostnames) == 2
            assert set(all_hostnames['gateway1']) == {"api.example.com", "www.example.com"}
            assert set(all_hostnames['gateway2']) == {"dev.example.com"}


class TestMainFunction:
    """Test cases for the main function and CLI arguments."""
    
    @patch('azure_gtw_checker.AzureGatewayChecker')
    @patch('sys.argv', ['azure_gtw_checker.py', '--list-subscriptions'])
    def test_list_subscriptions_table_format(self, mock_checker_class):
        """Test listing subscriptions in table format."""
        from azure_gtw_checker import main
        
        mock_checker = Mock()
        mock_checker.get_subscriptions.return_value = [
            {'id': 'sub1', 'name': 'Test Sub 1', 'state': 'Enabled'},
            {'id': 'sub2', 'name': 'Test Sub 2', 'state': 'Enabled'}
        ]
        mock_checker_class.return_value = mock_checker
        
        # Capture stdout to verify output
        with patch('builtins.print') as mock_print:
            main()
            
        # Verify that print was called (indicating successful execution)
        mock_print.assert_called()
    
    @patch('azure_gtw_checker.AzureGatewayChecker')
    @patch('sys.argv', ['azure_gtw_checker.py', '--subscription-id', 'test-sub', '--hostname', 'test.com'])
    def test_search_hostname_cli(self, mock_checker_class):
        """Test searching hostname via CLI."""
        from azure_gtw_checker import main
        
        mock_checker = Mock()
        mock_checker.search_hostname.return_value = [
            {
                'gateway_name': 'test-gateway',
                'resource_group': 'test-rg',
                'location': 'eastus',
                'found_hostname': 'test.com',
                'all_hostnames': ['test.com', 'api.test.com']
            }
        ]
        mock_checker_class.return_value = mock_checker
        
        with patch('builtins.print') as mock_print:
            main()
            
        mock_print.assert_called()
        mock_checker.search_hostname.assert_called_once_with('test.com')
    
    @patch('sys.argv', ['azure_gtw_checker.py', '--hostname', 'test.com'])
    def test_missing_subscription_id(self):
        """Test error when subscription ID is missing for gateway operations."""
        from azure_gtw_checker import main
        
        with patch('sys.exit') as mock_exit, \
             patch('builtins.print') as mock_print:
            main()
            
        # Should be called at least once with code 1
        assert mock_exit.call_count >= 1
        assert (1,) in [call.args for call in mock_exit.call_args_list]
        
        # Check that the error message was printed
        printed_messages = [call.args[0] for call in mock_print.call_args_list]
        assert any("--subscription-id is required" in msg for msg in printed_messages)