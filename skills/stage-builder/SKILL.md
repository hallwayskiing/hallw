---
name: stage-builder-skill
description: Guide for correctly calling the `build_stages` tool. Use this skill when an AI agent needs to plan its workflow by breaking down a user's request into actionable stages. This skill provides patterns for both simple tasks (1 stage) and complex tasks (5-6 stages).
---

# Stage Builder Skill

This skill guides the agent on how to use the `build_stages` tool effectively. Planning is a critical first step for any non-trivial task.

## Guidelines for `build_stages`

1. **Call Exactly Once**: The `build_stages` tool MUST be called at the beginning of the task.
2. **Actionable Stages**: Each stage name should be a clear, actionable instruction.
3. **Correct Granularity**:
   - For simple tasks, use 1 stage.
   - For complex tasks, use 5-6 stages to provide a clear roadmap without over-fragmenting the work.
4. **Logical Order**: Stages must follow a logical chronological order.

## Usage Patterns

### Simple Tasks (1 Stage)
Use a single stage for tasks that can be completed in a few tool calls or represent a single logical action.

**Example Triggers:**
- "Read this file."
- "What is the capital of France?"
- "Summarize this snippet."

### Complex Tasks (5-6 Stages)
Use multiple stages for tasks involving research, creation, testing, and refinement.

**Example Triggers:**
- "Build a new skill from scratch."
- "Develop a web application."
- "Conduct a deep research report on a specific topic."

## Reference Examples
For detailed examples of tool calls for both simple and complex scenarios, refer to [references/examples.md](references/examples.md).

## Workflow Integration
- **Step 1**: Analyze the user's request.
- **Step 2**: Determine the complexity and necessary steps.
- **Step 3**: Call `build_stages` with appropriate stage names.
- **Step 4**: Proceed to execute each stage, calling `end_current_stage` after each completion.
