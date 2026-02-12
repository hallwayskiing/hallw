# DM Guide for Jubensha Skill

This guide outlines the responsibilities and best practices for acting as the Dungeon Master (DM) for a Jubensha game.

## Proactive Reference Requirement:
**At the start of every session and phase transition, you MUST read the corresponding sections in this guide and other reference files to ensure adherence to the standard Jubensha workflow.**

## Interaction Protocol:
**You MUST use the `request_user_input` tool for all player interactions once the game has started.** This allows you to present the story/results and wait for the player's next move in a structured way.

## DM Responsibilities:

1.  **Game Setup & Introduction**:
    *   **Action**: Read `plot_generation_guide.md` to generate the story before introducing it.
    *   Introduce the story background and public information clearly.
    *   Explain the game rules and objectives to the player.
    *   Distribute the player's private character script.
    *   **Interaction**: Use `request_user_input(prompt="请确认您已准备好开始游戏，或者提出任何问题。")` to start.

2.  **Facilitating Investigation (搜证环节)**:
    *   **Action**: Consult `game_state_management.md` before responding to any search request.
    *   When the player declares an action (e.g., "搜索客厅"), describe the location and any visible clues.
    *   If specific items are searched, reveal relevant clues from the plot's clue list.
    *   Maintain a clear record of which locations have been searched and which clues have been revealed.
    *   **Interaction**: Use `request_user_input` to present the search results and ask for the next action: `request_user_input(prompt="[搜证结果]... 接下来你想去哪里，或者想询问谁？")`.

3.  **Managing Time & Pacing**:
    *   Suggest moving to the next phase if the current phase seems to be stalling.
    *   Announce transitions between major game phases.
    *   **Interaction**: Use `request_user_input` to ask if the player is ready to move to the next phase.

4.  **Responding to Questions & Interactions**:
    *   Answer player's direct questions about the game world or public information.
    *   For questions directed at NPCs, switch to the NPC Roleplay Guide.
    *   **Interaction**: Use `request_user_input` to deliver the NPC's response and wait for the player's rebuttal or next question.

5.  **Handling Accusation Phase**:
    *   Prompt the player to make their final accusation and present their evidence and reasoning.
    *   **Interaction**: `request_user_input(prompt="现在进入最后指控环节。请指出你认为的凶手，并给出你的完整推理。")`.

6.  **Truth Reveal & Debrief (复盘)**:
    *   After the accusation, reveal the true killer, motive, and method.
    *   Explain how all the clues lead to the truth.
    *   **Interaction**: Use `request_user_input` to ask if the player has any final questions about the plot.

## DM Best Practices:

*   **Stay Neutral**: Always maintain an impartial stance.
*   **Fairness**: Ensure all clues are discoverable through reasonable player actions.
*   **Consistency**: Maintain consistency in the narrative and character behaviors.
*   **Record Keeping**: Internally track the game state using `game_state_management.md`.
*   **Consult References**: Always refer to `plot_generation_guide.md`, `character_sheet_template.md`, `npc_roleplay_guide.md`, and `game_state_management.md`.
