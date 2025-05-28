# Automated PR Review Setup Guide

This guide explains how to set up the automated PR review system for your repository.

## Overview

The automated PR review system uses GitHub Actions to trigger AI-powered code reviews on new pull requests. When a PR is opened or updated, the system:

1. Analyzes the changed files and code diff
2. Sends the code to an AI service (Claude or GPT-4) for review
3. Posts a comprehensive review as a comment on the PR

## Prerequisites

1. **GitHub Repository** with Actions enabled
2. **AI Service API Key** (Anthropic Claude or OpenAI GPT-4)
3. **GitHub Personal Access Token** (if needed for private repos)

## Setup Steps

### 1. Repository Configuration

The following files are already included in this repository:

```
.github/workflows/pr-review.yml    # GitHub Actions workflow
scripts/pr-reviewer.js             # Main review script
scripts/package.json               # Node.js dependencies
```

### 2. GitHub Secrets Configuration

Add the following secrets to your GitHub repository:

1. Go to your repository on GitHub
2. Navigate to **Settings** → **Secrets and variables** → **Actions**
3. Add these repository secrets:

#### Required Secrets

- **`ANTHROPIC_API_KEY`** (recommended): Your Anthropic Claude API key
  - Get from: https://console.anthropic.com/
  - Used for high-quality code reviews

#### Optional Secrets

- **`OPENAI_API_KEY`**: Your OpenAI API key (fallback option)
  - Get from: https://platform.openai.com/api-keys
  - Used if Anthropic is unavailable

#### GitHub Token

The workflow uses `GITHUB_TOKEN` which is automatically provided by GitHub Actions.

### 3. AI Service Setup

#### Option A: Anthropic Claude (Recommended)

1. Sign up at https://console.anthropic.com/
2. Create an API key
3. Add it as `ANTHROPIC_API_KEY` secret in GitHub

#### Option B: OpenAI GPT-4

1. Sign up at https://platform.openai.com/
2. Create an API key
3. Add it as `OPENAI_API_KEY` secret in GitHub

### 4. Workflow Configuration

The workflow is configured to trigger on:
- New pull requests (`opened`)
- PR updates (`synchronize`)
- Target branches: `main`, `develop`, `master`

#### Customization Options

Edit `.github/workflows/pr-review.yml` to customize:

```yaml
# Change target branches
branches: [main, develop, master, your-branch]

# Skip reviews for specific conditions
if: github.actor != 'github-actions[bot]' && !contains(github.event.pull_request.title, '[skip-review]')
```

### 5. Testing the Setup

1. **Create a test PR**:
   ```bash
   git checkout -b test-pr-review
   echo "console.log('test');" > test.js
   git add test.js
   git commit -m "Add test file"
   git push origin test-pr-review
   ```

2. **Open a PR** on GitHub targeting your main branch

3. **Check the Actions tab** to see the workflow running

4. **Verify the review comment** appears on the PR

## Usage

### Normal Operation

Once set up, the system automatically reviews all new PRs. No manual intervention required.

### Skipping Reviews

To skip automated review for a specific PR, include `[skip-review]` in the PR title:

```
feat: Add new feature [skip-review]
```

### Review Quality

The AI reviewer analyzes:
- Code quality and readability
- Best practices adherence
- Potential bugs and security issues
- Architecture and design patterns
- Test coverage
- Documentation completeness

## Troubleshooting

### Common Issues

1. **Workflow not triggering**:
   - Check if GitHub Actions are enabled
   - Verify the workflow file is in `.github/workflows/`
   - Ensure target branch matches your setup

2. **AI API errors**:
   - Verify API keys are correctly set in GitHub Secrets
   - Check API key permissions and quotas
   - Review GitHub Actions logs for error details

3. **Review not posting**:
   - Check GitHub token permissions
   - Verify the bot has write access to issues/PRs
   - Look for errors in the "Post Review Comment" step

### Debugging

1. **Check GitHub Actions logs**:
   - Go to Actions tab in your repository
   - Click on the failed workflow run
   - Expand each step to see detailed logs

2. **Test locally**:
   ```bash
   cd scripts
   npm install
   
   # Set environment variables
   export ANTHROPIC_API_KEY="your-key"
   export PR_NUMBER="1"
   export PR_TITLE="Test PR"
   
   # Run the script
   node pr-reviewer.js
   ```

## Cost Considerations

### API Usage Costs

- **Anthropic Claude**: ~$0.01-0.05 per review (depending on code size)
- **OpenAI GPT-4**: ~$0.02-0.10 per review (depending on code size)
- **GitHub Actions**: Free for public repos, included minutes for private repos

### Cost Optimization

1. **Limit file types**: Modify workflow to only review specific file extensions
2. **Size limits**: Skip reviews for very large PRs
3. **Frequency limits**: Only review on specific events
4. **Caching**: Implement review caching for similar changes

## Security Considerations

### API Key Security

- ✅ Store API keys in GitHub Secrets (encrypted)
- ✅ Never commit API keys to code
- ✅ Use least-privilege API keys when possible
- ✅ Regularly rotate API keys

### Code Privacy

- ⚠️ Code is sent to external AI services
- ⚠️ Consider data privacy policies of AI providers
- ⚠️ May not be suitable for highly sensitive codebases

### Access Control

- ✅ Workflow only runs on PR events
- ✅ Uses GitHub's built-in permissions
- ✅ Bot comments are clearly marked as automated

## Advanced Configuration

### Custom Review Templates

Modify the `createReviewPrompt` function in `scripts/pr-reviewer.js` to customize review criteria.

### Integration with Other Tools

The system can be extended to integrate with:
- Code quality tools (ESLint, SonarQube)
- Security scanners (Snyk, CodeQL)
- Testing frameworks
- Documentation generators

### Multiple AI Providers

The script supports fallback between Anthropic and OpenAI. You can extend it to support additional providers.

## Support

For issues with this setup:

1. Check the troubleshooting section above
2. Review GitHub Actions logs
3. Test API keys independently
4. Create an issue in the repository

## License

This automated PR review system is provided under the MIT License.
