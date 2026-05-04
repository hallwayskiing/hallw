import os
import platform
import re
import shutil
from datetime import datetime
from pathlib import Path
from textwrap import dedent


def get_codebase_desc() -> str:
    """
    Scans AGENTS.md
    """
    agents_file = Path("AGENTS.md")
    if not agents_file.exists():
        return "No codebase description found."

    with open(agents_file, "r", encoding="utf-8") as f:
        return f"<!-- AGENTS.md -->\n{f.read()}"


def get_skills_desc() -> str:
    """
    Scans SKILL.md files from multiple directories and extracts path + YAML frontmatter.
    Directories: .agents/skills
    """
    # Define search directories
    search_dirs = [
        Path(".agents/skills"),
    ]

    skills = []
    yaml_pattern = re.compile(r"\A\s*---\s*\n(.*?)\n---", re.DOTALL)

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


def get_user_profile() -> str:
    """
    Generates the user profile for the automation agent based on the USER.md file.
    """
    user_profile_path = Path("workspace/USER.md")
    if not user_profile_path.exists():
        shutil.copy(Path(__file__).parent / "templates/USER.example.md", user_profile_path)

    with open(user_profile_path, "r", encoding="utf-8") as f:
        return f"<!-- workspace/USER.md -->\n{f.read()}"


def get_memory() -> str:
    """
    Manages daily memory files and returns recent memories (up to 3 recent days).
    """
    now = datetime.now()
    date_str = now.strftime("%Y-%m-%d")
    memory_dir = Path("workspace/memories")
    today_memory_dir = memory_dir / date_str
    today_memory_file = today_memory_dir / "MEMORY.md"

    if not today_memory_file.exists():
        today_memory_dir.mkdir(parents=True, exist_ok=True)
        template_path = Path(__file__).parent / "templates" / "MEMORY.example.md"
        shutil.copy(template_path, today_memory_file)

    recent_memories = []
    subdirs = sorted([d for d in memory_dir.iterdir() if d.is_dir()], key=lambda x: x.name, reverse=True)
    for subdir in subdirs[:3]:
        mem_file = subdir / "MEMORY.md"
        if mem_file.exists():
            with open(mem_file, "r", encoding="utf-8") as f:
                recent_memories.append(f"<!-- workspace/memories/{subdir.name}/MEMORY.md -->\n{f.read()}")

    return "\n\n".join(recent_memories)


def get_system_prompt() -> str:
    """
    Generates the general system prompt for HALLW.
    """
    return dedent(f"""
    <identity>
    You are HALLW, an AI automation agent.
    You are running in a {platform.system()} environment.
    Conversation start time is {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}.
    Current working directory is {os.getcwd()}.
    Through MEMORY.md, you can remember things across conversations. Treat them as your long-term memory.
    </identity>

    <codebase>
    {get_codebase_desc()}
    </codebase>

    <stages>
    - For every user input, you **MUST** call the `build_stages` tool to analyze the task and create stages.
    - If you completed multiple stages at once, pass the number of completed stages to `end_current_stage` tool.
    - If your plan needs adjustment mid-task, call `edit_stages` to replace all remaining stages with a new plan.
    - As an AI Agent, these stages are uninterruptible by user.
    - During stages, you can only receive from user by `request_user_decision` tool.
    - Stage management is internal to you. Don't expose it to the user.
    </stages>

    <exec>
    - Current backend is {"PowerShell" if platform.system() == "Windows" else "shell"}.
    - When listing recursively, always exclude junk files like .git, .venv, node_modules, .DS_Store, etc.
    </exec>

    <file_operations>
    - For file operations, use `read_file` and `write_file` instead of `exec` to get better availability.
    - Don't call `write_file` unless explicitly instructed by the user.
    - When modifying an existing file, prefer `edit_file` instead of rewriting the whole file.
    - If creating a large file, use append mode to write the file in chunks to avoid long processing time.
    - You **MUST** save your work in the `workspace/` directory.
    - You can operate on any files in any path, but carefully consider the impact of your actions.
    </file_operations>

    <available_skills>
    CRITICAL: Whenever a skill is potentially useful, you **MUST** find and read the full content of the SKILL.md file.
    {get_skills_desc()}
    </available_skills>

    <user_profile>
    {get_user_profile()}
    </user_profile>

    <memory>
    Summarize conversations, write down learnings, and list pending items **SILENTLY** and **ACTIVELY**.
    At the start of each conversation, **ALWAYS** present the pending items to the user if there are any.
    {get_memory()}
    </memory>

    <formats>
    - Never return an empty response.
    - Don't invent tool names, only use the provided tools without any prefix.
    - Use markdown style for all your plain responses, for they will be shown in a markdown viewer.
    - Prefer markdown to save files and structure them gracefully for better readability.
    </formats>
    """).strip()
