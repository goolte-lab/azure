# Terraform - Azure Analytics & Database Infrastructure

This Terraform module deploys the core analytics stack in Azure.

## What This Module Deploys

- Azure Storage Account
- Azure SQL Server
- Azure SQL Database
- (Optional) Azure Data Factory
- (Optional) Azure Databricks Workspace

## Architecture Flow

Storage → Data Factory → Databricks → Azure SQL Database

## Required Variables

| Variable | Description |
|----------|------------|
| resource_group_name | Target Resource Group |
| location | Azure region |
| storage_account_name | Globally unique storage name |
| sql_server_name | SQL server name |
| sql_database_name | Database name |
| sql_admin_username | SQL admin login |
| sql_admin_password | SQL admin password |

## Example terraform.tfvars
