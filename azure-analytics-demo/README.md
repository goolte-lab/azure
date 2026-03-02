# Azure Analytics Demo Repo

This repository contains Terraform code to deploy:

- Azure Storage
- Azure Data Factory
- Azure Databricks
- Azure SQL Database
- Azure Virtual Machine
- Azure DevOps Pipeline

## Structure

- terraform/: All Terraform files
- azure-pipelines.yml: DevOps pipeline YAML
- README.md: This file

## How to use

1. Update `terraform/terraform.tfvars` with your values.
2. Push repo to Azure DevOps.
3. Run the pipeline to deploy resources.
