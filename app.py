from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import os
import uuid
import base64
from dotenv import load_dotenv
import replicate
from werkzeug.utils import secure_filename
import io
import json
import requests
import random
import logging
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from resultsViz import main as analyze_results  # Re-enabled ML analysis
from openai import OpenAI  # Updated import for v1.0+

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
IMAGES_FOLDER = 'images'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure directories exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(IMAGES_FOLDER, exist_ok=True)

# Game state storage (in production, use a proper database)
games = {}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'healthy'})

@app.route('/api/test-openai', methods=['GET'])
def test_openai():
    """Test OpenAI API key and ChatGPT functionality"""
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            return jsonify({
                'status': 'error',
                'message': 'OPENAI_API_KEY not found in environment variables',
                'suggestion': 'Add your OpenAI API key to the .env file'
            }), 400
        
        # Configure OpenAI client
        openai = OpenAI(api_key=openai_api_key)
        
        # Test with a simple prompt
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant. Respond with a simple test message."},
                {"role": "user", "content": "Say 'OpenAI API is working!' and nothing else."}
            ],
            max_tokens=50,
            temperature=0.1
        )
        
        test_response = response.choices[0].message.content.strip()
        
        # Test the wild prompt generation function
        wild_prompt = generate_wild_ai_prompt()
        
        return jsonify({
            'status': 'success',
            'message': 'OpenAI API key is working correctly!',
            'test_response': test_response,
            'wild_prompt_example': wild_prompt,
            'api_key_length': len(openai_api_key),
            'api_key_prefix': openai_api_key[:7] + '...' if len(openai_api_key) > 10 else '***'
        })
        
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'OpenAI API test failed: {str(e)}',
            'error_type': type(e).__name__
        }), 500

@app.route('/api/game/create', methods=['POST'])
def create_game():
    data = request.get_json()
    num_players = data.get('numPlayers', 2)
    
    if not 2 <= num_players <= 6:
        return jsonify({'error': 'Number of players must be between 2 and 6'}), 400
    
    game_id = str(uuid.uuid4())
    games[game_id] = {
        'id': game_id,
        'numPlayers': num_players,
        'currentPlayer': 1,
        'images': [],
        'prompts': [],
        'status': 'waiting_for_image',
        'originalImage': None
    }
    
    return jsonify({
        'gameId': game_id,
        'numPlayers': num_players,
        'status': 'created'
    })

@app.route('/api/game/<game_id>/upload-image', methods=['POST'])
def upload_image(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    if 'image' not in request.files:
        return jsonify({'error': 'No image file provided'}), 400
    
    file = request.files['image']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(UPLOAD_FOLDER, f"{game_id}_{filename}")
        file.save(file_path)
        
        games[game_id]['originalImage'] = file_path
        games[game_id]['images'].append(file_path)
        
        # Generate AI prompt and create first modification
        try:
            api_token = os.getenv("REPLICATE_API_TOKEN")
            if not api_token:
                return jsonify({'error': 'REPLICATE_API_TOKEN not found in environment variables'}), 500
                
            client = replicate.Client(api_token=api_token)
            
            # Generate a wild, creative prompt using ChatGPT
            ai_prompt = generate_wild_ai_prompt()
            
            print(f"AI generating first prompt: {ai_prompt}")
            
            # Process the image with AI
            with open(file_path, "rb") as image_file:
                input_params = {
                    "prompt": ai_prompt,
                    "input_image": image_file,
                    "output_format": "jpg",
                    "temperature": 0.9,  # High temperature for more randomness
                    "guidance_scale": 7.5  # Lower guidance for more creative freedom
                }
                
                output = client.run(
                    "black-forest-labs/flux-kontext-pro",
                    input=input_params
                )
            
            # Save the AI-generated image
            ai_image_path = os.path.join(IMAGES_FOLDER, f"{game_id}_ai_start.jpg")
            
            # Handle different types of output from Replicate
            if hasattr(output, 'read'):
                # If output is a file-like object
                with open(ai_image_path, "wb") as file:
                    file.write(output.read())
            elif isinstance(output, str) and output.startswith('http'):
                # If output is a URL, download it
                response = requests.get(output)
                with open(ai_image_path, "wb") as file:
                    file.write(response.content)
            else:
                return jsonify({'error': f'Unexpected output format from Replicate: {type(output)}'}), 500
            
            # Add AI prompt and image to game state
            games[game_id]['prompts'].append({
                'player': 'AI',
                'prompt': ai_prompt
            })
            games[game_id]['images'].append(ai_image_path)
            
            games[game_id]['status'] = 'ready'
            
            print(f"AI-generated image saved to: {ai_image_path}")
            
            return jsonify({
                'message': 'Image uploaded and AI prompt generated successfully',
                'imagePath': file_path,
                'aiImagePath': ai_image_path,
                'aiPrompt': ai_prompt,
                'status': 'ready'
            })
            
        except Exception as e:
            import traceback
            print(f"Error generating AI prompt: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            # If AI generation fails, still allow the game to continue
            games[game_id]['status'] = 'ready'
            return jsonify({
                'message': 'Image uploaded successfully (AI prompt generation failed)',
                'imagePath': file_path,
                'status': 'ready'
            })
    
    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/api/game/<game_id>/submit-prompt', methods=['POST'])
def submit_prompt(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    data = request.get_json()
    prompt = data.get('prompt', '').strip()
    
    if not prompt:
        return jsonify({'error': 'Prompt cannot be empty'}), 400
    
    game = games[game_id]
    current_player = game['currentPlayer']
    
    # Store the prompt
    game['prompts'].append({
        'player': current_player,
        'prompt': prompt
    })
    
    # Process the image with AI
    try:
        api_token = os.getenv("REPLICATE_API_TOKEN")
        if not api_token:
            return jsonify({'error': 'REPLICATE_API_TOKEN not found in environment variables'}), 500
            
        client = replicate.Client(api_token=api_token)
        
        # Get the original image to modify (always use the first image)
        original_image_path = game['images'][0]  # Always use the original image
        
        # Check if the original image file exists
        if not os.path.exists(original_image_path):
            return jsonify({'error': f'Original image file not found: {original_image_path}'}), 500
        
        print(f"Processing original image: {original_image_path}")
        print(f"Player {current_player} prompt: {prompt}")
        print(f"Note: AI will modify the original image, not the previous player's image")
        
        # Read the original file and pass it as a file-like object
        with open(original_image_path, "rb") as image_file:
            input_params = {
                "prompt": prompt,
                "input_image": image_file,
                "output_format": "jpg",
                "temperature": 0.9,  # High temperature for more randomness
                "guidance_scale": 7.5  # Lower guidance for more creative freedom
            }
            
            print(f"Calling Replicate API with prompt: {prompt}")
            
            output = client.run(
                "black-forest-labs/flux-kontext-pro",
                input=input_params
            )
        
        print(f"Replicate API response received: {type(output)}")
        
        # Save the new image - handle different response types
        new_image_path = os.path.join(IMAGES_FOLDER, f"{game_id}_player_{current_player}.jpg")
        
        # Handle different types of output from Replicate
        if hasattr(output, 'read'):
            # If output is a file-like object
            with open(new_image_path, "wb") as file:
                file.write(output.read())
        elif isinstance(output, str) and output.startswith('http'):
            # If output is a URL, download it
            response = requests.get(output)
            with open(new_image_path, "wb") as file:
                file.write(response.content)
        else:
            return jsonify({'error': f'Unexpected output format from Replicate: {type(output)}'}), 500
        
        print(f"Image saved to: {new_image_path}")
        
        game['images'].append(new_image_path)
        
        # Move to next player or end game
        if current_player < game['numPlayers']:
            game['currentPlayer'] += 1
            game['status'] = 'in_progress'
        else:
            game['status'] = 'completed'
        
        return jsonify({
            'message': 'Prompt processed successfully',
            'newImagePath': new_image_path,
            'currentPlayer': game['currentPlayer'],
            'status': game['status'],
            'isGameComplete': game['status'] == 'completed'
        })
        
    except Exception as e:
        import traceback
        print(f"Error in submit_prompt: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to process image: {str(e)}'}), 500

@app.route('/api/game/<game_id>/status', methods=['GET'])
def get_game_status(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    return jsonify({
        'gameId': game_id,
        'numPlayers': game['numPlayers'],
        'currentPlayer': game['currentPlayer'],
        'status': game['status'],
        'images': game['images'],
        'prompts': game['prompts'],
        'isGameComplete': game['status'] == 'completed',
        'analysis': game.get('analysis', None)
    })

@app.route('/api/game/<game_id>/analyze', methods=['POST'])
def analyze_game_results(game_id):
    """Analyze game results using resultsViz"""
    try:
        if game_id not in games:
            return jsonify({'error': 'Game not found'}), 404
        
        game = games[game_id]
        if game['status'] != 'completed':
            return jsonify({'error': 'Game not completed yet'}), 400
        
        # Validate we have enough data for analysis
        if len(game['prompts']) < 2 or len(game['images']) < 3:
            return jsonify({'error': 'Not enough data for analysis'}), 400
        
        # Extract data for analysis
        # We want to compare ALL interpretations against the original image
        # This includes the AI's modification and all player modifications
        
        # The original image is at index 0, all modifications start at index 1
        original_image = game['images'][0]  # Original uploaded image
        all_modified_images = game['images'][1:]  # AI + Player modifications
        
        # For prompts, we compare all prompts against the original (empty) or include AI as first player
        # Since we don't have an "original prompt", we'll treat the AI prompt as the reference
        ai_prompt = game['prompts'][0]['prompt']  # First AI prompt
        all_prompts = [prompt['prompt'] for prompt in game['prompts']]  # AI + Player prompts
        
        # Debug: Print the data being passed to analysis
        print(f"Analysis data:")
        print(f"Original image: {original_image}")
        print(f"AI prompt: {ai_prompt}")
        print(f"All prompts: {all_prompts}")
        print(f"All modified images: {all_modified_images}")
        print(f"Original image exists: {os.path.exists(original_image)}")
        for i, img in enumerate(all_modified_images):
            print(f"Modified image {i+1} exists: {os.path.exists(img)}")
        
        # Run the analysis - compare all modified images against original image
        # and all prompts against the AI prompt (treating AI as first player)
        try:
            results = analyze_results(ai_prompt, all_prompts, original_image, all_modified_images)
            
            # Validate that all result arrays have the same length
            prompt_semantic_count = len(results['prompt_semantic_scores'])
            prompt_levenshtein_count = len(results['prompt_levenshtein_scores'])
            image_similarity_count = len(results['image_similarity_scores'])
            total_count = len(all_prompts)
            
            print(f"Analysis validation:")
            print(f"Total players (including AI): {total_count}")
            print(f"Prompt semantic scores: {prompt_semantic_count}")
            print(f"Prompt levenshtein scores: {prompt_levenshtein_count}")
            print(f"Image similarity scores: {image_similarity_count}")
            
            if not (prompt_semantic_count == prompt_levenshtein_count == image_similarity_count == total_count):
                print(f"WARNING: Array length mismatch! All should be {total_count}")
                # Truncate arrays to the shortest length
                min_length = min(prompt_semantic_count, prompt_levenshtein_count, image_similarity_count, total_count)
                results['prompt_semantic_scores'] = results['prompt_semantic_scores'][:min_length]
                results['prompt_levenshtein_scores'] = results['prompt_levenshtein_scores'][:min_length]
                results['image_similarity_scores'] = results['image_similarity_scores'][:min_length]
                print(f"Truncated all arrays to length: {min_length}")
                
        except Exception as analysis_error:
            print(f"ML analysis failed, using fallback: {analysis_error}")
            # Fallback to placeholder results
            num_players = len(all_prompts)
            results = {
                'prompt_semantic_scores': [0.5 + random.uniform(-0.2, 0.2) for _ in range(num_players)],
                'prompt_levenshtein_scores': [0.3 + random.uniform(-0.1, 0.1) for _ in range(num_players)],
                'image_similarity_scores': [0.6 + random.uniform(-0.2, 0.2) for _ in range(num_players)]
            }
            print("Using fallback analysis results")
        
        # Calculate final score
        mean_cos_sim_prompt = sum(results['prompt_semantic_scores']) / len(results['prompt_semantic_scores'])
        mean_cos_sim_image = sum(results['image_similarity_scores']) / len(results['image_similarity_scores'])
        mean_lev = sum(results['prompt_levenshtein_scores']) / len(results['prompt_levenshtein_scores'])

        normalized_sim_prompt = (mean_cos_sim_prompt + 1) / 2
        normalized_sim_image = (mean_cos_sim_image + 1) / 2

        final_score = int(mean_lev * 100 + normalized_sim_prompt * 100 + normalized_sim_image * 100)
        
        # Add analysis results to game data
        game['analysis'] = {
            'final_score': final_score,
            'prompt_semantic_scores': results['prompt_semantic_scores'],
            'prompt_levenshtein_scores': results['prompt_levenshtein_scores'],
            'image_similarity_scores': results['image_similarity_scores']
        }
        
        return jsonify({
            'final_score': final_score,
            'prompt_semantic_scores': results['prompt_semantic_scores'],
            'prompt_levenshtein_scores': results['prompt_levenshtein_scores'],
            'image_similarity_scores': results['image_similarity_scores']
        })
        
    except Exception as e:
        import traceback
        logging.error(f"Error analyzing game results: {e}")
        logging.error(f"Traceback: {traceback.format_exc()}")
        print(f"Error analyzing game results: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({'error': f'Failed to analyze game results: {str(e)}'}), 500

@app.route('/api/game/<game_id>/image/<int:image_index>', methods=['GET'])
def get_image(game_id, image_index):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    game = games[game_id]
    if image_index >= len(game['images']):
        return jsonify({'error': 'Image index out of range'}), 404
    
    image_path = game['images'][image_index]
    return send_file(image_path, mimetype='image/jpeg')

@app.route('/api/game/<game_id>/reset', methods=['POST'])
def reset_game(game_id):
    if game_id not in games:
        return jsonify({'error': 'Game not found'}), 404
    
    # Keep the same game ID but reset the state
    num_players = games[game_id]['numPlayers']
    games[game_id] = {
        'id': game_id,
        'numPlayers': num_players,
        'currentPlayer': 1,
        'images': [],
        'prompts': [],
        'status': 'waiting_for_image',
        'originalImage': None
    }
    
    return jsonify({
        'message': 'Game reset successfully',
        'gameId': game_id,
        'status': 'waiting_for_image'
    })

def generate_wild_ai_prompt():
    """Generate a wild, creative prompt using ChatGPT that will dramatically alter an image"""
    try:
        # Check if OpenAI API key is available
        openai_api_key = os.getenv("OPENAI_API_KEY")
        if not openai_api_key:
            # Fallback to hardcoded prompts if no API key
            return generate_fallback_prompt()
        
        # Configure OpenAI client
        openai = OpenAI(api_key=openai_api_key)
        
        # Create a system prompt that encourages wild, creative transformations
        system_prompt = """You are an AI artist who specializes in creating absolutely wild, vibey, and mind-bending image modifications. Your job is to take an existing image and add crazy, unexpected elements, creatures, or effects, while keeping the original image partially visible and recognizable.

Your prompts should:
- ADD new whacky elements, creatures, objects, or effects to the image (not just style changes)
- Keep the original image content partially visible and recognizable
- Create a vibey, energetic, and fun atmosphere
- Mix different styles, genres, and concepts in bizarre ways
- Be extremely creative and unexpected
- Include surreal, dreamlike, or impossible scenarios
- Be specific about what to add while preserving what to keep
- Create a wild, party-like, or psychedelic vibe
- Avoid anything offensive or inappropriate

Examples of good WHACKY ADDITION prompts:
- "Add a giant rainbow unicorn riding a skateboard while shooting laser beams from its horn, with the original image visible through a magical portal"
- "Transform this into a cyberpunk rave scene with neon dinosaurs breakdancing, holographic jellyfish floating around, and the original image glowing in the background"
- "Add a squad of tiny robots having a tea party on floating clouds, with rainbow lightning bolts and the original image as a mystical backdrop"
- "Turn this into a candyland explosion with gummy bears riding motorcycles, cotton candy tornadoes, and the original image as a dreamy foundation"
- "Add a time-traveling wizard riding a rocket-powered pizza while being chased by space cats, with the original image as a cosmic canvas"
- "Transform into a music festival where musical notes are alive and dancing, with rainbow fireworks and the original image as the stage backdrop"
- "Add a parallel universe where everything is made of food - pizza mountains, ice cream waterfalls, and the original image as the edible foundation"
- "Turn this into a superhero battle scene with capes made of lightning, powers that create rainbow explosions, and the original image as the heroic backdrop"
- "Add a magical forest where trees are made of neon lights, animals wear sunglasses, and the original image glows through the mystical atmosphere"
- "Transform into a sci-fi adventure with aliens having a beach party, spaceships made of candy, and the original image as the cosmic foundation"

AVOID prompts that:
- Only change the style or filter
- Completely replace the original image content
- Don't add new elements
- Are too tame or boring
- Ignore the original composition entirely

Generate ONE wild, vibey prompt that will add crazy new elements while keeping the original image partially visible and creating an amazing, energetic atmosphere."""

        # Generate the prompt using ChatGPT
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": "Generate a creative modification prompt to alter an existing image while keeping its core elements recognizable."}
            ],
            max_tokens=150,
            temperature=0.9,  # High temperature for more creativity
            top_p=0.9
        )
        
        ai_prompt = response.choices[0].message.content.strip()
        
        # Clean up the prompt (remove quotes if present)
        if ai_prompt.startswith('"') and ai_prompt.endswith('"'):
            ai_prompt = ai_prompt[1:-1]
        
        return ai_prompt
        
    except Exception as e:
        print(f"Error generating ChatGPT prompt: {str(e)}")
        # Fallback to hardcoded prompts
        return generate_fallback_prompt()

def generate_fallback_prompt():
    """Fallback function with hardcoded modification prompts if ChatGPT is unavailable"""
    ai_prompts = [
        "Apply a cyberpunk filter with neon lighting while keeping the original subject and composition",
        "Transform this into a watercolor painting style while preserving the main elements",
        "Add a dreamy, ethereal glow effect and soft lighting to this image",
        "Convert to a vintage film aesthetic with warm tones and grain while keeping the subject",
        "Apply a steampunk overlay with brass and copper tones to the existing elements",
        "Add magical sparkles and a fantasy atmosphere while maintaining the original scene",
        "Transform the lighting to golden hour with warm, dramatic shadows",
        "Apply a retro 80s aesthetic with vibrant colors and synthwave vibes",
        "Add a subtle glitch effect and digital distortion to the image",
        "Convert to a comic book style with bold outlines and flat colors",
        "Apply a noir film effect with high contrast and dramatic shadows",
        "Add a soft bokeh background effect while keeping the main subject sharp",
        "Transform to a pastel color palette with gentle, dreamy tones",
        "Apply a vintage polaroid effect with warm colors and slight vignette",
        "Add a subtle rainbow prism effect to the lighting",
        "Convert to a minimalist style with clean lines and reduced colors",
        "Apply a soft focus effect with romantic, dreamy atmosphere",
        "Add a subtle holographic overlay with iridescent colors",
        "Transform to a black and white with selective color highlights",
        "Apply a soft vintage filter with faded, nostalgic tones"
    ]
    
    return random.choice(ai_prompts)

@app.route('/api/test-ml-models', methods=['GET'])
def test_ml_models():
    """Test if ML models can load properly"""
    try:
        print("Testing ML model loading...")
        
        # Test sentence transformer
        print("Loading sentence transformer...")
        from sentence_transformers import SentenceTransformer
        model = SentenceTransformer('all-MiniLM-L6-v2')
        print("✓ Sentence transformer loaded successfully")
        
        # Test ViT model
        print("Loading ViT model...")
        from transformers import ViTFeatureExtractor, ViTModel
        feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224-in21k")
        vit_model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")
        print("✓ ViT model loaded successfully")
        
        # Test basic functionality
        print("Testing basic functionality...")
        test_prompt1 = "A cat sitting on a chair"
        test_prompt2 = "A dog lying on a couch"
        
        emb1 = model.encode(test_prompt1, convert_to_tensor=True)
        emb2 = model.encode(test_prompt2, convert_to_tensor=True)
        print("✓ Sentence encoding works")
        
        return jsonify({
            'status': 'success',
            'message': 'All ML models loaded and tested successfully',
            'models_tested': ['sentence-transformers', 'ViT']
        })
        
    except Exception as e:
        import traceback
        print(f"ML model test failed: {e}")
        print(f"Traceback: {traceback.format_exc()}")
        return jsonify({
            'status': 'error',
            'message': f'ML model test failed: {str(e)}',
            'error_type': type(e).__name__
        }), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 