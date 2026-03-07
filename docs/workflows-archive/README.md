# Archived GitHub Actions Workflows

These workflow files are kept **on record** but are not active. They were moved here so that `git push` works without requiring the Personal Access Token to have the `workflow` scope.

**To restore CI/CD when your PAT has `workflow` scope:**

1. Copy the desired `.yml` file(s) from this folder into `.github/workflows/`.
2. Commit and push. GitHub will run the workflows on the next matching push/PR.

**Files:**
- `backend-devsecops-pipeline.yml` – Build backend Docker image, push to ECR, deploy to EKS dev.
- `frontend-devsecops-pipeline.yml` – Build frontend, deploy to S3 dev.
