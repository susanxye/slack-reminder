#!/usr/bin/env node

const fs = require('fs-extra');
const path = require('path');
const Anthropic = require('@anthropic-ai/sdk');
const OpenAI = require('openai');

// Configuration
const CONFIG = {
  anthropicApiKey: process.env.ANTHROPIC_API_KEY,
  openaiApiKey: process.env.OPENAI_API_KEY,
  githubToken: process.env.GITHUB_TOKEN,
  prNumber: process.env.PR_NUMBER,
  prTitle: process.env.PR_TITLE,
  prBody: process.env.PR_BODY,
  prAuthor: process.env.PR_AUTHOR,
  repoOwner: process.env.REPO_OWNER,
  repoName: process.env.REPO_NAME,
  baseRef: process.env.BASE_REF,
  headRef: process.env.HEAD_REF,
};

// Initialize AI clients
let anthropic, openai;

if (CONFIG.anthropicApiKey) {
  anthropic = new Anthropic({
    apiKey: CONFIG.anthropicApiKey,
  });
}

if (CONFIG.openaiApiKey) {
  openai = new OpenAI({
    apiKey: CONFIG.openaiApiKey,
  });
}

async function readFile(filePath) {
  try {
    return await fs.readFile(filePath, 'utf8');
  } catch (error) {
    console.warn(`Could not read file ${filePath}:`, error.message);
    return '';
  }
}

async function getChangedFiles() {
  try {
    const changedFilesContent = await readFile('../changed_files.txt');
    return changedFilesContent.split('\n').filter(line => line.trim());
  } catch (error) {
    console.warn('Could not read changed files:', error.message);
    return [];
  }
}

async function getPRDiff() {
  try {
    return await readFile('../pr_diff.patch');
  } catch (error) {
    console.warn('Could not read PR diff:', error.message);
    return '';
  }
}

function createReviewPrompt(prData, changedFiles, diff) {
  return `You are an expert code reviewer. Please analyze this pull request and provide a comprehensive review.

## Pull Request Information
- **Title**: ${prData.title}
- **Author**: ${prData.author}
- **Description**: ${prData.body || 'No description provided'}
- **Base Branch**: ${prData.baseRef}
- **Head Branch**: ${prData.headRef}

## Changed Files
${changedFiles.length > 0 ? changedFiles.map(file => `- ${file}`).join('\n') : 'No files listed'}

## Code Changes
\`\`\`diff
${diff || 'No diff available'}
\`\`\`

Please provide a detailed review covering:

1. **Code Quality**: Assess the overall code quality, readability, and maintainability
2. **Best Practices**: Check adherence to coding standards and best practices
3. **Potential Issues**: Identify bugs, security vulnerabilities, or performance concerns
4. **Architecture**: Evaluate design decisions and architectural patterns
5. **Testing**: Comment on test coverage and quality
6. **Documentation**: Assess documentation completeness and clarity
7. **Suggestions**: Provide specific improvement recommendations

Format your response as a GitHub comment with:
- Clear sections using markdown headers
- Specific line references where applicable
- Constructive feedback with actionable suggestions
- Overall assessment and recommendation

Start your response with "🤖 **Automated PR Review**" and include appropriate emojis for visual clarity.`;
}

async function generateReviewWithAnthropic(prompt) {
  try {
    const response = await anthropic.messages.create({
      model: 'claude-3-sonnet-20240229',
      max_tokens: 4000,
      messages: [
        {
          role: 'user',
          content: prompt
        }
      ]
    });

    return response.content[0].text;
  } catch (error) {
    console.error('Error with Anthropic API:', error.message);
    throw error;
  }
}

async function generateReviewWithOpenAI(prompt) {
  try {
    const response = await openai.chat.completions.create({
      model: 'gpt-4',
      messages: [
        {
          role: 'system',
          content: 'You are an expert code reviewer. Provide detailed, constructive feedback on pull requests.'
        },
        {
          role: 'user',
          content: prompt
        }
      ],
      max_tokens: 4000,
      temperature: 0.3
    });

    return response.choices[0].message.content;
  } catch (error) {
    console.error('Error with OpenAI API:', error.message);
    throw error;
  }
}

async function generateReview(prompt) {
  // Try Anthropic first, then OpenAI as fallback
  if (anthropic) {
    try {
      console.log('Generating review with Anthropic Claude...');
      return await generateReviewWithAnthropic(prompt);
    } catch (error) {
      console.warn('Anthropic failed, trying OpenAI...');
    }
  }

  if (openai) {
    try {
      console.log('Generating review with OpenAI GPT-4...');
      return await generateReviewWithOpenAI(prompt);
    } catch (error) {
      console.error('OpenAI also failed:', error.message);
      throw error;
    }
  }

  throw new Error('No AI service available. Please configure ANTHROPIC_API_KEY or OPENAI_API_KEY.');
}

function createFallbackReview(prData, changedFiles) {
  return `🤖 **Automated PR Review**

## Summary
This is an automated review for PR #${prData.number} by @${prData.author}.

**Note**: AI review service is currently unavailable. This is a basic structural review.

## Files Changed
${changedFiles.length > 0 ? changedFiles.map(file => `- \`${file}\``).join('\n') : 'No files detected'}

## Basic Checks
- ✅ PR has a title: "${prData.title}"
- ${prData.body ? '✅' : '⚠️'} PR has description
- ✅ Changed ${changedFiles.length} file(s)

## Recommendations
1. **Manual Review Required**: Please ensure this PR is reviewed by team members
2. **Testing**: Verify all tests pass and add new tests if needed
3. **Documentation**: Update documentation if functionality changes
4. **Code Style**: Ensure code follows project conventions

## Next Steps
- [ ] Manual code review by team members
- [ ] Verify CI/CD pipeline passes
- [ ] Test the changes locally
- [ ] Update documentation if needed

---
*This is an automated review. For detailed analysis, please ensure AI services are properly configured.*`;
}

async function main() {
  try {
    console.log('Starting PR review generation...');

    // Validate required environment variables
    if (!CONFIG.prNumber || !CONFIG.prTitle) {
      throw new Error('Missing required PR information');
    }

    // Gather PR data
    const prData = {
      number: CONFIG.prNumber,
      title: CONFIG.prTitle,
      body: CONFIG.prBody,
      author: CONFIG.prAuthor,
      baseRef: CONFIG.baseRef,
      headRef: CONFIG.headRef,
    };

    // Get changed files and diff
    const changedFiles = await getChangedFiles();
    const diff = await getPRDiff();

    console.log(`Analyzing PR #${prData.number}: "${prData.title}"`);
    console.log(`Changed files: ${changedFiles.length}`);
    console.log(`Diff size: ${diff.length} characters`);

    let reviewContent;

    try {
      // Generate AI review
      const prompt = createReviewPrompt(prData, changedFiles, diff);
      reviewContent = await generateReview(prompt);
    } catch (error) {
      console.warn('AI review failed, generating fallback review:', error.message);
      reviewContent = createFallbackReview(prData, changedFiles);
    }

    // Save review to file
    await fs.writeFile('review_output.md', reviewContent);
    console.log('Review saved to review_output.md');

    // Set GitHub Actions output
    console.log('::set-output name=review_content::generated');

  } catch (error) {
    console.error('Error generating PR review:', error.message);
    
    // Create error review
    const errorReview = `🤖 **Automated PR Review - Error**

## Error
Failed to generate automated review: ${error.message}

## Manual Review Required
Please ensure this PR is manually reviewed by team members.

---
*Automated review failed. Please check the GitHub Actions logs for details.*`;

    await fs.writeFile('review_output.md', errorReview);
    process.exit(1);
  }
}

// Run the script
if (require.main === module) {
  main();
}

module.exports = {
  generateReview,
  createReviewPrompt,
  createFallbackReview
};
