
# Azure Enterprise Terraform Deployment with Multi-Environment Approvals

This repository implements an **enterprise-ready Terraform deployment** using Azure DevOps Pipelines, including:

- Multi-environment promotion: Dev → Test → Production
- Manual approval gates
- Email notifications for approvals
- Terraform Plan/Apply separation
- PR validation

---

## Repository Structure

```text
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
```

Each `*.tfvars` file contains environment-specific configuration.

---

## 1. Create Azure Service Connection (Service Principal)

Terraform in Azure DevOps requires a **Service Principal** for authentication.

1. Go to **Azure DevOps → Project Settings → Service Connections**
2. Click **New Service Connection → Azure Resource Manager**
3. Select **Service Principal (automatic)**
4. Choose the target subscription
5. Name it, e.g.:  

```
Azure-Service-Connection-Name
```

6. Grant access permission to all pipelines
7. Use this name in the YAML variable `azureServiceConnection`

> Terraform tasks in the pipeline will use this connection for provisioning resources.

---

## 2. Create Environments in Azure DevOps

Environments allow **approval gates and email notifications**.

1. Go to **Pipelines → Environments**
2. Create three environments:
   - `Dev`
   - `Test`
   - `Production`

---

## 3. Configure Approval Gates

### Test Environment
1. Open **Environment → Test**
2. Click **Approvals and Checks → Add approval**
3. Assign approvers (users or groups)
4. Save

### Production Environment
1. Open **Environment → Production**
2. Click **Approvals and Checks → Add approval**
3. Assign approvers (users or groups)
4. Optional: Require multiple approvers
5. Save

> Approvals automatically trigger email notifications to approvers.

---

## 4. Email Notifications

When a deployment reaches a stage associated with an environment that has **approval gates**:

- Azure DevOps sends **email notifications** to all approvers
- The pipeline pauses until an approval is completed
- Approvers can approve via **email link** or **Azure DevOps UI**

No extra YAML configuration is required for email.

---

## 5. Branch Protection & PR Validation (Recommended)

1. Go to **Repos → Branches → main**
2. Enable:
   - Require Pull Request for changes
   - Require successful build for PR
   - Require at least one reviewer
3. This ensures Dev/Test/Prod pipelines only run on approved merges

---

## 6. Terraform Backend (Recommended)

Use an **Azure Storage Account** to store state per environment:

```hcl
terraform {
  backend "azurerm" {
    resource_group_name  = "rg-terraform-state"
    storage_account_name = "tfstatestorage"
    container_name       = "tfstate"
    key                  = "dev.terraform.tfstate"
  }
}
```

> Use separate `key` values per environment (`dev`, `test`, `prod`) for isolated state.

---

## 7. Promotion Workflow

| Stage | Trigger | Approval |
|-------|---------|----------|
| Dev   | Auto on merge | None |
| Test  | After Dev   | Required |
| Prod  | After Test  | Required + Email |

---

## 8. Security Best Practices

- Do **NOT** store passwords, secrets, or PATs in repo
- Use:
  - Azure DevOps secret variables
  - Variable groups
  - Azure Key Vault integration

- Restrict Production deployment permissions
- Enable RBAC and auditing for critical resources

---

## 9. Running the Pipeline

1. Ensure **Terraform code is valid**
2. Push changes to `main`
3. Dev stage runs automatically
4. Approvers handle Test and Production stages
5. Monitor deployments in **Pipelines → Runs**
