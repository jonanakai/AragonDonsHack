import requests
import json
import time
import os
from PIL import Image
import io
import base64
from config import FLUX_CONFIG
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FluxAPI:
    def __init__(self):
        self.api_key = FLUX_CONFIG['api_key']
        self.api_url = FLUX_CONFIG['api_url']
        self.initial_model_endpoint = FLUX_CONFIG['initial_model_endpoint']
        self.alter_model_endpoint = FLUX_CONFIG['alter_model_endpoint']
        self.max_retries = FLUX_CONFIG['max_retries']
        self.timeout = FLUX_CONFIG['timeout']
        
        if not self.api_key:
            raise ValueError("BFL_API_KEY environment variable is required")
    
    def _encode_image_to_base64(self, image_path):
        """Convert image to base64 string"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            logger.error(f"Error encoding image {image_path}: {e}")
            raise
    
    def _decode_base64_to_image(self, base64_string, output_path):
        """Convert base64 string to image and save"""
        try:
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))
            image.save(output_path)
            return output_path
        except Exception as e:
            logger.error(f"Error decoding base64 image: {e}")
            raise
    
    def generate_image_from_prompt(self, prompt, output_path, size=(1024, 1024)):
        """Generate a new image from a text prompt using BFL Flux (flux-pro-1.1)"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'prompt': prompt,
            'width': size[0],
            'height': size[1],
            'num_images': 1,
            'response_format': 'b64_json'
        }
        endpoint = f"{self.api_url}{self.initial_model_endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Generating image with prompt: {prompt[:50]}...")
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'data' in result and len(result['data']) > 0:
                        image_data = result['data'][0]['b64_json']
                        return self._decode_base64_to_image(image_data, output_path)
                    else:
                        raise Exception("No image data in response")
                else:
                    logger.warning(f"API request failed (attempt {attempt + 1}): {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        response.raise_for_status()
                        
            except Exception as e:
                logger.error(f"Error generating image (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
    
    def transform_image_with_prompt(self, image_path, prompt, output_path, size=(1024, 1024)):
        """Transform an existing image using a prompt with BFL Flux (flux-kontext-pro)"""
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        # Encode the input image
        base64_image = self._encode_image_to_base64(image_path)
        
        payload = {
            'prompt': prompt,
            'image': base64_image,
            'width': size[0],
            'height': size[1],
            'num_images': 1,
            'response_format': 'b64_json'
        }
        endpoint = f"{self.api_url}{self.alter_model_endpoint}"
        
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Transforming image with prompt: {prompt[:50]}...")
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if 'data' in result and len(result['data']) > 0:
                        image_data = result['data'][0]['b64_json']
                        return self._decode_base64_to_image(image_data, output_path)
                    else:
                        raise Exception("No image data in response")
                else:
                    logger.warning(f"API request failed (attempt {attempt + 1}): {response.status_code} - {response.text}")
                    if attempt < self.max_retries - 1:
                        time.sleep(2 ** attempt)
                    else:
                        response.raise_for_status()
                        
            except Exception as e:
                logger.error(f"Error transforming image (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(2 ** attempt)
                else:
                    raise
    
    def test_connection(self):
        """Test the BFL API connection by attempting a simple image generation (dry run)"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            payload = {
                'prompt': 'test',
                'width': 64,
                'height': 64,
                'num_images': 1,
                'response_format': 'b64_json'
            }
            endpoint = f"{self.api_url}{self.initial_model_endpoint}"
            response = requests.post(
                endpoint,
                headers=headers,
                json=payload,
                timeout=10
            )
            if response.status_code == 200:
                logger.info("API test succeeded (dummy image generated)")
                return True
            else:
                logger.error(f"API test failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return False

# The API URL is now https://api.bfl.ai/v1 as set in config.py 