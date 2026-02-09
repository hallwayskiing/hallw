# Stage Builder Skill Examples

## Simple Example (1 Stage)

**User Query:** "Help me read the file 'hello.txt' and summarize it."

**Agent Thinking:** The task is straightforward and involves reading a file and summarizing its content. A single stage is sufficient.

**Tool Call:**
```json
{
  "name": "build_stages",
  "arguments": {
    "stage_names": [
      "Read 'hello.txt' and provide a summary"
    ]
  }
}
```

---

## Complex Example (5-6 Stages)

**User Query:** "Create a full-stack website for a personal portfolio including a landing page, an about page, and a contact form. Deploy it to a local folder."

**Agent Thinking:** This is a multi-step task involving design, implementation of multiple components, and deployment. It requires breaking down into discrete logical steps.

**Tool Call:**
```json
{
  "name": "build_stages",
  "arguments": {
    "stage_names": [
      "Analyze portfolio requirements and design the site structure",
      "Implement the landing page with professional styling",
      "Develop the about page with personal information",
      "Create the contact form with validation logic",
      "Perform local deployment and verify site functionality",
      "Finalize the project and document usage instructions"
    ]
  }
}
```
