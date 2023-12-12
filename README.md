# Parchment Adventures

Parchment Adventures is a extremely versatile text-based adventure based on generative AI.

![Parchment Adventures Screenshot](assets/images/Parchment-adventures.png)

# Introduction
## About the game


# Getting Started
## How to install and run
### 1. Download the game from Github


### 2. Python + libraries
You need to install Python on your computer to run the game. You can download Python using this link: . 

After installing Python, you need to install couple of libraries. Start a commmand prompt (on a windows machine, press win+r and run cmd.), navigate to the game folder and run the command to install the requirements. You should be able to run something like this on your computer

```
cd 
Python -r install requirements.txt
```
### 3. OpenAI API Key
The game is using OpenAI API to run the game. When you start the game for the first time, you will be asked to enter your API key. You can order a API key at https://platform.openai.com/api-keys. 

## Usage
### How to play
The game is played using the main console window. Write a command and press enter to send it to the narrator. The narrator will continue the story and the game will update your quests, items, etc.

### How to configure
The context of the game is based on a couple of files in the config folder.

- game_state.txt
- summary.txt

#### Game state
The game state states the items and quests you start with. Feel free to change this to whatever you'd like.

#### Summary
The summary states the summary of the history up to the start of the gamne. You can use the summary to easily change the setting of the game.

### Advanced configurations
- narrator_task_description.txt
- game_state_manager_task_description.txt
- history_manager_task_description.txt



## Contact
Join me on ![Discord](https://discord.gg/pWU7NNzq) for discussing suggestions, bugs, and other things.

