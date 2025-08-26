# Aethelgard: The Guild's Path - A Discord Adventure RPG (Alpha)

Welcome to Aethelgard, a fully-featured, text-based RPG bot for Discord! This project is a complex, multi-system adventure game built with Python, featuring persistent player data, a dynamic combat system, quests, crafting, and much more.

---
## ⚠️ Project Status: In Development (Alpha Stage)

This is an active, in-development project. The core systems are functional, and the initial tutorial and starting area (Oakhaven Outpost) are complete. This currently represents about **15-20%** of the planned features based on my full story outline. My immediate focus is on building out the main questline and expanding the world with new towns and points of interest.

---
## ✨ Key Features

### Implemented & Functional:
-   **Persistent Player Data:** Player progress, pets, and inventory are saved permanently using an SQLite database.
-   **Modular Cog Architecture:** The bot is organized into a professional "cog" structure, separating concerns for clean and maintainable code.
-   **Dynamic UI Kit:** The game uses `discord.py`'s modern UI kit (Views, Buttons, Modals) for an interactive experience.
-   **Turn-Based Combat System:** Engage in strategic turn-based battles against wild pets.
-   **In-Depth Pet System:** Collect and level up starter pets with unique stats and skills.
-   **Quest & Inventory System:** A scalable quest engine is in place, and players can manage items in a categorized inventory.
-   **Tutorial & Starting Zone:** The complete new player experience, from character creation to the first quests in the Oakhaven Outpost area, is implemented.

### Planned Features (In-Progress):
-   **Expanded World:** Adding ~12 unique towns and multiple points of interest based on a complete story outline.
-   **Main Story Questline:** Developing the central narrative for the middle and end game.
-   **Crafting & Guild Systems:** Implementing item crafting and guild-based mechanics.
-   **Advanced Combat:** Adding more skills, passive abilities, and pet evolutions.

---
## 🛠️ Technical Showcase

This project demonstrates a strong understanding of modern bot development and core programming principles:

-   **Language:** Python 3
-   **Core Libraries:** `discord.py`, `sqlite3`, `asyncio`, `python-dotenv`, `easy_pil`
-   **Key Concepts:**
    -   **Object-Oriented Programming (OOP):** The project is built with classes for players, pets, items, and game systems.
    -   **AI-Assisted Development:** Leveraged AI tools as a development partner for brainstorming, code generation, refactoring, and debugging, demonstrating a modern and efficient workflow.
    -   **Database Management:** Full SQL schema design and execution for creating and managing related tables.
    -   **Asynchronous Programming:** All Discord events and long-running tasks are handled asynchronously to ensure the bot remains responsive.
    -   **Secure Credential Handling:** The bot token and other secrets are kept out of the codebase using environment variables.

---
## 🚀 Setup & Installation

To run this bot yourself, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/YourUsername/discord-adventure-bot.git](https://github.com/YourUsername/discord-adventure-bot.git)
    cd discord-adventure-bot
    ```
    *(Replace `YourUsername` with your actual GitHub username)*

2.  **Create a virtual environment and install dependencies:**
    ```bash
    # Create the environment
    python -m venv venv
    # Activate it (Windows)
    .\venv\Scripts\activate
    # Install required libraries
    pip install -r requirements.txt
    ```

3.  **Set up your environment variables:**
    -   Create a new file named `.env` in the main project folder.
    -   Copy the contents of `.env.example` into it and fill in your actual bot token and server ID.

4.  **Run the bot:**
    ```bash
    python main.py
    ```