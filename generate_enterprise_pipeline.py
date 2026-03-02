import os
from pathlib import Path
import zipfile

# Base directories
BASE_DIR = "azure-enterprise"
TERRAFORM_DIR = os.path.join(BASE_DIR, "terraform")
ENVIRONMENTS_DIR = os.path.join(BASE_DIR, "environments")
PIPELINE_FILE = os.path.join(BASE_DIR, "azure-pipelines-enterprise.yml")
README_FILE = os.path.join(BASE_DIR, "README.md")

terraform_folders = ["agents", "database"]

# 1️⃣ Create folders
folders_to_create = [BASE_DIR, TERRAFORM_DIR, ENVIRONMENTS_DIR]
folders_to_create += [os.path.join(TERRAFORM_DIR, f) for f in terraform_folders]

for folder in folders_to_create:
    Path(folder).mkdir(parents=True, exist_ok=True)

# 2️⃣ Create placeholder main.tf
main_tf_content = """# Terraform placeholder
terraform {
  required_version = ">= 1.0"
}
"""

for tf_folder in terraform_folders:
    tf_path = os.path.join(TERRAFORM_DIR, tf_folder, "main.tf")
    if not os.path.exists(tf_path):
        with open(tf_path, "w", encoding="utf-8") as f:
            f.write(main_tf_content)

# 3️⃣ Create empty tfvars files
for env in ["dev", "test", "prod"]:
    tfvars_path = os.path.join(ENVIRONMENTS_DIR, f"{env}.tfvars")
    if not os.path.exists(tfvars_path):
        with open(tfvars_path, "w", encoding="utf-8") as f:
            f.write(f"# {env} environment variables\n")

# 4️⃣ Create README.md
readme_content = """
# Azure Enterprise Terraform Deployment with Multi-Environment Approvals

This repository implements an enterprise-ready Terraform deployment using Azure DevOps Pipelines, including:

- Multi-environment promotion: Dev → Test → Production
- Manual approval gates
- Email notifications for approvals
- Terraform Plan/Apply separation
- PR validation

## Repository Structure

azure-enterprise/
├── terraform/
│   ├── agents/
│   └── database/
├── environments/
│   ├── dev.tfvars
│   ├── test.tfvars
│   └── prod.tfvars
├── azure-pipelines-enterprise.yml
└── README.md

## Service Connection Setup

1. Azure DevOps → Project Settings → Service Connections
2. New Service Connection → Azure Resource Manager
3. Service Principal (automatic)
4. Name it: Azure-Service-Connection-Name
5. Grant access to pipelines

## Environments & Approval Gates

- Create environments: Dev, Test, Production
- Test & Production: Add Approval → Assign approvers
- Emails sent automatically when approval is needed

## Promotion Workflow

Dev → Test → Prod
"""

with open(README_FILE, "w", encoding="utf-8") as f:
    f.write(readme_content)

# 5️⃣ Create full azure-pipelines-enterprise.yml
pipeline_content = """
trigger:
  branches:
    include:
      - main

pr:
  branches:
    include:
      - main

variables:
  terraformVersion: '1.7.5'
  azureServiceConnection: 'Azure-Service-Connection-Name'

stages:

# Validate Stage
- stage: Validate
  displayName: "Validate Terraform"
  jobs:
  - job: Validate
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: TerraformInstaller@1
      inputs:
        terraformVersion: $(terraformVersion)
    - script: |
        cd terraform/agents
        terraform init -backend=false
        terraform fmt -check
        terraform validate
      displayName: "Validate Agents"
    - script: |
        cd terraform/database
        terraform init -backend=false
        terraform fmt -check
        terraform validate
      displayName: "Validate Database"

# Dev Plan & Apply
- stage: Plan_Dev
  dependsOn: Validate
  displayName: "Plan - Dev"
  jobs:
  - job: PlanDev
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: TerraformInstaller@1
      inputs:
        terraformVersion: $(terraformVersion)
    - task: AzureCLI@2
      inputs:
        azureSubscription: $(azureServiceConnection)
        scriptType: bash
        scriptLocation: inlineScript
        inlineScript: |
          cd terraform/database
          terraform init
          terraform plan -var-file=../../environments/dev.tfvars -out=tfplan
    - publish: terraform/database/tfplan
      artifact: dev-plan

- stage: Apply_Dev
  dependsOn: Plan_Dev
  displayName: "Apply - Dev"
  jobs:
  - deployment: DeployDev
    environment: Dev
    strategy:
      runOnce:
        deploy:
          steps:
          - download: current
            artifact: dev-plan
          - task: TerraformInstaller@1
            inputs:
              terraformVersion: $(terraformVersion)
          - task: AzureCLI@2
            inputs:
              azureSubscription: $(azureServiceConnection)
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                cd terraform/database
                terraform init
                terraform apply -auto-approve tfplan

# Test Plan & Apply
- stage: Plan_Test
  dependsOn: Apply_Dev
  displayName: "Plan - Test"
  jobs:
  - job: PlanTest
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: TerraformInstaller@1
      inputs:
        terraformVersion: $(terraformVersion)
    - task: AzureCLI@2
      inputs:
        azureSubscription: $(azureServiceConnection)
        scriptType: bash
        scriptLocation: inlineScript
        inlineScript: |
          cd terraform/database
          terraform init
          terraform plan -var-file=../../environments/test.tfvars -out=tfplan
    - publish: terraform/database/tfplan
      artifact: test-plan

- stage: Apply_Test
  dependsOn: Plan_Test
  displayName: "Apply - Test"
  jobs:
  - deployment: DeployTest
    environment: Test
    strategy:
      runOnce:
        deploy:
          steps:
          - download: current
            artifact: test-plan
          - task: TerraformInstaller@1
            inputs:
              terraformVersion: $(terraformVersion)
          - task: AzureCLI@2
            inputs:
              azureSubscription: $(azureServiceConnection)
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                cd terraform/database
                terraform init
                terraform apply -auto-approve tfplan

# Prod Plan & Apply
- stage: Plan_Prod
  dependsOn: Apply_Test
  displayName: "Plan - Production"
  jobs:
  - job: PlanProd
    pool:
      vmImage: 'ubuntu-latest'
    steps:
    - task: TerraformInstaller@1
      inputs:
        terraformVersion: $(terraformVersion)
    - task: AzureCLI@2
      inputs:
        azureSubscription: $(azureServiceConnection)
        scriptType: bash
        scriptLocation: inlineScript
        inlineScript: |
          cd terraform/database
          terraform init
          terraform plan -var-file=../../environments/prod.tfvars -out=tfplan
    - publish: terraform/database/tfplan
      artifact: prod-plan

- stage: Apply_Prod
  dependsOn: Plan_Prod
  displayName: "Apply - Production"
  jobs:
  - deployment: DeployProd
    environment: Production
    strategy:
      runOnce:
        deploy:
          steps:
          - download: current
            artifact: prod-plan
          - task: TerraformInstaller@1
            inputs:
              terraformVersion: $(terraformVersion)
          - task: AzureCLI@2
            inputs:
              azureSubscription: $(azureServiceConnection)
              scriptType: bash
              scriptLocation: inlineScript
              inlineScript: |
                cd terraform/database
                terraform init
                terraform apply -auto-approve tfplan
"""

with open(PIPELINE_FILE, "w", encoding="utf-8") as f:
    f.write(pipeline_content)

# 6️⃣ Create ZIP
# 6️⃣ Create ZIP for Windows
zip_file_path = os.path.join(BASE_DIR, "azure-enterprise-full.zip")
with zipfile.ZipFile(zip_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            file_path = os.path.join(root, file)
            zipf.write(file_path, os.path.relpath(file_path, BASE_DIR))

print(f"✅ Full enterprise repo ZIP created: {zip_file_path}")

 