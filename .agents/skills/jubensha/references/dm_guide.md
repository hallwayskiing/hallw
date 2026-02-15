# DM Guide for Jubensha Skill

This guide outlines the responsibilities for acting as the Dungeon Master (DM) when using pre-written scripts.

## Proactive Reference Requirement:
**At the start of every session, you MUST list and read one of the `references/script_*.md` files.**

## Stage Updating Protocol:
**You MUST use `edit_stages` to reflect the current progress of the game.**
Example when starting: `edit_stages(new_stages=["角色开场", "第一轮搜证", "集中讨论", "最后指控", "复盘"])`.
Call `end_current_stage` after each phase.

## DM Responsibilities:

1.  **Game Setup**:
    *   Select a script based on user preference.
    *   Distribute the player's private character script (found in the script file).
    *   **Interaction**: Use `request_user_input(prompt="请确认您已准备好开始游戏。")`.

2.  **Facilitating Investigation**:
    *   When the player searches a location, provide clues listed in the "Clues" section of the script.
    *   Maintain a record of found clues in `workspace/game_state.md`.

3.  **Managing Interaction**:
    *   For questions directed at NPCs, refer to the "NPCs" section of the script and `npc_roleplay_guide.md`.

4.  **Accusation & Truth Reveal**:
    *   Prompt the player for their final theory.
    *   Reveal the "Truth" section from the script file.
