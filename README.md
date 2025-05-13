# AI-Based Board Game: Territory Conquest

## Project Overview
This project involves the development of an AI-based board game titled **"Territory Conquest."** The game incorporates multiple power-ups and AI-controlled opponents that utilize the **Minimax algorithm** for decision-making. Players aim to claim tiles on the board using strategic moves while utilizing power-ups to enhance gameplay. The AI can play against human players or another AI.

## Features
- **Minimax AI**: The AI uses the Minimax algorithm with Alpha-Beta pruning for optimal decision-making.
- **Power-ups**: Several power-ups spawn randomly across the board, providing advantages like freezing opponents or gaining double points.
- **Two Game Modes**: Human vs AI and AI vs AI modes.
- **Turn-based Gameplay**: Players take turns to claim tiles on the grid-based board.

## Installation
1. Clone the repository:  
   `git clone https://github.com/yourusername/territory-conquest.git`

2. Navigate to the project directory:  
   `cd territory-conquest`

3. Install the required dependencies:  
   `pip install -r requirements.txt`

## How to Run
1. Navigate to the project folder.
2. Run the game by executing:  
   `python game.py`

## Game Controls
- **Player 1 (Human)**: Arrow keys to move.
- **Player 2 (AI)**: AI moves based on the Minimax algorithm.
- **Power-ups**: Collected by landing on the tiles with power-ups.

## Project Structure
- **game.py**: The main game logic and setup.
- **ai.py**: Contains the Minimax algorithm and AI decision-making functions.
- **board.py**: Defines the game board, tiles, and power-up mechanics.
- **requirements.txt**: List of required Python libraries.

## AI Performance
The AI performed with a win rate of approximately 60% against human players, demonstrating the effectiveness of the Minimax algorithm in making optimal moves. The average decision-making time for the AI was 1.5 seconds, allowing for smooth gameplay without noticeable lag.

## License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments
- **Pygame**: A library used for building the game’s graphical interface.
- **NumPy**: For handling board state and operations.
- The idea and inspiration for this project stem from a desire to explore AI-driven gameplay.
