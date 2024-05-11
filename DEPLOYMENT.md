# Deployment Documentation
## Overview
This document provides instructions on how to set up and deploy the project using a Git-based deployment strategy with automated service restarts and environment variable management.

## Prerequisites
- A Virtual Private Server (VPS) with SSH access.
- Git installed on both local machine and VPS.
- A bare Git repository set up on the VPS.

## Setting Up the Deployment Environment
1. Create a Bare Repository on Your VPS
```bash
mkdir -p /path/to/git/repos/your-project.git
cd /path/to/git/repos/your-project.git
git init --bare
```

2. Set Up the `post-receive` Hook
Create a `post-receive` hook to automate deployment tasks:

```bash
nano /path/to/git/repos/your-project.git/hooks/post-receive
```

Add the following script:
```bash
#!/bin/bash
GIT_WORK_TREE=/path/to/your/project git checkout -f

# Set environment variables
echo 'TELEGRAM_BOT_TOKEN=${TELEGRAM_BOT_TOKEN}' > /path/to/your/project/.env
echo 'SERVER_IP=${SERVER_IP}' >> /path/to/your/project/.env 
echo 'SERVER_PORT=${SERVER_PORT}' >> /path/to/your/project/.env

# Restart the service
sudo systemctl restart your-service-name
```

Make the hook executable:

```bash
chmod +x /path/to/git/repos/your-project.git/hooks/post-receive
```

## Deployment Process
### Using GitHub Actions

Configure GitHub Actions to automate pushing changes to the VPS:

```yaml
name: Push to VPS and Deploy

on:
  push:
    branches:
      - main

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2

    - name: Set up SSH keys
      uses: webfactory/ssh-agent@v0.5.3
      with:
        ssh-private-key: ${{ secrets.SSH_PRIVATE_KEY }}

    - name: Add remote and push
      run: |
        git remote add deploy ssh://user@your-vps-ip/path/to/git/repos/your-project.git
        git push deploy main
```

## Security Considerations
- Ensure that SSH keys are managed securely.
- Use secrets management tools for sensitive data like TELEGRAM_BOT_TOKEN.

## Adding to the Repository
1. Create or update the Markdown file: Open your text editor or use the GitHub interface to create or edit `README.md` or `DEPLOYMENT.md`.
2. Paste the content: Use the above example as a template.
3. Commit and push: Save your changes, commit, and push them to your repository.

```bash
git add README.md  # or DEPLOYMENT.md
git commit -m "Update deployment documentation"
git push origin main
```

This will help ensure anyone working with or deploying your project has clear guidelines and can maintain the necessary operational standards.