# Azure Application Gateway Hostname Checker

[![CI](https://github.com/JavierRamirezMoral/endpointsearch/workflows/CI/badge.svg)](https://github.com/JavierRamirezMoral/endpointsearch/actions)
[![Python Version](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Python script to search for hostnames in all Application Gateways of an Azure tenant using DefaultAzureCredential for authentication.

## Features

- 🔍 Search for specific hostnames across all Application Gateways
- 📝 List all hostnames configured in Application Gateways
- 🔐 Secure authentication using Azure DefaultAzureCredential
- 📊 Support for both JSON and table output formats
- 🏗️ Programmatic API for integration with other tools
- 📋 List available Azure subscriptions
- 🧪 Comprehensive test coverage

## Requirements

- Python 3.8 or higher
- Azure CLI installed and configured (for authentication)
- Appropriate Azure permissions to read Application Gateway configurations

### Azure Permissions Required

Your Azure account needs the following permissions:
- `Network Contributor` or `Reader` role on the subscription or resource groups containing Application Gateways
- `Reader` role to list subscriptions (if using `--list-subscriptions`)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/JavierRamirezMoral/endpointsearch.git
cd endpointsearch
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure Azure authentication:
```bash
# Option 1: Azure CLI login
az login

# Option 2: Set environment variables
export AZURE_CLIENT_ID="your-client-id"
export AZURE_CLIENT_SECRET="your-client-secret"
export AZURE_TENANT_ID="your-tenant-id"
```

## Usage

### Command Line Interface

#### List Available Subscriptions
```bash
python azure_gtw_checker.py --list-subscriptions
```

#### Get All Hostnames from All Application Gateways
```bash
python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --all-hostnames
```

#### Search for a Specific Hostname
```bash
python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --hostname example.com
```

#### Output in JSON Format
```bash
python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --all-hostnames --output-format json
```

#### Enable Verbose Logging
```bash
python azure_gtw_checker.py --subscription-id YOUR_SUBSCRIPTION_ID --hostname example.com --verbose
```

### Programmatic Usage

```python
from azure_gtw_checker import AzureGatewayChecker

# Initialize with subscription ID
checker = AzureGatewayChecker("your-subscription-id")

# Get all subscriptions
subscriptions = checker.get_subscriptions()

# Get all Application Gateways
gateways = checker.get_application_gateways()

# Search for a specific hostname
results = checker.search_hostname("api.example.com")

# Get all hostnames from all gateways
all_hostnames = checker.get_all_hostnames()
```

## Examples

See the [examples/](examples/) directory for:
- [usage_example.py](examples/usage_example.py) - Programmatic usage examples
- [example_output.txt](examples/example_output.txt) - Sample output formats

### Example Output

**Table Format:**
```
Hostname 'api.example.com' found in the following gateways:
------------------------------------------------------------
Gateway: prod-app-gateway
Resource Group: prod-rg
Location: eastus
All hostnames: api.example.com, www.example.com, admin.example.com
------------------------------------------------------------
```

**JSON Format:**
```json
[
  {
    "gateway_name": "prod-app-gateway",
    "resource_group": "prod-rg",
    "location": "eastus",
    "found_hostname": "api.example.com",
    "all_hostnames": [
      "api.example.com",
      "www.example.com",
      "admin.example.com"
    ]
  }
]
```

## Testing

Run the test suite:

```bash
# Install development dependencies
pip install -r requirements-dev.txt

# Run tests with coverage
pytest tests/ -v --cov=azure_gtw_checker --cov-report=term-missing

# Run specific test
pytest tests/test_azure_gtw_checker.py::TestAzureGatewayChecker::test_search_hostname_found -v
```

### Test Coverage

The test suite includes:
- Unit tests for all major functions
- Mock tests for Azure API interactions
- CLI argument parsing tests
- Error handling tests

## Development

### Code Style

This project uses:
- [Black](https://black.readthedocs.io/) for code formatting
- [isort](https://pycqa.github.io/isort/) for import sorting
- [flake8](https://flake8.pycqa.org/) for linting

Format code:
```bash
black .
isort .
flake8 .
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and add tests
4. Run the test suite: `pytest`
5. Format your code: `black . && isort .`
6. Commit your changes: `git commit -am 'Add new feature'`
7. Push to the branch: `git push origin feature/new-feature`
8. Submit a pull request

## Error Handling

The script includes comprehensive error handling for:
- Authentication failures
- Network connectivity issues
- Missing Azure permissions
- Invalid subscription IDs
- API rate limiting

## Limitations

- Requires Azure CLI or service principal authentication
- Read-only operations (does not modify Application Gateway configurations)
- Subject to Azure API rate limits
- Requires appropriate Azure RBAC permissions

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

**Javier Ramírez Moral**

## Changelog

### v1.0.0
- Initial release
- Support for hostname searching across Application Gateways
- CLI and programmatic interfaces
- Comprehensive test coverage
- CI/CD pipeline
