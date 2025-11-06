import * as core from "@actions/core";
import * as exec from "@actions/exec";
import * as path from "path";
import * as fs from "fs";

async function run(): Promise<void> {
  try {
    // Get inputs
    const script = core.getInput("script", { required: true });
    const token = core.getInput("github-token", { required: true });
    const resultEncoding = core.getInput("result-encoding") || "json";
    const retries = core.getInput("retries") || "0";
    const retryExemptStatusCodes = core.getInput("retry-exempt-status-codes") || "400,401,403,404,422";
    const baseUrl = core.getInput("base-url") || "";

    // Setup Python
    core.info("Setting up Python...");
    await exec.exec("python", ["--version"]);

    // Install required Python packages
    core.info("Installing Python dependencies...");
    const requirementsPath = path.join(__dirname, "../python/requirements.txt");
    if (fs.existsSync(requirementsPath)) {
      await exec.exec("pip", ["install", "-r", requirementsPath]);
    } else {
      await exec.exec("pip", ["install", "PyGithub", "requests"]);
    }

    // Create a temporary Python script file
    const scriptPath = path.join(process.cwd(), "temp_script.py");
    const wrapperPath = path.join(__dirname, "../python/github_script.py");
    
    // Build the Python runner script
    const runnerScript = `
import sys
import os
import json

# Set environment variables for the script
os.environ["INPUT_GITHUB_TOKEN"] = """${token.replace(/"/g, '\\"')}"""
os.environ["INPUT_RETRIES"] = "${retries}"
os.environ["INPUT_RETRY_EXEMPT_STATUS_CODES"] = "${retryExemptStatusCodes}"
${baseUrl ? `os.environ["INPUT_BASE_URL"] = "${baseUrl}"` : ""}

# Import the wrapper
sys.path.insert(0, "${path.dirname(wrapperPath).replace(/\\/g, "\\\\")}")
from github_script import GitHubWrapper, Context, Core, run_script

# Initialize context
token = os.getenv("INPUT_GITHUB_TOKEN", "")
retries_val = int(os.getenv("INPUT_RETRIES", "0"))
retry_codes = [int(x.strip()) for x in os.getenv("INPUT_RETRY_EXEMPT_STATUS_CODES", "400,401,403,404,422").split(",")]
base_url = os.getenv("INPUT_BASE_URL") or None

github = GitHubWrapper(token, base_url, retries_val, retry_codes)
context = Context()
core = Core()

# User script
user_script = """${script.replace(/"/g, '\\"').replace(/\n/g, "\\n")}"""

# Execute user script
exec_globals = {
    'github': github,
    'context': context,
    'core': core,
    'os': os,
    'sys': sys,
    'json': json,
}

try:
    exec(user_script, exec_globals)
    result = exec_globals.get('__result__')
    
    # Output the result
    if result is not None:
        if "${resultEncoding}" == "json":
            print("::set-output name=result::" + json.dumps(result))
        else:
            print("::set-output name=result::" + str(result))
except Exception as e:
    core.set_failed(str(e))
    sys.exit(1)
`;

    fs.writeFileSync(scriptPath, runnerScript);

    // Execute the Python script
    core.info("Executing Python script...");
    let output = "";
    let errorOutput = "";

    const options = {
      listeners: {
        stdout: (data: Buffer) => {
          output += data.toString();
        },
        stderr: (data: Buffer) => {
          errorOutput += data.toString();
        },
      },
    };

    const exitCode = await exec.exec("python", [scriptPath], options);

    // Clean up temporary script
    if (fs.existsSync(scriptPath)) {
      fs.unlinkSync(scriptPath);
    }

    if (exitCode !== 0) {
      core.setFailed(`Python script failed with exit code ${exitCode}\n${errorOutput}`);
      return;
    }

    // Parse output for result
    const resultMatch = output.match(/::set-output name=result::(.+)/);
    if (resultMatch) {
      const result = resultMatch[1];
      core.setOutput("result", result);
    }

    core.info("Script execution completed successfully");
  } catch (error) {
    if (error instanceof Error) {
      core.setFailed(error.message);
    }
  }
}

run();
