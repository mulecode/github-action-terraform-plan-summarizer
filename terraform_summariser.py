"""
Module to summarize the terraform plan output
"""
import json
import os
import time


def parse_terraform_plan_json(plan_json: dict) -> tuple:
    added_resources = []
    updated_resources = []
    destroyed_resources = []
    replaced_resources = []

    for resource in plan_json.get('resource_changes', []):
        action = resource['change']['actions']
        resource_id = resource['address']

        if action == ['create']:
            added_resources.append(resource_id)
        elif action == ['update']:
            updated_resources.append(resource_id)
        elif action == ['delete']:
            destroyed_resources.append(resource_id)
        elif action == ['delete', 'create']:
            replaced_resources.append(resource_id)

    return added_resources, updated_resources, destroyed_resources, replaced_resources


def summarize_plan_json(plan_json: dict) -> str:
    added, updated, destroyed, replaced = parse_terraform_plan_json(plan_json)

    summary = []

    if added:
        summary.append(f"❇️ **Resources to be added ({len(added)}):**")
        summary.extend(f"  - _{resource}_" for resource in added)
        summary.append("")

    if updated:
        summary.append(f"🔆️ **Resources to be updated in place ({len(updated)}):**")
        summary.extend(f"  - _{resource}_" for resource in updated)
        summary.append("")

    if replaced:
        summary.append(f"🌀 **Resources to be replaced (destroyed and recreated) ({len(replaced)}):**")
        summary.extend(f"  - _{resource}_" for resource in replaced)
        summary.append("")

    if destroyed:
        summary.append(f"💢️ **Resources to be destroyed ({len(destroyed)}):**")
        summary.extend(f"  - _{resource}_" for resource in destroyed)
        summary.append("")

    # Handle case where no actions are detected
    if not (added or updated or destroyed or replaced):
        return "💠 **No changes detected in the Terraform plan.**"

    summary.append(
        f"> Summary: {len(added)} to add, {len(updated)} to update, {len(replaced)} to replace, {len(destroyed)} to destroy.")

    return "\n".join(summary)


def set_action_outputs(output_pairs):
    """Sets the GitHub Action outputs.

    Keyword arguments:
    output_pairs - Dictionary of outputs with values
    """
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as f:
            for key, value in output_pairs.items():
                print("{0}={1}".format(key, value), file=f)


def write_summary_to_file(summary, filename):
    """
    Write the summary to a file
    :param summary:
    :param filename:
    :return:
    """
    with open(filename, "w") as file:
        file.write(summary)


def get_file_name() -> str:
    """
    Get the file name
    :return:
    """
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    return f"summary_{timestamp}.txt"


def main(plan_json_file_path):
    # Check if variable is set
    if not plan_json_file_path:
        print("Error: TERRAFORM_PLAN_JSON environment variable is not set")
        return
    # Check if the file exists
    if not os.path.exists(plan_json_file_path):
        print(f"Error: File {plan_json_file_path} does not exist")
        return
    # Read the plan file
    with open(plan_json_file_path, 'r') as file_content:
        plan_dict = json.load(file_content)
    # Summarize the plan
    summary = summarize_plan_json(plan_dict)
    # Write the summary to a file
    file_name = get_file_name()
    write_summary_to_file(summary, file_name)
    # Set the output
    set_action_outputs({
        "summarisedPlan": file_name
    })


if __name__ == "__main__":
    plan_json_file_path = os.getenv('TERRAFORM_PLAN_JSON')
    main(plan_json_file_path)
