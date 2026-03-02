import os
import zipfile

# Folder structure
base_dir = "azure-analytics-demo"
terraform_dir = os.path.join(base_dir, "terraform")

os.makedirs(terraform_dir, exist_ok=True)

# File contents
files = {
    os.path.join(terraform_dir, "main.tf"): """provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}

resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}

resource "azurerm_data_factory" "adf" {
  name                = var.data_factory_name
  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location
}

resource "azurerm_databricks_workspace" "workspace" {
  name                       = var.databricks_workspace_name
  resource_group_name         = azurerm_resource_group.rg.name
  location                    = azurerm_resource_group.rg.location
  sku                         = "standard"
  managed_resource_group_name = "${var.resource_group_name}-databricks-rg"
}

resource "azurerm_sql_server" "sql" {
  name                         = var.sql_server_name
  resource_group_name           = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_sql_database" "sqldb" {
  name                = var.sql_database_name
  server_name         = azurerm_sql_server.sql.name
  resource_group_name = azurerm_resource_group.rg.name
  sku_name            = "S0"
  max_size_gb         = 5
}

resource "azurerm_network_interface" "nic" {
  name                = "${var.vm_name}-nic"
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name

  ip_configuration {
    name                          = "internal"
    subnet_id                     = var.subnet_id
    private_ip_address_allocation = "Dynamic"
  }
}

resource "azurerm_windows_virtual_machine" "vm" {
  name                  = var.vm_name
  location              = azurerm_resource_group.rg.location
  resource_group_name   = azurerm_resource_group.rg.name
  size                  = "Standard_B1s"
  admin_username        = var.vm_admin_username
  admin_password        = var.vm_admin_password
  network_interface_ids = [azurerm_network_interface.nic.id]

  os_disk {
    caching              = "ReadWrite"
    storage_account_type = "Standard_LRS"
  }

  source_image_reference {
    publisher = "MicrosoftWindowsServer"
    offer     = "WindowsServer"
    sku       = "2019-Datacenter"
    version   = "latest"
  }
}
""",
    os.path.join(terraform_dir, "variables.tf"): """variable "resource_group_name" {}
variable "location" { default = "eastus" }

variable "storage_account_name" {}
variable "data_factory_name" {}
variable "databricks_workspace_name" {}
variable "sql_server_name" {}
variable "sql_database_name" {}
variable "sql_admin_username" {}
variable "sql_admin_password" {}

variable "vm_name" {}
variable "vm_admin_username" {}
variable "vm_admin_password" {}
variable "subnet_id" {}
""",
    os.path.join(terraform_dir, "outputs.tf"): """output "storage_account_name" {
  value = azurerm_storage_account.storage.name
}

output "data_factory_name" {
  value = azurerm_data_factory.adf.name
}

output "databricks_workspace_url" {
  value = azurerm_databricks_workspace.workspace.workspace_url
}

output "sql_server_name" {
  value = azurerm_sql_server.sql.name
}

output "sql_database_name" {
  value = azurerm_sql_database.sqldb.name
}

output "vm_name" {
  value = azurerm_windows_virtual_machine.vm.name
}
""",
    os.path.join(terraform_dir, "terraform.tfvars"): """resource_group_name          = "rg-analytics-demo"
storage_account_name         = "stganalytics001"
data_factory_name            = "adf-demo"
databricks_workspace_name    = "dbx-demo"
sql_server_name              = "sqlserverdemo001"
sql_database_name            = "sqldb-demo"
sql_admin_username           = "sqladmin"
sql_admin_password           = "P@ssw0rd123!"

vm_name                      = "vm-demo"
vm_admin_username            = "vmadmin"
vm_admin_password            = "VmP@ss123!"
subnet_id                    = "/subscriptions/<SUBSCRIPTION_ID>/resourceGroups/rg-analytics-demo/providers/Microsoft.Network/virtualNetworks/vnet1/subnets/default"
""",
    os.path.join(base_dir, "azure-pipelines.yml"): """trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

variables:
  tfWorkingDir: 'terraform'
  azureServiceConnection: 'Azure-SP-Terraform'

stages:
- stage: Terraform
  displayName: "Terraform CI/CD"
  jobs:
  - job: Terraform_Deploy
    displayName: "Terraform Init, Plan, Apply"
    steps:
    - task: TerraformInstaller@1
      inputs:
        terraformVersion: '1.7.0'

    - script: terraform init
      workingDirectory: $(tfWorkingDir)
      displayName: 'Terraform Init'

    - script: terraform plan -out=tfplan
      workingDirectory: $(tfWorkingDir)
      displayName: 'Terraform Plan'

    - task: AzureCLI@2
      displayName: 'Upload Terraform Plan'
      inputs:
        azureSubscription: $(azureServiceConnection)
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az storage blob upload \
            --account-name mystorageacct \
            --container-name terraform-plans \
            --name tfplan_$(Build.BuildId) \
            --file $(tfWorkingDir)/tfplan \
            --overwrite true

    - script: terraform apply -auto-approve tfplan
      workingDirectory: $(tfWorkingDir)
      displayName: 'Terraform Apply'
""",
    os.path.join(base_dir, "README.md"): """# Azure Analytics Demo Repo

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
"""
}

# Write files
for path, content in files.items():
    with open(path, "w") as f:
        f.write(content)

# Create ZIP
zip_filename = "azure-analytics-demo.zip"
with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for foldername, subfolders, filenames in os.walk(base_dir):
        for filename in filenames:
            filepath = os.path.join(foldername, filename)
            zipf.write(filepath, os.path.relpath(filepath, base_dir))

print(f"ZIP file created: {zip_filename}")
