# 🎮 Prompt Chain - AI Image Transformation Game

An AI-powered image transformation guessing game (local pass-and-play edition) built for the Replicate Hackathon 2025, powered by Black Forest Labs' Flux API.

## 🧩 Concept Summary

In Prompt Chain, players try to reverse-engineer a prompt that transformed a starting image. Each round, a player sees two images: the original image and an altered version. The player's job is to write a prompt that, when applied to the original image using Black Forest Labs' Flux, recreates the altered version as closely as possible.

Then, the next player sees the same original image and only the image generated from the previous player's prompt, and must guess again. The game continues as a visual game of "telephone," with each player's prompt evolving the image further.

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Black Forest Labs API key (get one at [blackforestlabs.com](https://blackforestlabs.com/))

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd aragondonshack
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure your API key**
   ```bash
   # Copy the example environment file
   cp env_example.txt .env
   
   # Edit .env and add your BFL API key
   BFL_API_KEY=your_actual_bfl_api_key_here
   ```

4. **Test the API connection**
   ```bash
   python main.py --test-api
   ```

5. **Start the game**
   ```bash
   # GUI mode (recommended)
   python main.py
   
   # Command-line mode
   python main.py --cli
   ```

## 🎯 Game Flow

### 1. Initialization (Setup before gameplay)
- AI generates a Primary Image (Image A) using BFL Flux
- AI generates a Prompt (Prompt 1) to alter it
- Using BFL Flux, apply Prompt 1 to Image A → Get Image B
- Save: Image A, Image B, Prompt 1 (hidden from players)

### 2. Player Turn (Repeat each round)
- Player views: The original image (Image A) and the previous altered image
- Player writes a prompt they think could create the second image from the first
- Using BFL Flux, apply the player's prompt to Image A
- Save the result as the new altered image and pass to the next player

### 3. End of Game
- After a set number of rounds, show the full chain
- Display: The original image, all prompts in order, all generated images
- Let players compare how the prompt chain evolved

## 🛠️ Features

### Core Features
- ✅ AI-powered image generation and transformation using BFL Flux
- ✅ Configurable number of rounds (3-10)
- ✅ Timer per turn (2 minutes default)
- ✅ Both GUI and command-line interfaces
- ✅ Automatic file organization and logging
- ✅ Game progress tracking and results display
- ✅ High-resolution image generation (1024x1024)

### GUI Features
- 🎨 Modern dark theme interface
- 🖼️ Side-by-side image comparison
- ⏱️ Real-time countdown timer
- 📊 Progress bar and round tracking
- 💾 File browser for custom primary images
- 📋 Complete results review

### CLI Features
- 🖥️ Full command-line interface
- 📝 Interactive prompt input
- 🔄 Real-time game status updates
- 📊 Detailed results display

## 📁 File Structure

```
project/
├── primary_image/           # Primary game image
├── rounds/                  # Round data
│   ├── round_0/            # AI's initial round
│   │   ├── altered_image.jpg
│   │   └── prompt.txt
│   ├── round_1/            # Player 1
│   │   ├── altered_image.jpg
│   │   └── prompt.txt
│   └── ...
├── output/                  # Game summaries
├── logs/                    # Application logs
├── config.py               # Configuration settings
├── flux_api.py             # BFL Flux API client
├── game_manager.py         # Core game logic
├── gui.py                  # GUI interface
├── main.py                 # Main entry point
└── requirements.txt        # Python dependencies
```

## ⚙️ Configuration

### Environment Variables
- `BFL_API_KEY`: Your Black Forest Labs API key (required)

### Game Settings (config.py)
- `default_rounds`: Number of rounds (default: 6)
- `turn_time_limit`: Time limit per turn in seconds (default: 120)
- `image_size`: Generated image size (default: 1024x1024)
- `min_rounds`/`max_rounds`: Round limits (3-10)

## 🎮 How to Play

### Setup
1. Choose number of rounds (3-10)
2. Optionally select a custom primary image
3. Click "Start New Game"

### During Gameplay
1. **View the images**: You'll see the original image and a target image
2. **Write a prompt**: Think about what prompt could transform the original into the target
3. **Submit**: Enter your prompt and click "Submit Prompt"
4. **Wait**: The AI will generate a new image based on your prompt using BFL Flux
5. **Pass**: Hand the computer to the next player

### End Game
- Review the complete prompt chain
- See how each player's interpretation evolved
- Compare the final result to the original target

## 🔧 Development

### Running Tests
```bash
# Test API connection
python main.py --test-api

# Run with debug logging
python main.py --debug
```

### Project Structure
- `flux_api.py`: Handles all BFL Flux API interactions
- `game_manager.py`: Core game logic and state management
- `gui.py`: Tkinter-based user interface
- `config.py`: Centralized configuration
- `main.py`: Entry point with CLI argument parsing

### Adding Features
The modular design makes it easy to add new features:
- Modify `config.py` for new settings
- Extend `game_manager.py` for new game mechanics
- Update `gui.py` for new UI elements
- Add new API methods in `flux_api.py`

## 🤝 Contributing

This project was created for the Replicate Hackathon 2025 by:
- Jona Nakai
- Laurent Ludwig  
- Rumi Loghmani
- Nathan Wu

## 📄 License

This project is part of the Replicate Hackathon 2025 submission.

## 🆘 Troubleshooting

### Common Issues

**"BFL_API_KEY environment variable is required"**
- Make sure you've created a `.env` file with your API key
- Check that the key is valid at [blackforestlabs.com](https://blackforestlabs.com/)

**"API connection failed"**
- Verify your internet connection
- Check that your API key is correct
- Ensure you have sufficient API credits with Black Forest Labs

**"Image not found"**
- Check that image files exist in the expected directories
- Verify file permissions

**GUI not starting**
- Try running with `--cli` flag for command-line mode
- Check that tkinter is installed: `python -c "import tkinter"`

### Getting Help
- Check the logs in `prompt_chain.log`
- Run with `--debug` flag for detailed output
- Test API connection with `--test-api`

---

**Enjoy playing Prompt Chain! 🎮✨**
