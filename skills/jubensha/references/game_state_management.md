# Game State Management Guide for Jubensha Skill

This guide outlines the protocols for tracking and managing the game state during a Jubensha session to ensure logical consistency and a smooth player experience.

## Key Game State Components to Track:

1.  **Current Game Phase**:
    *   `Setup`: Initializing game, plot generation, character selection.
    *   `Introduction`: DM setting the scene, rules explanation.
    *   `Investigation`: Players searching locations, gathering clues.
    *   `Discussion/Interrogation`: Players interacting with NPCs, forming theories.
    *   `Accusation`: Player making final accusation.
    *   `Reveal`: DM explaining the truth, debriefing.

2.  **Revealed Public Clues**:
    *   Maintain a list of all clues that have been discovered and are now public knowledge.
    *   Ensure newly revealed clues are added to this list.
    *   Avoid re-revealing the same clue unless explicitly requested and contextually appropriate.

3.  **Location Search Status**:
    *   Track which locations (e.g., "客厅", "书房", "卧室") have been searched by the player.
    *   For each location, note what was found and if it has been thoroughly searched (to prevent infinite searching).

4.  **NPC Interaction Log**:
    *   Record key questions asked to each NPC and their responses.
    *   Note if an NPC lied, deflected, or provided critical information.
    *   This helps maintain NPC consistency (refer to `npc_roleplay_guide.md`).

5.  **Player Inventory (if applicable)**:
    *   If the game involves players picking up physical items, maintain a list of items the player currently possesses.

6.  **Player Hypotheses/Deductions**:
    *   Keep track of the player's developing theories and whom they suspect.
    *   This helps in guiding the DM's responses and anticipating player actions.

7.  **Private Character Information Status**:
    *   For each NPC, track if their private secrets or motives have been revealed (and under what circumstances).
    *   This is crucial for maintaining the mystery and ensuring secrets are guarded appropriately.

8.  **The Truth (Internal Only)**:
    *   The pre-generated killer, motive, method, and alibi breakdown. This information is *never* revealed until the `Reveal` phase.
    *   All DM actions and NPC responses must be consistent with this hidden truth without directly exposing it.

## Management Protocols:

*   **Initialization**: At the start of a new game, reset all game state components to their initial (empty or pre-defined) values.
*   **Updates**: After every player action or DM response that alters the game state (e.g., clue found, location searched, NPC interrogated), update the relevant components.
*   **Cross-Referencing**: When making decisions or generating responses, always cross-reference the current game state to ensure accuracy and consistency.
    *   Example: Before revealing a clue, check if it has already been revealed. Before an NPC responds, check their last interaction log.
*   **Completeness**: Strive for a complete and accurate record of the game's progression to ensure a satisfying and logical conclusion.
*   **Difficulty Scaling (Optional)**: In a high-difficulty game, some clues might be more obscure or require combining multiple pieces of information. Ensure the `Revealed Public Clues` accurately reflect the subtlety.
