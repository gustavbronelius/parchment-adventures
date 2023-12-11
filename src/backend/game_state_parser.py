# File: game_state_parser.py

import os

def parse_game_state():
    game_state_dir = '../data'
    game_state_files = [f for f in os.listdir(game_state_dir) if f.startswith('game_state_')]
    if not game_state_files:
        game_state_file_path = os.path.join('../config', 'game_state.txt')
    else:
        latest_game_state_file = max(game_state_files, key=lambda f: os.path.getmtime(os.path.join(game_state_dir, f)))
        game_state_file_path = os.path.join(game_state_dir, latest_game_state_file)

    with open(game_state_file_path, 'r') as file:
        content = file.read()

    try:
        split_content = content.split('\n## Quests\n', 1)
        items_section = split_content[0]

        if len(split_content) > 1:
            quests_section = '## Quests\n' + split_content[1]
        else:
            raise IndexError("Quests section not found in game state file.")

    except IndexError as e:
        print(f"Game state parser - Warning: {e}. All content will be treated as items.")
        items_section = content  # Assign all content to items_section
        quests_section = ""      # Leave quests_section empty

    return items_section, quests_section

# Usage:
items_section, quests_section = parse_game_state()

