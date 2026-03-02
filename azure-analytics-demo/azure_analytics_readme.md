# Azure Analytics Demo + DevOps Agent

This repository contains Terraform code and Azure DevOps pipeline to deploy:

- Azure Storage
- Azure Data Factory
- Azure Databricks
- Azure SQL Database
- Azure Virtual Machine
- Self-hosted Azure DevOps Agent VM (Linux or Windows)
- Azure DevOps Pipeline

---

## Folder Structure

```
azure-analytics-demo/
├── terraform/
│   ├── main.tf
│   ├── variables.tf
│   ├── outputs.tf
│   └── terraform.tfvars
├── azure-pipelines.yml
└── README.md
```

---

## How It Works

1. **Terraform** provisions Azure resources:
   - Storage → ADF → Databricks → SQL → VM
2. **DevOps agent VM** is automatically registered via startup script (`custom_data` for Linux or `CustomScriptExtension` for Windows)
3. **Azure DevOps pipeline** runs:
   - `terraform init`
   - `terraform plan` → optionally uploads plan to storage
   - `terraform apply` → deploys resources

---

## Terraform Variables

- `resource_group_name`  
- `storage_account_name`  
- `data_factory_name`  
- `databricks_workspace_name`  
- `sql_server_name`  
- `sql_database_name`  
- `vm_name`  
- `vm_admin_username` / `vm_admin_password`  
- `subnet_id`  
- `azure_devops_url` (Org URL)  
- `azure_devops_pat` (PAT with Agent Pool rights)  
- `azure_devops_pool` (Agent pool name)  

> **Security Note:** Store PAT in Key Vault or as secret variables. Never commit in repo.

---

## How to Use

1. Update `terraform/terraform.tfvars` and variables for your environment.
2. Run the Python script `create_template.py` to generate all files locally and ZIP them.
3. Push the ZIP to Azure DevOps repository.
4. Run the pipeline to deploy Azure resources and register the DevOps agent automatically.

