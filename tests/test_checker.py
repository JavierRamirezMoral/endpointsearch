import pytest
from unittest.mock import Mock, patch
import azure_gtw_checker as checker

def fake_ag(name, rg, listeners=None, rules=None):
    return {
        'name': name,
        'resource_group': rg,
        'http_listeners': listeners or [],
        'request_routing_rules': rules or []
    }

def test_search_hostname_found(monkeypatch):
    ags = [
        fake_ag('app-gtw-prod', 'rg-prod', listeners=[{'host_name': 'ejemplo.com'}]),
        fake_ag('app-gtw-dr', 'rg-dr', listeners=[{'host_name': 'otro.com'}]),
    ]
    monkeypatch.setattr(checker, 'list_application_gateways', lambda sub, cred: ags)
    results = checker.search_hostname('fake-sub', 'ejemplo.com', credential=Mock())
    assert isinstance(results, list)
    assert any(r['name'] == 'app-gtw-prod' for r in results)

def test_search_hostname_not_found(monkeypatch):
    ags = [fake_ag('app-gtw', 'rg', listeners=[{'host_name': 'no-coincide.com'}])]
    monkeypatch.setattr(checker, 'list_application_gateways', lambda sub, cred: ags)
    results = checker.search_hostname('fake-sub', 'noexiste.com', credential=Mock())
    assert results == []
