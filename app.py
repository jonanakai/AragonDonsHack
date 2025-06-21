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
        games[game_id]['status'] = 'ready'
        games[game_id]['images'].append(file_path)
        
        return jsonify({
            'message': 'Image uploaded successfully',
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
        
        # Get the current image to modify
        current_image_path = game['images'][-1]
        
        # Check if the image file exists
        if not os.path.exists(current_image_path):
            return jsonify({'error': f'Image file not found: {current_image_path}'}), 500
        
        print(f"Processing image: {current_image_path}")
        print(f"Prompt: {prompt}")
        
        input_params = {
            "image": current_image_path,  # Pass the file path as string
            "prompt": prompt,
            "prompt_upsampling": True
        }
        
        print(f"Calling Replicate API with params: {input_params}")
        
        output = client.run(
            "black-forest-labs/flux-kontext-pro",
            input=input_params
        )
        
        print(f"Replicate API response received: {type(output)}")
        
        # Save the new image - output is already a file-like object
        new_image_path = os.path.join(IMAGES_FOLDER, f"{game_id}_player_{current_player}.jpg")
        
        # Handle different types of output from Replicate
        if hasattr(output, 'read'):
            # If output is a file-like object
            with open(new_image_path, "wb") as file:
                file.write(output.read())
        elif isinstance(output, str) and output.startswith('http'):
            # If output is a URL, download it
            import requests
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
        'isGameComplete': game['status'] == 'completed'
    })

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) 