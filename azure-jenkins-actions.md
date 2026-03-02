# CI/CD Platform Terminology Comparison

This table shows equivalent terms between Azure DevOps, Jenkins, and GitHub Actions:

| Feature / Concept               | Azure DevOps                                      | Jenkins                                   | GitHub Actions                            | Notes                                       |
| ------------------------------- | ------------------------------------------------- | ----------------------------------------- | ----------------------------------------- | ------------------------------------------- |
| **Pipeline**                    | Pipeline                                          | Job / Pipeline / Multi-branch Pipeline    | Workflow                                  | Represents the CI/CD process                |
| **Stage**                       | Stage                                             | Stage (in Declarative Pipeline)           | Job                                       | Logical grouping of steps                   |
| **Job**                         | Job                                               | Stage or Job                              | Job                                       | Runs on an agent/runner                     |
| **Step / Task**                 | Task / Script                                     | Step / Shell / Build Step                 | Step                                      | Individual command or task                  |
| **Trigger**                     | `trigger`, `pr`                                   | Poll SCM / webhook / multibranch trigger  | `on:` (push, pull_request, schedule)      | Defines when pipeline runs                  |
| **Agent / Runner**              | Agent Pool → Agent                                | Node / Executor / Agent                   | Runner                                    | Executes jobs                               |
| **Artifact**                    | Pipeline Artifacts                                | Archive / Archive Artifacts               | `actions/upload-artifact`                 | Outputs of builds or pipelines              |
| **Environment**                 | Environment (with approvals & checks)             | Folder / Job / Node labels                | Environment / Deployment jobs             | Can include approvals or deployment targets |
| **Approval / Gate**             | Approvals and Checks                              | Input step / external approval plugin     | `workflow_run` + required reviewers       | Manual intervention before deployment       |
| **Variable**                    | Pipeline Variables / Variable Groups              | Parameters / Environment Variables        | `env:` or `secrets:`                      | Configurable values in pipelines            |
| **Secret / Credentials**        | Azure DevOps Service Connection / Secret Variable | Credentials Plugin / Secrets              | `secrets`                                 | Stored securely for access                  |
| **Template / Reuse**            | YAML Templates                                    | Shared Library / Jenkinsfile Shared Steps | Reusable Workflow / Composite Actions     | Reuse pipeline definitions                  |
| **Source Control Integration**  | Git / Azure Repos / GitHub / SVN                  | Git / SVN / Mercurial etc.                | GitHub repo (native)                      | Where pipeline triggers come from           |
| **Terraform / IaC integration** | Terraform Task / CLI                              | Terraform Plugin / Shell step             | Terraform CLI in steps                    | All can integrate with Terraform            |
| **Notifications**               | Email / Teams / Slack via Service Hook            | Email / Slack Plugin                      | Actions / Webhooks / GitHub notifications | Alerts for builds/deployments               |
| **Pipeline as Code**            | YAML                                              | Jenkinsfile                               | YAML (`.github/workflows/`)               | Version controlled CI/CD                    |
