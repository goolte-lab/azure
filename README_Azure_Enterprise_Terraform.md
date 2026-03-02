
# Azure Enterprise Terraform Deployment with Multi-Environment Approvals

This repository implements an enterprise-ready Infrastructure-as-Code deployment using:

- Azure DevOps Pipelines
- Terraform
- Multi-environment promotion (Dev → Test → Production)
- Manual approval gates
- Email approval notifications
- Plan/Apply separation

---

# Architecture Overview

Terraform code is organized by resource type:

terraform/
  ├── agents/
  └── database/

Environment-specific configuration:

environments/
  ├── dev.tfvars
  ├── test.tfvars
  └── prod.tfvars

Pipeline file:

azure-pipelines-enterprise.yml

---

# Deployment Flow

1. Pull Request → Validate stage runs
2. Merge to main → Dev Plan & Apply
3. After Dev → Test Plan
4. Test Apply requires approval
5. After Test → Production Plan
6. Production Apply requires approval + email notification

Flow:

PR → Validate → Dev → (Approve) Test → (Approve) Production

---

# Step 1: Create Azure Service Connection

1. Go to Azure DevOps
2. Project Settings
3. Service Connections
4. New Service Connection
5. Choose Azure Resource Manager
6. Select Service Principal (automatic)
7. Name it:

Azure-Service-Connection-Name

8. Grant access permission to all pipelines

---

# Step 2: Create Environments in Azure DevOps

Go to:

Pipelines → Environments

Create three environments:

- Dev
- Test
- Production

---

# Step 3: Configure Approval Gates

## For Test Environment

1. Open Environment → Test
2. Click Approvals and Checks
3. Add Approval
4. Add required approvers (users or groups)
5. Save

## For Production Environment

1. Open Environment → Production
2. Click Approvals and Checks
3. Add Approval
4. Add required approvers
5. Optional: Require multiple approvers
6. Save

---

# Email Notification Behavior

When a deployment reaches a stage that uses:

environment: Test
environment: Production

Azure DevOps automatically:

- Sends approval email to assigned approvers
- Displays approval request in DevOps UI
- Pauses pipeline until approval

No additional YAML configuration is required for email.

---

# Step 4: Configure Branch Protection (Recommended)

In Repos → Branches → main:

- Enable PR validation
- Require successful build
- Require reviewers

This prevents direct production changes without review.

---

# Step 5: Configure Terraform Backend (Recommended)

For enterprise setups, use Azure Storage backend:

terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstatestorage"
    container_name       = "tfstate"
    key                  = "dev.terraform.tfstate"
  }
}

Use separate state files per environment:
- dev.terraform.tfstate
- test.terraform.tfstate
- prod.terraform.tfstate

---

# Security Best Practices

Do NOT store:

- SQL passwords
- PAT tokens
- Secrets

Instead use:

- Azure DevOps secret variables
- Variable groups
- Azure Key Vault integration

---

# Promotion Strategy

Dev:
- Auto deploy
- Used for development testing

Test:
- Requires manual approval
- Used for QA validation

Production:
- Requires approval
- Optional multi-approver requirement
- Can require change management integration

---

# Enterprise Governance Recommendations

- Use separate subscriptions for Dev/Test/Prod
- Restrict Production deployment permissions
- Enable audit logs
- Enable state locking
- Enable RBAC restrictions
- Monitor cost and security posture

---

This setup follows enterprise CI/CD best practices for Azure infrastructure deployments.
