import os
import json
import time
from datetime import datetime
from PIL import Image
import logging
from config import GAME_CONFIG, FILE_CONFIG
from flux_api import FluxAPI

logger = logging.getLogger(__name__)

class GameManager:
    def __init__(self):
        self.flux_api = FluxAPI()
        self.game_state = {
            'current_round': 0,
            'total_rounds': GAME_CONFIG['default_rounds'],
            'primary_image_path': None,
            'rounds_data': [],
            'game_started': False,
            'game_finished': False,
            'start_time': None,
            'end_time': None
        }
        self._setup_directories()
    
    def _setup_directories(self):
        """Create necessary directories for the game"""
        directories = [
            FILE_CONFIG['primary_image_dir'],
            FILE_CONFIG['rounds_dir'],
            FILE_CONFIG['prompts_dir'],
            FILE_CONFIG['output_dir'],
            FILE_CONFIG['logs_dir']
        ]
        
        for directory in directories:
            os.makedirs(directory, exist_ok=True)
            logger.info(f"Created directory: {directory}")
    
    def initialize_game(self, primary_image_path=None, total_rounds=None):
        """Initialize a new game"""
        if total_rounds:
            self.game_state['total_rounds'] = min(max(total_rounds, GAME_CONFIG['min_rounds']), GAME_CONFIG['max_rounds'])
        
        # Generate or use provided primary image
        if primary_image_path and os.path.exists(primary_image_path):
            self.game_state['primary_image_path'] = primary_image_path
        else:
            self.game_state['primary_image_path'] = self._generate_primary_image()
        
        # Generate initial AI prompt and transformed image
        self._generate_initial_round()
        
        self.game_state['game_started'] = True
        self.game_state['start_time'] = datetime.now()
        self.game_state['current_round'] = 1
        
        logger.info(f"Game initialized with {self.game_state['total_rounds']} rounds")
        return self.game_state
    
    def _generate_primary_image(self):
        """Generate a primary image using AI"""
        primary_prompt = "A beautiful landscape photograph with mountains, trees, and a clear blue sky, high quality, detailed"
        output_path = os.path.join(FILE_CONFIG['primary_image_dir'], 'primary_image.jpg')
        
        try:
            self.flux_api.generate_image_from_prompt(primary_prompt, output_path)
            logger.info(f"Generated primary image: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Failed to generate primary image: {e}")
            raise
    
    def _generate_initial_round(self):
        """Generate the initial AI round (round 0)"""
        initial_prompt = "Transform this landscape into a magical fantasy scene with floating islands and glowing crystals"
        round_dir = os.path.join(FILE_CONFIG['rounds_dir'], 'round_0')
        os.makedirs(round_dir, exist_ok=True)
        
        prompt_path = os.path.join(round_dir, 'prompt.txt')
        image_path = os.path.join(round_dir, 'altered_image.jpg')
        
        # Save the AI prompt
        with open(prompt_path, 'w') as f:
            f.write(initial_prompt)
        
        # Generate the transformed image
        try:
            self.flux_api.transform_image_with_prompt(
                self.game_state['primary_image_path'],
                initial_prompt,
                image_path
            )
            
            round_data = {
                'round': 0,
                'prompt': initial_prompt,
                'prompt_path': prompt_path,
                'image_path': image_path,
                'is_ai_round': True,
                'timestamp': datetime.now().isoformat()
            }
            
            self.game_state['rounds_data'].append(round_data)
            logger.info("Generated initial AI round")
            
        except Exception as e:
            logger.error(f"Failed to generate initial round: {e}")
            raise
    
    def submit_player_prompt(self, prompt, player_name="Player"):
        """Submit a player's prompt for the current round"""
        if not self.game_state['game_started'] or self.game_state['game_finished']:
            raise ValueError("Game is not active")
        
        if self.game_state['current_round'] > self.game_state['total_rounds']:
            raise ValueError("Game is already finished")
        
        # Create round directory
        round_dir = os.path.join(FILE_CONFIG['rounds_dir'], f'round_{self.game_state["current_round"]}')
        os.makedirs(round_dir, exist_ok=True)
        
        prompt_path = os.path.join(round_dir, 'prompt.txt')
        image_path = os.path.join(round_dir, 'altered_image.jpg')
        
        # Save the player's prompt
        with open(prompt_path, 'w') as f:
            f.write(prompt)
        
        # Get the previous image to transform
        if self.game_state['current_round'] == 1:
            # First player round - use the AI's transformed image
            previous_image = self.game_state['rounds_data'][0]['image_path']
        else:
            # Use the previous player's output
            previous_image = self.game_state['rounds_data'][-1]['image_path']
        
        # Generate the transformed image
        try:
            self.flux_api.transform_image_with_prompt(
                self.game_state['primary_image_path'],  # Always use primary image as base
                prompt,
                image_path
            )
            
            round_data = {
                'round': self.game_state['current_round'],
                'prompt': prompt,
                'prompt_path': prompt_path,
                'image_path': image_path,
                'player_name': player_name,
                'is_ai_round': False,
                'timestamp': datetime.now().isoformat()
            }
            
            self.game_state['rounds_data'].append(round_data)
            self.game_state['current_round'] += 1
            
            # Check if game is finished
            if self.game_state['current_round'] > self.game_state['total_rounds']:
                self._finish_game()
            
            logger.info(f"Player {player_name} submitted prompt for round {round_data['round']}")
            return round_data
            
        except Exception as e:
            logger.error(f"Failed to process player prompt: {e}")
            raise
    
    def _finish_game(self):
        """Mark the game as finished"""
        self.game_state['game_finished'] = True
        self.game_state['end_time'] = datetime.now()
        self._save_game_summary()
        logger.info("Game finished")
    
    def _save_game_summary(self):
        """Save a summary of the game"""
        summary = {
            'game_info': {
                'total_rounds': self.game_state['total_rounds'],
                'start_time': self.game_state['start_time'].isoformat() if self.game_state['start_time'] else None,
                'end_time': self.game_state['end_time'].isoformat() if self.game_state['end_time'] else None,
                'duration': str(self.game_state['end_time'] - self.game_state['start_time']) if self.game_state['start_time'] and self.game_state['end_time'] else None
            },
            'primary_image': self.game_state['primary_image_path'],
            'rounds': self.game_state['rounds_data']
        }
        
        summary_path = os.path.join(FILE_CONFIG['output_dir'], 'game_summary.json')
        with open(summary_path, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Game summary saved to {summary_path}")
    
    def get_current_round_info(self):
        """Get information for the current round"""
        if not self.game_state['game_started']:
            return None
        
        if self.game_state['current_round'] == 1:
            # First player round
            return {
                'round': 1,
                'original_image': self.game_state['primary_image_path'],
                'target_image': self.game_state['rounds_data'][0]['image_path'],
                'is_final_round': self.game_state['total_rounds'] == 1
            }
        elif self.game_state['current_round'] <= self.game_state['total_rounds']:
            # Subsequent rounds
            return {
                'round': self.game_state['current_round'],
                'original_image': self.game_state['primary_image_path'],
                'target_image': self.game_state['rounds_data'][-1]['image_path'],
                'is_final_round': self.game_state['current_round'] == self.game_state['total_rounds']
            }
        else:
            return None
    
    def get_game_progress(self):
        """Get current game progress"""
        return {
            'current_round': self.game_state['current_round'],
            'total_rounds': self.game_state['total_rounds'],
            'progress_percentage': (self.game_state['current_round'] - 1) / self.game_state['total_rounds'] * 100,
            'game_finished': self.game_state['game_finished']
        }
    
    def get_full_chain(self):
        """Get the complete prompt chain for review"""
        if not self.game_state['game_finished']:
            return None
        
        chain = {
            'primary_image': self.game_state['primary_image_path'],
            'rounds': []
        }
        
        for round_data in self.game_state['rounds_data']:
            chain['rounds'].append({
                'round': round_data['round'],
                'prompt': round_data['prompt'],
                'image_path': round_data['image_path'],
                'player_name': round_data.get('player_name', 'AI'),
                'is_ai_round': round_data['is_ai_round']
            })
        
        return chain
    
    def reset_game(self):
        """Reset the game state"""
        self.game_state = {
            'current_round': 0,
            'total_rounds': GAME_CONFIG['default_rounds'],
            'primary_image_path': None,
            'rounds_data': [],
            'game_started': False,
            'game_finished': False,
            'start_time': None,
            'end_time': None
        }
        logger.info("Game reset") 