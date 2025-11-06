import dotenv from 'dotenv';
const result = dotenv.config()

const getInputName = (name: string) => {
  return `INPUT_${name.replace(/ /g, '_').toUpperCase()}`
}

for (const key in result.parsed) {
  if (Object.prototype.hasOwnProperty.call(result.parsed, key)) {
    const value = result.parsed[key];
    process.env[getInputName(key)] = value;
  }
}

import "dotenv/config";

// Set up test environment variables
process.env.INPUT_SCRIPT = `
core.info("Testing GitHub Python Script!")
core.info(f"Repository: {context.repo['owner']}/{context.repo['repo']}")
core.info(f"Actor: {context.actor}")

# Test return value
__result__ = {"status": "success", "message": "Local test passed!"}
`;

process.env.INPUT_GITHUB_TOKEN = process.env.GITHUB_TOKEN || "";
process.env.INPUT_RESULT_ENCODING = "json";
process.env.GITHUB_REPOSITORY = "austenstone/github-python-script";
process.env.GITHUB_ACTOR = "austenstone";
process.env.GITHUB_EVENT_NAME = "push";
process.env.GITHUB_SHA = "abc123";
process.env.GITHUB_REF = "refs/heads/main";

// Run the action
import("./index.js").catch((error) => {
  console.error(error);
  process.exit(1);
});

process.env.GITHUB_REPOSITORY_OWNER='owner';
process.env.GITHUB_WORKFLOW='My Workflow';
process.env.GITHUB_ACTION='action-name';
process.env.GITHUB_ACTOR='username';
process.env.GITHUB_SHA='1234567890abcdef1234567890abcdef12345678';
process.env.GITHUB_REF='refs/heads/main';
process.env.GITHUB_REF_NAME='main';
process.env.GITHUB_REF_TYPE='branch';
process.env.GITHUB_HEAD_REF='';
process.env.GITHUB_BASE_REF='';
process.env.GITHUB_EVENT_NAME='push';
process.env.GITHUB_RUN_ID=JSON.stringify(15049210062);
process.env.GITHUB_RUN_ATTEMPT=JSON.stringify(1);
process.env.GITHUB_JOB='build';
process.env.GITHUB_RETENTION_DAYS=JSON.stringify(90);

process.env.GITHUB_API_URL='https://api.github.com';
process.env.GITHUB_GRAPHQL_URL='https://api.github.com/graphql';
process.env.GITHUB_SERVER_URL='https://github.com';

(async () => {
  await import('./index');
})();