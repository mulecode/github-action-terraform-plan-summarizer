# github-action-terraform-plan-summarizer

Github plugin for summarizing a terraform plan

## How to use it

```yaml
  terraform_plan_summarizer:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Summarize Terraform Plan
        id: summariseTerraformPlan
        uses: mulecode/github-action-terraform-plan-summarizer@main
        with:
          terraformPlanJson: ./plan.json

      - name: Print summarised plan content
        run: cat "${{ steps.summariseTerraformPlan.outputs.summarisedPlan }}"
```
