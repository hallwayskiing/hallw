---
name: email-checker
description: Workflow for checking email. Use when the user needs to check their email.
---

# Email Checker Workflow

## Stages

1. **Check new messages** - Check email for new messages
2. **Analyze new messages** - Analyze new messages for important information
3. **Reply to user** - Reply to user based on the analysis

## Tool Sequence

```
build_stages(stage_names=['Check new messages', 'Analyze new messages', 'Reply to user'])
cat USER.md
request_user_input(prompt="What is the email address you want to check?") # Optional if email address is provided in USER.md
exec(command='echo "{{user_input}}" > USER.md')
exec(commmand='gog gmail search "is:unread label:inbox" --max 10 --account [EMAIL_ADDRESS]')
end_current_stage()

# Filter rules
Ignore emails about new recruitment roles. Ignore emails about job application confirmations.
Focus on emails about job interviews, job offers, and job rejections.
end_current_stage()

Reply to user based on the analysis.
end_current_stage()
```
