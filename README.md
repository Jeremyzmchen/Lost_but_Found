# Lost But Found - Game Dev

<img width="2400" height="1350" alt="image" src="https://github.com/user-attachments/assets/e8956c29-038f-4035-a7bc-3bde6bd8e4e7" />



**Lost But Found** is a 2D interactive game developed using Python and the Pygame framework. The game challenges players to manage items, interact with various NPCs, and navigate through a dynamic environment while dealing with game elements like the police and thieves.



<img width="2371" height="1340" alt="image" src="https://github.com/user-attachments/assets/38aa51ca-4f67-4e89-8534-942b9b174931" />

<img width="2356" height="1340" alt="image" src="https://github.com/user-attachments/assets/7d38f6f2-3b33-4485-a050-a97c55fb7950" />

<img width="2371" height="1340" alt="image" src="https://github.com/user-attachments/assets/60fe5167-f1d5-4bbb-91ab-310a067974eb" />

<img width="2364" height="1340" alt="image" src="https://github.com/user-attachments/assets/84f057c3-85fa-4115-b9f6-3b3863e278d2" />

<img width="2380" height="1340" alt="image" src="https://github.com/user-attachments/assets/36dce22a-2c18-4a80-a60b-f67f5cffdc86" />


## Inspiration & References
***This project was inspired by a famous game Lost but Found on Steam.*** While adopting the premise of returning lost items to their rightful owners, this version introduces complex character interactions and a robust backend architecture designed for academic rigor.


## Gameplay Features

***Entity System:***   Includes diverse characters such as customers, police officers, and thieves, each with unique behaviors.


***Item Management:***   A system to handle various in-game items and inventory mechanics.


***State Machine:***   Robust game state management including Menu, Gameplay, and GameOver states.


***UI & HUD:***   Interactive buttons, popups, and a Head-Up Display (HUD) for a seamless user experience.


***Multimedia Integration:***   Supports custom fonts, background music (BGM), and sound effects (SFX).

<img width="2400" height="1350" alt="image" src="https://github.com/user-attachments/assets/05c6b80c-5544-4697-960b-22305bc7bea5" />


## Tech Stack

***Language:*** Python 


***Library:*** Pygame 


***Design Patterns:*** State Pattern for game flow, Manager classes for system handling.

## Repository Structure
```Plaintext

.
├── assets/             # Game assets (images, sounds, fonts) [cite: 106, 108, 110]
├── config/             # Global settings and configurations [cite: 133]
├── game/
│   ├── entities/       # Character and item classes (Police, Thief, Customer, etc.) [cite: 134, 135, 136, 137, 138, 139]
│   ├── managers/       # Inventory and game logic managers [cite: 140, 141]
│   ├── states/         # Game state definitions (Menu, Gameplay, Game Over) 
│   └── ui/             # UI components (Buttons, HUD, Popups) 
├── test/               # Unit tests for gameplay logic [cite: 153]
└── start.py            # Main entry point to launch the game [cite: 152]
```

## How to Run
Prerequisites: Ensure you have Python installed.

Install Dependencies:

```bash
pip install pygame
```

Launch Game:

```Bash
python start.py
```
