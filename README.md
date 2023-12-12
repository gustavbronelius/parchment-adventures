# Parchment Adventures

Parchment Adventures is a extremely versatile text-based adventure based on generative AI.

![Parchment Adventures Screenshot](assets/images/Parchment-adventures.png)

# Introduction
## About the game


# Getting Started
## How to install and run
### 1. Download the game
Use [this link](https://github.com/gustavbronelius/parchment-adventures/archive/refs/heads/main.zip) to download the game.

### 2. Extract the game
On a newer version of Windows, you should be able to right-click the folder and press "Extract". If that doesn't work, you can download 7zip or Winrar.

### 3. Python
You need to install Python on your computer to run the game. You can download Python on [this website](https://www.python.org/downloads/).

### 4. Installing and running
After installing Python, you need to navigate to the folder you donwloaded the game to. In that folder, you need to run these two files:

1. Install dependencies (Windows)
2. start (Windows)

### 5. OpenAI API Key
The first time you run the game, you will be asked to enter your OpenAI API key. You can order a API key at https://platform.openai.com/api-keys. You also need to make sure you have some dollar available on the account the API key is connected to. 5 USD will be more than enough.

This key is vital to running the game as without it, no commands can be processed.

## Usage
### How to play
The game is played using the main console window. Write a command and press enter to send it to the narrator. The narrator will continue the story and the game will update your quests, items, etc.

### How to configure
The context of the game is based on a couple of files in the config folder.

- summary.txt
- game_state.txt

#### Summary
The summary states the summary of the history up to the start of the gamne. You can use the summary to easily change the setting of the game. Cowboys in space? Deep ones hiding in Innsmouth? Knights of Ni defending castles?

#### Game state
The game state states the items and quests you start with. Feel free to change this to whatever you'd like. 

### Advanced configurations
- narrator_task_description.txt
- game_state_manager_task_description.txt
- history_manager_task_description.txt

#### Narrator
#### Game State Manager
#### History Manager

## Contact
Join me on [Discord](https://discord.gg/pWU7NNzq) for discussing suggestions, sharing configurations, bugs, and other things.

