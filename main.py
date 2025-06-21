#!/usr/bin/env python3
"""
Prompt Chain - AI Image Transformation Game
A local pass-and-play game where players guess prompts to recreate AI-transformed images.

Usage:
    python main.py                    # Start GUI
    python main.py --cli              # Start command-line interface
    python main.py --test-api         # Test BFL Flux API connection
    python main.py --help             # Show help
"""

import argparse
import sys
import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('prompt_chain.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

def test_api_connection():
    """Test the BFL Flux API connection"""
    try:
        from flux_api import FluxAPI
        api = FluxAPI()
        
        if api.test_connection():
            print("✅ BFL Flux API connection successful!")
            return True
        else:
            print("❌ BFL Flux API connection failed!")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API connection: {e}")
        return False

def run_cli_game():
    """Run the game in command-line interface mode"""
    try:
        from game_manager import GameManager
        
        print("🎮 Welcome to Prompt Chain (CLI Mode)!")
        print("=" * 50)
        
        # Get game settings
        while True:
            try:
                rounds = int(input(f"Number of rounds (3-10, default {GAME_CONFIG['default_rounds']}): ") or GAME_CONFIG['default_rounds'])
                if 3 <= rounds <= 10:
                    break
                print("Please enter a number between 3 and 10.")
            except ValueError:
                print("Please enter a valid number.")
        
        use_custom_image = input("Use custom primary image? (y/n, default n): ").lower().startswith('y')
        primary_image_path = None
        
        if use_custom_image:
            while True:
                primary_image_path = input("Enter path to primary image: ").strip()
                if os.path.exists(primary_image_path):
                    break
                print("File not found. Please enter a valid path.")
        
        # Initialize game
        print("\n🚀 Initializing game...")
        game_manager = GameManager()
        game_manager.initialize_game(
            primary_image_path=primary_image_path,
            total_rounds=rounds
        )
        
        print("✅ Game initialized successfully!")
        
        # Game loop
        while not game_manager.game_state['game_finished']:
            round_info = game_manager.get_current_round_info()
            if not round_info:
                break
            
            print(f"\n{'='*60}")
            print(f"🎯 ROUND {round_info['round']} of {game_manager.game_state['total_rounds']}")
            print(f"{'='*60}")
            
            print(f"📁 Original Image: {round_info['original_image']}")
            print(f"🎯 Target Image: {round_info['target_image']}")
            print(f"⏰ Time limit: {GAME_CONFIG['turn_time_limit']} seconds")
            
            # Get player prompt
            print("\n💭 Enter your prompt to recreate the target image:")
            prompt = input("> ").strip()
            
            if not prompt:
                print("⚠️  No prompt entered. Using default prompt.")
                prompt = "Transform this image"
            
            # Submit prompt
            print("\n🔄 Processing your prompt...")
            try:
                result = game_manager.submit_player_prompt(prompt)
                print(f"✅ Round {result['round']} completed!")
                print(f"📝 Your prompt: {result['prompt']}")
                print(f"🖼️  Generated image: {result['image_path']}")
                
            except Exception as e:
                print(f"❌ Error processing prompt: {e}")
                break
        
        # Show results
        if game_manager.game_state['game_finished']:
            print(f"\n{'='*60}")
            print("🎉 GAME COMPLETE! 🎉")
            print(f"{'='*60}")
            
            chain = game_manager.get_full_chain()
            if chain:
                print(f"\n📋 FULL PROMPT CHAIN:")
                print(f"{'='*50}")
                
                for round_data in chain['rounds']:
                    print(f"\nRound {round_data['round']} ({round_data['player_name']}):")
                    print(f"Prompt: \"{round_data['prompt']}\"")
                    print(f"Image: {round_data['image_path']}")
                    print("-" * 30)
        
        print("\n👋 Thanks for playing Prompt Chain!")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Game interrupted by user.")
    except Exception as e:
        logger.error(f"Error in CLI game: {e}")
        print(f"❌ Error: {e}")

def run_gui_game():
    """Run the game in GUI mode"""
    try:
        from gui import PromptChainGUI
        app = PromptChainGUI()
        app.run()
    except Exception as e:
        logger.error(f"Error in GUI game: {e}")
        print(f"❌ Error starting GUI: {e}")
        print("Falling back to CLI mode...")
        run_cli_game()

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Prompt Chain - AI Image Transformation Game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py                    # Start GUI
  python main.py --cli              # Start command-line interface
  python main.py --test-api         # Test BFL Flux API connection
        """
    )
    
    parser.add_argument('--cli', action='store_true',
                       help='Run in command-line interface mode')
    parser.add_argument('--test-api', action='store_true',
                       help='Test BFL Flux API connection')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug logging')
    
    args = parser.parse_args()
    
    # Set debug logging if requested
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Check for required environment variable
    if not os.getenv('BFL_API_KEY'):
        print("❌ Error: BFL_API_KEY environment variable is required!")
        print("Please set your Black Forest Labs API key in a .env file or environment variable.")
        print("\nExample .env file:")
        print("BFL_API_KEY=your_bfl_api_key_here")
        print("\nGet your API key from: https://blackforestlabs.com/")
        return 1
    
    # Test API connection if requested
    if args.test_api:
        success = test_api_connection()
        return 0 if success else 1
    
    # Run game
    try:
        if args.cli:
            run_cli_game()
        else:
            run_gui_game()
        return 0
        
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"❌ Unexpected error: {e}")
        return 1

if __name__ == "__main__":
    # Import config here to avoid circular imports
    from config import GAME_CONFIG
    
    sys.exit(main()) 