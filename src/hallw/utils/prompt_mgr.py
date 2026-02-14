import platform
import re
import shutil
from datetime import datetime
from pathlib import Path

from langchain_core.tools import BaseTool


def generateSkillsDesc() -> str:
    """
    Scans SKILL.md files from multiple directories and extracts path + YAML frontmatter.
    Directories: skills/, ~/.agents, ~/.codex, ~/anthropic
    """
    # Define search directories
    home = Path.home()
    search_dirs = [
        Path("skills"),  # Relative to cwd
        home / ".agents",
        home / ".codex",
        home / "anthropic",
    ]

    skills = []
    yaml_pattern = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

    for search_dir in search_dirs:
        if not search_dir.exists():
            continue

        # Find all SKILL.md files recursively
        for skill_file in search_dir.rglob("SKILL.md"):
            try:
                content = skill_file.read_text(encoding="utf-8")
                match = yaml_pattern.match(content)
                if match:
                    yaml_content = match.group(1).strip()
                    skills.append(f"- path: {skill_file} \n {yaml_content}")
            except Exception:
                continue

    return "\n\n".join(skills) if skills else "No skills found."


def generateToolsDesc(tools_dict: dict[str, BaseTool]) -> str:
    """
    Dynamically generates a formatted description string listing all available tools
    and their docstrings based on the tools_dic dictionary.
    """
    descs = []
    for tool_name, tool_obj in tools_dict.items():
        if hasattr(tool_obj, "args") and tool_obj.args:
            args_list = ", ".join(tool_obj.args.keys())
        else:
            args_list = ""
        descs.append(f"- {tool_name}({args_list}): {tool_obj.description}")
    return "\n".join(descs)


def generateUserProfile() -> str:
    """
    Generates the user profile for the automation agent based on the USER.md file.
    """
    if not Path("USER.md").exists():
        shutil.copy("templates/USER.example.md", "USER.md")

    with open("USER.md", "r", encoding="utf-8") as f:
        return f.read()


def generateSystemPrompt(tools_dict: dict[str, BaseTool]) -> str:
    """
    Generates the system prompt for the automation agent based on the task and grid size.

    Args:
        user_task(str): The specific task the agent needs to accomplish.
    """

    return f"""
    <identity>
    You are HALLW, Heuristic Autonomous Logic Loop Worker, an AI automation agent.
    You need to complete user's task by appropriate use of the available tools.
    Your main ability is enabled by `exec` tool, which can execute any command in the terminal.
    You are running in a {platform.system()} environment.
    Today is {datetime.now().strftime("%Y-%m-%d")}.
    </identity>

    <stages>
    - At the beginning of the task, you **MUST** call the `build_stages` tool to analyze the task and create stages.
    - At the end of each stage, you **MUST** call the `end_current_stage` tool to proceed to the next stage,
    or end the task if it is completed. Otherwise you will get stuck in the current stage.
    - If you completed multiple stages at once, pass the number of completed stages to `end_current_stage` tool.
    - If your plan needs adjustment mid-task, call `edit_stages` to replace all remaining stages with a new plan.
    - During stages, you can only receive from user by `request_user_input` tool.
    </stages>

    <exec>
    - Provide direct command to execute. Don't mention backend.
    - For file operations, use **read_file** and **write_file** to get better availability.
    - In PowerShell, don't use `cmd` grammar like `cd` or `dir`. It causes mistakes.
    - Current backend is {"PowerShell" if platform.system()=="Windows" else "sh"}.
    - When listing recursively, always exclude junk files like .git, .venv, node_modules, .DS_Store, etc.
    </exec>

    <available_tools>
    {generateToolsDesc(tools_dict)}
    </available_tools>

    <available_skills>
    {generateSkillsDesc()}
    Whenever a skill is potentially useful, you **MUST** find and read the full content of the SKILL.md file.
    </available_skills>

    <user_profile>
    **User Profile:**
    {generateUserProfile()}
    You need to use this profile to complete tasks that are related to user's personal information.
    If any information is missing, ask the user to provide it.
    If user provides important information, update it in USER.md.
    </user_profile>

    <workspace>
    - You must save your work in the `workspace/` directory.
    - You can edit any files in any path, but carefully consider the impact of your actions.
    </workspace>

    <formats>
    - Never respond emptyly.
    - Don't invent tool names, only use the provided tools without any prefix.
    - Use markdown style for all your plain responses, for they will be shown in a markdown viewer.
    - Prefer markdown to save files and structure them gracefully for better readability.
    </formats>

    <communication_style>
    - You have **TWO** language settings: working language and response language.
    - Your working language is English, you must think and plan in English.
    - Your response language should match the user's input language.
    </communication_style>


    **Now analyze the task, arrange your plan, and take actions.
    """
