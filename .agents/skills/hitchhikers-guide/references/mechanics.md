# Game Mechanics and Logic

## State Schema
The game state is managed via `scripts/game_manager.py`. The JSON structure includes:
- `location`: String (e.g., "Arthur's Bedroom").
- `inventory`: List of strings.
- `improbability`: Float (0.0 to 1.0).
- `stats`: Dictionary with `sanity`, `hunger`, `health`.
- `flags`: Dictionary of boolean flags.
- `history`: List of recent actions.

## The Improbability Drive (Randomness)
After every turn, roll for a random event based on the `improbability` level.
- High improbability (e.g., > 0.5) leads to surreal events:
    - Turning into a penguin for one turn.
    - Finding a cup of tea in a vacuum.
    - Sudden appearance of a sperm whale and a bowl of petunias.
- Low improbability leads to mundane but annoying events:
    - Stubbing a toe.
    - Forgetting where you put your towel.

## Roguelike Death
When health or sanity hits 0, or a fatal puzzle is failed:
1. Describe the death in a humorous way.
2. "Reconstitute" the player using the Infinite Improbability Drive.
3. Reset `location` to a random "safe" spot (e.g., Heart of Gold, Earth before destruction).
4. Clear half the `inventory` (except the Towel, if owned).
5. Set `improbability` to a high value (0.9) for the next turn.

## Puzzles
Puzzles should be illogical but consistent with the source material.
- **Babelfish Puzzle**: Requires a sequence of items (junk mail, towel, etc.) to catch the fish.
- **Vogon Poetry**: Requires "Sanity" checks. If sanity is low, the player dies of boredom/pain.

## Style Guide
- Use dry, British humor.
- Personify inanimate objects (e.g., the door that enjoys opening).
- Use footnotes or "Guide" interjections for lore.
- Never say "You can't do that." Say "Doing that would be as productive as teaching a Vogon to appreciate modern dance."

## The Number 42
If any calculation, stat, or improbability check ever results in exactly 42, the current location should immediately be transformed into a "High Improbability Zone" regardless of the current stat. The Agent should provide a particularly surreal description involving tea and scrabble tiles.
