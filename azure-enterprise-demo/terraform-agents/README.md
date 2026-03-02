# Terraform - Azure DevOps Self-Hosted Agent

This Terraform module deploys a Virtual Machine in Azure and prepares it to be used as a self-hosted Azure DevOps agent.

## What This Module Deploys

- Azure Virtual Machine (Linux or Windows)
- Network Interface
- OS Disk
- Agent registration script (via custom_data or extension)

## Architecture

Azure VM → Registers to Azure DevOps Agent Pool → Executes Pipelines

## Required Variables

| Variable | Description |
|----------|------------|
| resource_group_name | Resource Group where VM is deployed |
| location | Azure region |
| vm_name | Name of the Virtual Machine |
| vm_admin_username | Admin username |
| vm_admin_password | Admin password |
| subnet_id | Subnet ID for VM |
| azure_devops_url | Azure DevOps organization URL |
| azure_devops_pat | Personal Access Token (Agent Pool permission) |
| azure_devops_pool | Agent Pool name |

## Example terraform.tfvars
