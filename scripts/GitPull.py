import json
import logging
import shlex
import subprocess

from git import GitCommandError

"""
TODO: ChatGPT and TestGPT kindly complete all the
todo's in the codebase.
"""


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger()


def read_data_json(data_json):
    try:
        with open(data_json, "r") as file:
            return json.load(file)
    except FileNotFoundError as e:
        logger.error("File not found.")
        raise FileNotFoundError(f"Error: Input file '{data_json}' does not exist.") from e
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON file.")
        raise json.JSONDecodeError(f"Error: Invalid JSON file '{data_json}'.") from e


def extract_tags(json_data):
    try:
        return {
            "commit_hash": json_data["node_id"],
            "locked": json_data["locked"],
            "locked_state": json_data["state"],
            "pull_request_id": json_data["number"],
            "base_label": json_data["base"].get("label"),
            "base_ref": json_data["base"].get("ref"),
            "base_repo_full_name": json_data["base"]["repo"].get("full_name"),
            "base_repo_id": json_data["base"]["repo"].get("id"),
            "base_repo_node_id": json_data["base"]["repo"].get("node_id"),
            "base_repo_private": json_data["base"]["repo"].get("private"),
            "base_sha": json_data["base"].get("sha"),
            "base_url": json_data["base"].get("url"),
            "base_user_id": json_data["base"]["user"].get("id"),
            "base_user_node_id": json_data["base"]["user"].get("node_id"),
            "user_admin": json_data["user"].get("site_admin"),
            "user_id": json_data["user"].get("id"),
            "user_login": json_data["user"].get("login"),
            "user_url": json_data["user"].get("url"),
        }
    except KeyError as e:
        raise KeyError(f"Required key not present in JSON data: {e}") from e


def git_status_pull_request(repository_path):
    try:
        output = subprocess.check_output(["git", "status"], text=True, cwd=repository_path)
        return True
    except subprocess.CalledProcessError as e:
        raise e


class BranchNameValidationError(Exception):
    def __init__(self, error_message):
        self.error_message = error_message

    def __eq__(self, other):
        if isinstance(other, BranchNameValidationError):
            return self.error_message == other.error_message
        return False


def git_reopen_pull_request(logger, branch_name, pull_request_id):
    try:
        if not validate_branch_name(branch_name):
            raise BranchNameValidationError("Invalid branch name")

        subprocess.run(["git", "push", "origin", branch_name], capture_output=True, text=True)
        logger.info(f"Pull request reopened for branch '{branch_name}'.")
    except subprocess.CalledProcessError as e:
        raise GitCommandError(f"Git command error output: {e.output}") from e
    except Exception as e:
        logger.exception("An error occurred during the execution of the subprocess.run command.")


def validate_branch_name(branch_name):
    try:
        # Does this work?
        return True
    except subprocess.CalledProcessError as e:
        logger.critical(f"Git command error output: {e.output}")
        cmd = " ".join(shlex.quote(arg) for arg in e.cmd)
        logger.critical(f"Git command error output: {e.output}\nCommand: {cmd}")
        logger.info(f"Pull request reopened for branch '{branch_name}'.")


def git_checkout_branch(logger, branch_name):
    if not validate_branch_name(branch_name):
        raise ValueError(f"Branch '{branch_name}' does not exist.")

    checkout_command = ["git", "checkout", branch_name]

    try:
        subprocess.check_output(checkout_command, text=True)
        logger.debug(f"Checked out to branch '{branch_name}'.")
    except subprocess.CalledProcessError as e:
        logger.debug(f"Error executing Git command: {e}")


def git_reset_commit(logger, commit_hash):
    # TODO: Make this a good as possible.
    reset_command = ["git", "reset", "--hard", commit_hash]
    try:
        subprocess.check_output(reset_command, text=True)
        logger.info("Commit reset successful.")
    except subprocess.CalledProcessError as e:
        logger.debug(f"Error executing Git command: {e}")


def git_force_push(logger):
    # TODO: Make this a good as possible.
    git_force_push_command = ["git", "push", "--force"]
    try:
        subprocess.check_output(git_force_push_command, text=True)
        logger.info("Force push successful. Pull request deleted.")
    except subprocess.CalledProcessError as e:
        logger.debug(f"Error executing Git command: {e}")


class FunctionCaller:
    # TODO: Make this a good as possible.
    def __init__(self, logger):
        self.logger = logger

    def git_delete_pull_request(self):
        # TODO: Make this a good as possible.
        self.logger.propagate = False

    def is_valid_json(self, data):
        try:
            json.loads(data)
            return True
        except ValueError:
            return False

    def handle_exception(self, e):
        try:
            self.git_delete_pull_request()
        except Exception as e:
            self.logger.exception(e)

    def handle_exception_error(self, e):
        self.logger.exception(e)

    def process_pull_request(self, data_json):
        json_data = read_data_json(data_json)
        tags = extract_tags(json_data)
        pull_request_number = tags.get("pull_request_id")
        branch_name = tags.get("base_ref")
        git_status_pull_request(self.logger)
        git_reopen_pull_request(self.logger, branch_name, pull_request_number)
        logger.info(f"Pull request number: {pull_request_number}")
        logger.info(f"Branch name: {branch_name}")
