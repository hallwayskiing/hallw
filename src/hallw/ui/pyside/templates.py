# --- HTML Templates ---
# User Message
USER_MSG_TEMPLATE = """
<table width="100%" border="0" cellpadding="0" cellspacing="0" style="margin-top: 20px; margin-bottom: 6px;">
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
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18" style="background-color: #131720; border: 1px solid #3b82f6; border-radius: 16px; margin-top: 20px; margin-bottom: 20px;">
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
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18" style="background-color: #131720; border: 1px solid #f59e42; border-radius: 16px; margin-top: 20px; margin-bottom: 20px;">
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
<table width="95%" align="center" border="0" cellspacing="0" cellpadding="18" style="background-color: #131720; border: 1px solid #f54c4c; border-radius: 16px; margin-top: 20px; margin-bottom: 20px;">
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
<div style="color: #666666; font-size: 14px; margin: 20px 0; font-family: monospace; padding-left: 5px;">
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
            <div style="color: #536dfe; font-size: 16px; line-height: 150%;
                        font-weight: bold; text-align: center;">
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
                <pre style="background: #24160c; color: #ffe4c7; padding: 12px; font-size: 16px; border: 1px solid #f97316; white-space: pre-wrap;  word-break: break-word; ">{command}</pre>
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
<div style="max-width: 680px; margin: 60px auto; padding: 0 20px;">
    <div style="text-align: center; margin-bottom: 48px;">
        <div style="font-size: 56px; margin-bottom: 16px; letter-spacing: -1px;">✨</div>
        <h1 style="color: #ffffff; font-size: 32px; font-weight: 600; margin: 0 0 12px 0; letter-spacing: -0.5px;">
            Welcome to HALLW
        </h1>
        <p style="color: #888888; font-size: 15px; margin: 0; font-weight: 400;">
            Heuristic Autonomous Logic Loop Worker
        </p>
    </div>

    <div style="background: linear-gradient(135deg, #111111 0%, #0d0d0d 100%);
                border: 1px solid #222222;
                border-radius: 16px;
                padding: 16px 32px;
                margin-bottom: 32px;
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);">
        <p style="color: #e0e0e0; font-size: 16px; line-height: 1.7; margin-top: 16px;">
            I can browse the web, manage files, and answer your questions.
        </p>
    </div>

    <div style="margin-bottom: 24px;">
        <p style="color: #666666; font-size: 12px; font-weight: 600;
                  text-transform: uppercase; letter-spacing: 1.5px;
                  margin: 0 0 20px 4px;">
            💡 Try Asking me to
        </p>

        <div style="background-color: #0f0f0f;
                    border: 1px solid #1f1f1f;
                    border-radius: 12px;
                    padding: 6px;">
            <div style="padding: 16px 20px; margin-bottom: 2px; border-bottom: 1px solid #1a1a1a;">
                <span style="color: #4a7fc9; font-size: 18px; margin-right: 12px;">📰</span>
                <span style="color: #e8e8e8; font-size: 15px;">
                    Summarize the latest news and save to news.md.
                </span>
            </div>
            <div style="padding: 16px 20px; margin-bottom: 2px; border-bottom: 1px solid #1a1a1a;">
                <span style="color: #4a7fc9; font-size: 18px; margin-right: 12px;">🔍</span>
                <span style="color: #e8e8e8; font-size: 15px;">
                    Read local files and provide a technical report.
                </span>
            </div>
            <div style="padding: 16px 20px; margin-bottom: 2px; border-bottom: 1px solid #1a1a1a;">
                <span style="color: #4a7fc9; font-size: 18px; margin-right: 12px;">🍝</span>
                <span style="color: #e8e8e8; font-size: 15px;">
                    Search for a traditional Lasagna recipe and save it.
                </span>
            </div>
        </div>
    </div>

    <p style="color: #555555; font-size: 13px; text-align: center; margin-top: 40px; font-style: italic;">
        Type your request below to get started
    </p>
</div>
"""
