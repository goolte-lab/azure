
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
