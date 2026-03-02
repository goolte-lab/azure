# Azure Analytics Infrastructure with Terraform and Azure DevOps

## Overview

This repository demonstrates a full **Azure Analytics infrastructure** deployment using **Terraform** and **Azure DevOps pipelines**.  
It includes:

- **Azure Storage Account**: Raw and processed data storage
- **Azure Data Factory (ADF)**: Data orchestration and pipelines
- **Azure Databricks**: Data transformation and analytics
- **Azure SQL Database**: Structured data storage
- **Azure Virtual Machine (VM)**: Optional compute / admin tasks
- **Azure DevOps Pipeline**: CI/CD to deploy and manage resources

All resources are deployed in a single **Resource Group** and can be connected through Terraform outputs.

---

## Architecture & Data Flow

```text
 [Storage Account]   ← raw / processed data
        │
        ▼
 [Data Factory] ─ triggers ─> [Databricks]
        │                         │
        ▼                         ▼
  [SQL Database]  ← processed data
        ▲
        │
    [Virtual Machine] (optional admin / scripts)
```

- **Storage**: Provides input/output for pipelines and notebooks  
- **ADF**: Orchestrates pipelines and triggers Databricks notebooks  
- **Databricks**: Processes and transforms data, writes to SQL  
- **SQL Database**: Stores structured, processed data  
- **VM**: Optional compute for scripts or testing  
- **Resource Group**: Central container for all resources, simplifying identity and networking  

---

## Terraform Resources

### Resource Group

```hcl
resource "azurerm_resource_group" "rg" {
  name     = var.resource_group_name
  location = var.location
}
```

### Storage Account

```hcl
resource "azurerm_storage_account" "storage" {
  name                     = var.storage_account_name
  resource_group_name      = azurerm_resource_group.rg.name
  location                 = azurerm_resource_group.rg.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
}
```

### Data Factory

```hcl
resource "azurerm_data_factory" "adf" {
  name                = var.data_factory_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
}
```

### Databricks Workspace

```hcl
resource "azurerm_databricks_workspace" "workspace" {
  name                        = var.databricks_workspace_name
  resource_group_name          = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  sku                          = "standard"
  managed_resource_group_name  = "${var.resource_group_name}-databricks-rg"
}
```

### SQL Database

```hcl
resource "azurerm_sql_server" "sql" {
  name                         = var.sql_server_name
  resource_group_name           = azurerm_resource_group.rg.name
  location                     = azurerm_resource_group.rg.location
  administrator_login          = var.sql_admin_username
  administrator_login_password = var.sql_admin_password
}

resource "azurerm_sql_database" "sqldb" {
  name                = var.sql_database_name
  resource_group_name = azurerm_resource_group.rg.name
  server_name         = azurerm_sql_server.sql.name
  sku_name            = "S0"
  max_size_gb         = 5
}
```

### Virtual Machine

```hcl
resource "azurerm_windows_virtual_machine" "vm" {
  name                = var.vm_name
  location            = azurerm_resource_group.rg.location
  resource_group_name = azurerm_resource_group.rg.name
  size                = "Standard_B1s"
  admin_username      = var.vm_admin_username
  admin_password      = var.vm_admin_password
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
```

---

## Terraform Inputs & Connections

| Resource         | Inputs Needed                                           | Connected To / Purpose                                     |
|-----------------|--------------------------------------------------------|-----------------------------------------------------------|
| Storage Account  | Name, container, key or SAS                            | ADF pipelines, Databricks notebooks, VM optional         |
| ADF             | Storage account name, container, SQL DB info          | Orchestrates pipelines → triggers Databricks / SQL       |
| Databricks      | Storage account, SQL DB credentials, notebook params | Processes data, writes to SQL, triggered by ADF         |
| SQL Database    | Server, database, credentials or managed identity     | Sink for processed data from ADF/Databricks             |
| VM              | Optional: Storage access, SQL connection             | Admin tasks, scripts, monitoring                         |

- Terraform outputs can be passed to ADF pipelines or Databricks jobs to **wire connections dynamically**.

---

## Azure DevOps Pipeline

### Stages

1. **Terraform Init**: Initializes the Terraform working directory
2. **Terraform Plan**: Generates plan and optionally stores it in **Azure Storage**
3. **Review / Approval**: Optional manual approval
4. **Terraform Apply**: Applies the exact plan, updating only changed resources

### Sample YAML

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

stages:
- stage: Terraform
  displayName: "Deploy Analytics Infrastructure"
  jobs:
  - job: Terraform_Deploy
    displayName: "Terraform Init, Plan, Apply"
    steps:

    - task: TerraformInstaller@1
      inputs:
        terraformVersion: '1.7.0'

    - script: terraform init
      workingDirectory: terraform
      displayName: 'Terraform Init'

    - script: terraform plan -out=tfplan
      workingDirectory: terraform
      displayName: 'Terraform Plan'

    - task: AzureCLI@2
      displayName: 'Upload Plan to Storage'
      inputs:
        azureSubscription: 'Azure-SP-Terraform'
        scriptType: 'bash'
        scriptLocation: 'inlineScript'
        inlineScript: |
          az storage blob upload \
            --account-name stfterraform001 \
            --container-name plans \
            --name tfplan_$(Build.BuildId) \
            --file terraform/tfplan \
            --overwrite true

    - script: terraform apply -auto-approve tfplan
      workingDirectory: terraform
      displayName: 'Terraform Apply'
```

---

## Typical Changes Managed via Pipeline

| Resource        | Typical Changes                                                      |
|-----------------|----------------------------------------------------------------------|
| Storage         | Add containers, update replication, network rules                   |
| ADF             | Add/modify pipelines, datasets, linked services                     |
| Databricks      | Add/modify clusters, notebooks, jobs, libraries                     |
| SQL Database    | Add/modify databases, SKU, firewall rules                            |
| VM              | Resize VM, add disks, modify extensions                               |

- Terraform tracks incremental changes and updates **only what changed**.
- Plan can be **stored in Azure Storage** for review and audit.

---

## Best Practices

- Use **Azure DevOps Service Principal** for Terraform authentication.  
- Store **sensitive secrets** in pipeline variables or Azure Key Vault.  
- Use **Terraform outputs** to dynamically connect ADF pipelines and Databricks jobs.  
- Use **VNet / Subnets** for private network connections between Databricks, SQL, and VM.  

---

## References

- [Terraform Azure Provider](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs)  
- [Azure Data Factory Terraform](https://registry.terraform.io/providers/hashicorp/azurerm/latest/docs/resources/data_factory)  
- [Azure Databricks Terraform](https://registry.terraform.io/providers/databricks/databricks/latest/docs)  
- [Azure DevOps Terraform Pipeline](https://learn.microsoft