# --- HTML Templates ---
# User Message
USER_MSG_TEMPLATE = """
<table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top: 20px; margin-bottom: 6px; font-family: Segoe UI, Microsoft YaHei, sans-serif;">
    <tr>
        <td width="60%"></td>
        <td style="background-color: #1a1a1a; border-left: 4px solid #174ea6; color: #ffffff; padding: 16px 20px; font-size: 14px;">
            {text}
        </td>
    </tr>
</table>
"""

# AI Header
AI_HEADER_TEMPLATE = """
<div style="margin-top: 10px; margin-bottom: 5px;">
    <br>
    <br>
    <span style="font-size: 18px;">✨</span>
    <span style="color: #A8C7FA; font-weight: bold; font-size: 14px; margin-left: 6px;">HALLW</span>
    <br>
</div>
"""

# Info Card
INFO_MSG_TEMPLATE = """
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18" style="background-color: #131720; border: 1px solid #3b82f6; border-radius: 16px; margin-top: 20px; margin-bottom: 20px; font-family: Segoe UI, Microsoft YaHei, sans-serif;">
    <tr>
        <td>
            <div style="color: #60a5fa; font-weight: bold; font-size: 14px; margin-bottom: 10px; letter-spacing: 0.5px;">{icon} {title}</div>
            <div style="color: #ffffff; font-size: 16px; line-height: 150%;">{text}</div>
        </td>
    </tr>
</table>
"""

# Warning Card
WARNING_MSG_TEMPLATE = """
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18" style="background-color: #131720; border: 1px solid #f59e42; border-radius: 16px; margin-top: 20px; margin-bottom: 20px; font-family: Segoe UI, Microsoft YaHei, sans-serif;">
    <tr>
        <td>
            <div style="color: #f59e42; font-weight: bold; font-size: 14px; margin-bottom: 10px; letter-spacing: 0.5px;">⚠️ WARNING</div>
            <div style="color: #ffffff; font-size: 16px; line-height: 150%;">{text}</div>
        </td>
    </tr>
</table>
"""

# Error Card
ERROR_MSG_TEMPLATE = """
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18" style="background-color: #131720; border: 1px solid #f54c4c; border-radius: 16px; margin-top: 20px; margin-bottom: 20px; font-family: Segoe UI, Microsoft YaHei, sans-serif;">
    <tr>
        <td>
            <div style="color: #f76969; font-weight: bold; font-size: 14px; margin-bottom: 10px; letter-spacing: 0.5px;">❌ ERROR</div>
            <div style="color: #ffffff; font-size: 16px; line-height: 150%;">{text}</div>
        </td>
    </tr>
</table>
"""

# End Message
END_MSG_TEMPLATE = """
<div style="color: #666666; font-size: 14px; margin: 20px 0; padding-left: 5px; font-family: Segoe UI, Microsoft YaHei, sans-serif;">
    <br>
    <br>
    {icon} {text}
    <br>
</div>
"""

# Stage Message
STAGE_MSG_TEMPLATE = """
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18"
       style="background-color: #131720; border: 1px solid #536dfe; border-radius: 16px;
              margin-top: 20px; margin-bottom: 20px;">
    <tr>
        <td>
            <div style="color: #536dfe; font-weight: bold; font-size: 14px;
                        margin-bottom: 10px; letter-spacing: 0.5px;">
                🚀 {title}
            </div>
            <div style="color: #536dfe; font-size: 16px; line-height: 150%; font-weight: bold; text-align: center; font-family: Segoe UI, Microsoft YaHei, sans-serif;">
                {text}
            </div>
        </td>
    </tr>
</table>
"""

SCRIPT_CONFIRM_TEMPLATE = """
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18"
       style="background-color: #1b1208; border: 1px solid #f97316; border-radius: 16px;
              margin-top: 20px; margin-bottom: 20px;">
    <tr>
        <td>
            <div style="color: #fb923c; font-weight: bold; font-size: 14px; margin-bottom: 12px;">
                🛡️ System Command Request
            </div>
            <div style="color: #ffd8b5; font-size: 14px; line-height: 150%; margin-bottom: 14px;">
                HALLW wants to run the following system command:
            </div>
            <div style="display: flex; justify-content: center; align-items: center; height: 100px;">
                <pre style="background: #24160c; color: #ffe4c7; padding: 12px; font-size: 16px; border: 1px solid #f97316; white-space: pre-wrap;  word-break: break-word; font-family: 'Consolas', 'Microsoft YaHei', monospace;">{command}</pre>
            </div>
            <div style="margin-top: 14px; text-align: center; font-weight: 700; color: #fef3c7;">
                {notice}
            </div>
        </td>
    </tr>
</table>
"""

SCRIPT_CONFIRM_OPTIONS_TEMPLATE = """
<div>
    <a href="{approve_url}" style="color: #30c749; margin-right: 30px; text-decoration: none;">
        ✅ Allow
    </a>
    <a href="{reject_url}" style="color: #cc1f2a; margin-left: 30px; text-decoration: none;">
        ❌ Reject
    </a>
</div>
"""

SCRIPT_CONFIRM_STATUS_TEMPLATE = """
<div style="color: #83857f; font-style: italic;">
    {text}
</div>
"""

# Welcome Page
WELCOME_HTML = """
<div style="
    max-width: 900px;
    margin: 40px auto 32px;
    padding: 0 24px;
    color: #e5e7eb;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Microsoft YaHei', sans-serif;
">

    <!-- Top bar: product + status badges -->
    <div style="
        display: table;
        width: 100%;
        margin-bottom: 32px;
    ">
        <div style="display: table-cell; vertical-align: middle;">
            <span style="
                font-size: 13px;
                text-transform: uppercase;
                letter-spacing: 2px;
                color: #6b7280;
            ">
                HALLW • Autonomous Workspace
            </span>
        </div>
    </div>

    <!-- Main hero section -->
    <div style="text-align: left; margin-bottom: 40px;">
        <div style="font-size: 36px; margin-bottom: 12px;">
            <span style="margin-right: 10px;">✨</span>
            <span style="font-weight: 600; letter-spacing: -1px;">HALLW - Your AI Assistant</span>
        </div>

        <p style="
            margin: 6px 0 0 2px;
            font-size: 16px;
            color: #9ca3af;
            max-width: 640px;
            line-height: 1.7;
        ">
            Orchestrate web automation, file operations, and system commands. <br>
            Think in natural language — HALLW turns it into deterministic workflows.
        </p>
    </div>

    <table width="100%" cellspacing="0" cellpadding="0" style="margin-bottom: 32px;">
        <tr>
            <!-- Capabilities -->
            <td style="width: 33%; padding-right: 10px; vertical-align: top;">
                <div style="
                    background-color: #050712;
                    border: 1px solid #111827;
                    padding: 16px 16px 14px 16px;
                ">
                    <div style="font-size: 20px; margin-bottom: 8px;">🧠 Core Skills</div>
                    <div style="font-size: 14px; color: #9ca3af; line-height: 1.6; margin-bottom: 10px;">
                        • Browse and extract information<br>
                        • Analyze and transform documents<br>
                        • Generate code, scripts, and reports
                    </div>
                </div>
            </td>

            <!-- Automation -->
            <td style="width: 33%; padding: 0 5px; vertical-align: top;">
                <div style="
                    background-color: #050712;
                    border: 1px solid #111827;
                    padding: 16px 16px 14px 16px;
                ">
                    <div style="font-size: 20px; margin-bottom: 8px;">⚙️ Automation</div>
                    <div style="font-size: 14px; color: #9ca3af; line-height: 1.6; margin-bottom: 10px;">
                        • Run multi-stage workflows<br>
                        • Think with reflection<br>
                        • Keep a structured task history
                    </div>
                </div>
            </td>

            <!-- Environment -->
            <td style="width: 33%; padding-left: 10px; vertical-align: top;">
                <div style="
                    background-color: #050712;
                    border: 1px solid #111827;
                    padding: 16px 16px 14px 16px;
                ">
                    <div style="font-size: 20px; margin-bottom: 8px;">🖥️ Environment</div>
                    <div style="font-size: 14px; color: #9ca3af; line-height: 1.6; margin-bottom: 10px;">
                        • Local-first desktop agent<br>
                        • Transparent tool usage<br>
                        • Human-in-the-loop approvals
                    </div>
                </div>
            </td>
        </tr>
    </table>

    <!-- Quick actions section -->
    <div style="margin-bottom: 24px;">
        <div style="
            font-size: 16px;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 1.6px;
            color: #6b7280;
            margin: 0 0 12px 4px;
        ">
            Quick start
        </div>

        <div style="
            background-color: #121005;
            border: 1px solid #111827;
            padding: 6px;
        ">
            <div style="color: #e5e7eb; font-size: 16px;">
                📰 Summarize today's tech headlines and save as tech_news.md.
            </div>
            <div style="color: #e5e7eb; font-size: 16px; margin-top: 8px;">
                🍜 Learn how to cook a Chinese dish and create recipe.md.
            </div>
            <div style="color: #e5e7eb; font-size: 16px; margin-top: 8px;">
                🛫 Find and tell me ten interesting places to visit in Paris.
            </div>
            <div style="color: #e5e7eb; font-size: 16px; margin-top: 8px;">
                👗 Browse Lululemon's latest collection.
            </div>
            <div style="color: #e5e7eb; font-size: 16px; margin-top: 8px;">
                🌤️ Gather the next ten days' weather forecast.
            </div>
        </div>
    </div>
</div>
"""
