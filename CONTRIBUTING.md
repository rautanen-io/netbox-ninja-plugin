# Contributing to Ninja Netbox Plugin

Thank you for your interest in contributing to the Ninja Netbox Plugin! This document provides guidelines and instructions for contributing to the project.

## Table of Contents
- [Development Setup](#development-setup)
- [Development Environment](#development-environment)
- [Debugging](#debugging)
- [Code of Conduct](#code-of-conduct)
- [Getting Help](#getting-help)

## Development Setup

### Prerequisites
- [Poetry](https://python-poetry.org/) - Python dependency management and packaging tool
- Git
- Docker and Docker Compose (for local development)

### Initial Setup

1. Clone the repository:
```bash
git clone https://github.com/rautanen-io/netbox-ninja-plugin.git
cd netbox-ninja-plugin
```

2. Install dependencies:
```bash
poetry install
```

3. Start the development environment:
```bash
make debug
```

4. Wait for Netbox to start and all migrations to complete, then press `Ctrl+C` to stop the server.

5. Create a superuser:
```bash
make createsuperuser
```

6. Start the environment again:
```bash
make debug
```

7. Access the application at http://localhost:8000

## Development Environment

The `./develop` directory contains:
- A Docker Compose configuration for launching Netbox and its dependencies
- A sample `configuration.py` file for Netbox configuration
- A custom `manage.py` file that supports debugging

## Debugging

### VS Code Configuration

To enable debugging in VS Code, use the following `launch.json` configuration:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Debug Netbox",
            "type": "debugpy",
            "request": "attach",
            "connect": {
                "port": 3000,
                "host": "127.0.0.1"
            },
            "pathMappings": [
                {
                    "localRoot": "${workspaceFolder}/netbox_ninja_plugin",
                    "remoteRoot": "/opt/netbox_ninja_plugin/netbox_ninja_plugin"
                }
            ]
        }
    ]
}
```

## Code of Conduct

This project and everyone participating in it is governed by our Code of Conduct. By participating, you are expected to uphold this code. Please report any unacceptable behavior to [veikko@rautanen.io](mailto:veikko@rautanen.io).

## Getting Help

If you need assistance or have questions about contributing:
- Open an issue on GitHub
- Contact the maintainers at [veikko@rautanen.io](mailto:veikko@rautanen.io)
