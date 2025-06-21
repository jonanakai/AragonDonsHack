from sentence_transformers import SentenceTransformer, util
import torch
import torch.nn.functional as F
import Levenshtein
from transformers import ViTFeatureExtractor, ViTModel
from PIL import Image
import matplotlib.pyplot as plt
import numpy as np

def simScoreImage(image1, image2):
    # Load pretrained ViT and feature extractor
    model = ViTModel.from_pretrained("google/vit-base-patch16-224-in21k")
    feature_extractor = ViTFeatureExtractor.from_pretrained("google/vit-base-patch16-224-in21k")
    model.eval()

    # Load and preprocess two images
    # image paths 
    image1 = Image.open(image1).convert("RGB")
    image2 = Image.open(image2).convert("RGB")

    inputs1 = feature_extractor(images=image1, return_tensors="pt")
    inputs2 = feature_extractor(images=image2, return_tensors="pt")

    # Get embeddings (use CLS token output)
    with torch.no_grad():
        output1 = model(**inputs1).last_hidden_state[:, 0]
        output2 = model(**inputs2).last_hidden_state[:, 0]

    cosine_sim = F.cosine_similarity(output1, output2, dim=1).item()
    print("cosine similarity")
    print(cosine_sim)

    return cosine_sim

def simScore(prompt1, prompt2):
    model = SentenceTransformer('all-MiniLM-L6-v2')
    emb1 = model.encode(prompt1, convert_to_tensor=True)
    emb2 = model.encode(prompt2, convert_to_tensor=True)

    # Cosine similarity
    cosine_sim = F.cosine_similarity(emb1, emb2, dim=0)
    print("Semantic similarity:", cosine_sim.item())
    print("cosine similarity")
    print(cosine_sim)
    return cosine_sim.item()

def levScore(prompt1, prompt2):
    dist_calc = Levenshtein.distance(prompt1, prompt2)
    lev_similarity = 1 - (dist_calc / max(len(prompt1), len(prompt2)))
    return lev_similarity

def main(reference_prompt, example_prompts, reference_image, example_images):
    """
    Compute similarity scores between reference and example prompts/images, then plot trends.
    
    Args:
        reference_prompt: The reference text prompt to compare against
        example_prompts: List of example text prompts to compare with reference
        reference_image: The reference image path to compare against
        example_images: List of example image paths to compare with reference
    """
    
    # Initialize lists to store similarity scores
    prompt_semantic_scores = []
    prompt_levenshtein_scores = []
    image_similarity_scores = []
    
    # Compute similarities between reference prompt and each example prompt
    print("Computing prompt similarities against reference...")
    for i, example_prompt in enumerate(example_prompts):
        print(f"Comparing reference prompt with example prompt {i+1}")
        
        # Semantic similarity
        sem_sim = simScore(reference_prompt, example_prompt)
        prompt_semantic_scores.append(sem_sim)
        
        # Levenshtein distance
        lev_dist = levScore(reference_prompt, example_prompt)
        prompt_levenshtein_scores.append(lev_dist)
    
    # Compute similarities between reference image and each example image
    print("\nComputing image similarities against reference...")
    for i, example_image in enumerate(example_images):
        print(f"Comparing reference image with example image {i+1}")
        
        img_sim = simScoreImage(reference_image, example_image)
        image_similarity_scores.append(img_sim)
    
    # Set up plotting style
    plt.style.use('default')
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.linewidth'] = 1.2
    plt.rcParams['grid.alpha'] = 0.3
    
    # Ensure all arrays have the same length for consistent plotting
    max_length = max(len(prompt_semantic_scores), len(prompt_levenshtein_scores), len(image_similarity_scores))
    
    # Pad shorter arrays with the last value to match the longest array
    if len(prompt_semantic_scores) < max_length:
        last_value = prompt_semantic_scores[-1] if prompt_semantic_scores else 0
        prompt_semantic_scores.extend([last_value] * (max_length - len(prompt_semantic_scores)))
    
    if len(prompt_levenshtein_scores) < max_length:
        last_value = prompt_levenshtein_scores[-1] if prompt_levenshtein_scores else 0
        prompt_levenshtein_scores.extend([last_value] * (max_length - len(prompt_levenshtein_scores)))
    
    if len(image_similarity_scores) < max_length:
        last_value = image_similarity_scores[-1] if image_similarity_scores else 0
        image_similarity_scores.extend([last_value] * (max_length - len(image_similarity_scores)))
    
    # Create consistent x-axis for all plots
    x_axis = list(range(1, max_length + 1))
    
    print(f"Plotting with {max_length} users for all charts")
    print(f"Prompt semantic scores: {len(prompt_semantic_scores)}")
    print(f"Prompt levenshtein scores: {len(prompt_levenshtein_scores)}")
    print(f"Image similarity scores: {len(image_similarity_scores)}")
    
    # Plot 1: Reference vs Example Prompts Semantic Similarity
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, prompt_semantic_scores, 'b-o', linewidth=2.5, markersize=8, 
             markerfacecolor='lightblue', markeredgecolor='blue', markeredgewidth=2)
    
    plt.title('Semantic Similarity To Original Prompt', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('User', fontsize=13)
    plt.ylabel('Similarity To Original', fontsize=13)
    plt.grid(True, alpha=0.3)
    
    # Set x-axis to show only whole numbers
    plt.xticks(x_axis)
    
    # Allow full range for y-axis (can include negative values)
    y_min = min(prompt_semantic_scores) - 0.1
    y_max = max(prompt_semantic_scores) + 0.1
    plt.ylim(y_min, y_max)
    
    # Add value labels on points
    for i, v in enumerate(prompt_semantic_scores):
        plt.annotate(f'{v:.3f}', (i+1, v), textcoords="offset points", 
                    xytext=(0,12), ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add horizontal line for average
    avg_semantic = np.mean(prompt_semantic_scores)
    plt.axhline(y=avg_semantic, color='blue', linestyle='--', alpha=0.7, linewidth=2,
                label=f'Average: {avg_semantic:.3f}')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('SemanticCompare.png', dpi=300, bbox_inches='tight')
    
    # Plot 2: Reference vs Example Prompts Levenshtein Distance
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, prompt_levenshtein_scores, 'r-s', linewidth=2.5, markersize=8,
             markerfacecolor='lightcoral', markeredgecolor='red', markeredgewidth=2)
    
    plt.title('Levenshtein Similarity To Original Prompt', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('User', fontsize=13)
    plt.ylabel('Similarity To Original', fontsize=13)
    plt.grid(True, alpha=0.3)
    
    # Set x-axis to show only whole numbers
    plt.xticks(x_axis)
    
    # Keep y-axis scale 0-1 for Levenshtein
    plt.ylim(0, 1)
    
    # Add value labels on points
    for i, v in enumerate(prompt_levenshtein_scores):
        plt.annotate(f'{v:.3f}', (i+1, v), textcoords="offset points", 
                    xytext=(0,12), ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add horizontal line for average
    avg_levenshtein = np.mean(prompt_levenshtein_scores)
    plt.axhline(y=avg_levenshtein, color='red', linestyle='--', alpha=0.7, linewidth=2,
                label=f'Average: {avg_levenshtein:.3f}')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('LevCompare.png', dpi=300, bbox_inches='tight')
    
    # Plot 3: Reference vs Example Images Similarity
    plt.figure(figsize=(10, 6))
    plt.plot(x_axis, image_similarity_scores, 'g-^', linewidth=2.5, markersize=8,
             markerfacecolor='lightgreen', markeredgecolor='green', markeredgewidth=2)
    
    plt.title('Visual Similarity To First Generation', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('User', fontsize=13)
    plt.ylabel('Similarity To Original', fontsize=13)
    plt.grid(True, alpha=0.3)
    
    # Set x-axis to show only whole numbers
    plt.xticks(x_axis)
    
    # Allow full range for y-axis (can include negative values)
    y_min = min(image_similarity_scores) - 0.1
    y_max = max(image_similarity_scores) + 0.1
    plt.ylim(y_min, y_max)
    
    # Add value labels on points
    for i, v in enumerate(image_similarity_scores):
        plt.annotate(f'{v:.3f}', (i+1, v), textcoords="offset points", 
                    xytext=(0,12), ha='center', fontsize=10, fontweight='bold',
                    bbox=dict(boxstyle="round,pad=0.2", facecolor='white', alpha=0.8))
    
    # Add horizontal line for average
    avg_image = np.mean(image_similarity_scores)
    plt.axhline(y=avg_image, color='green', linestyle='--', alpha=0.7, linewidth=2,
                label=f'Average: {avg_image:.3f}')
    plt.legend(fontsize=11)
    plt.tight_layout()
    plt.savefig('ImageCompare.png', dpi=300, bbox_inches='tight')
    
    # Print summary

    mean_cos_sim_prompt = np.mean(prompt_semantic_scores)
    mean_cos_sim_image = np.mean(image_similarity_scores)
    mean_lev = np.mean(prompt_levenshtein_scores)

    normalized_sim_prompt = (mean_cos_sim_prompt + 1) / 2
    normalized_sim_image = (mean_cos_sim_image + 1) / 2

    score = mean_lev * 100 + normalized_sim_prompt * 100 + normalized_sim_image * 100

    print(f"FINAL SCORE: {int(score)}")


    return {
        'reference_prompt': reference_prompt,
        'reference_image': reference_image,
        'prompt_semantic_scores': prompt_semantic_scores,
        'prompt_levenshtein_scores': prompt_levenshtein_scores,
        'image_similarity_scores': image_similarity_scores
    }

    print()

# Example usage:
if __name__ == "__main__":
    # Example reference and example data (replace with your actual data)

    # change this to the original first prompt
    reference_prompt = "A beautiful sunset over the ocean"
    # change these to the prompts by the users
    example_prompts = [
        "A stunning sunset at the beach",
        "A dog playing in the park", 
        "A cat sleeping on a couch",
        "A bird flying in the sky",
        "clown crying"
    ]
    # change this to the path to the original image created by the first prompt
    reference_image = "/mnt/c/users/lludw/projects/test/sunset.jpg"

    # change these to the paths to the images generated by the user promtps
    example_images = [
        "/mnt/c/users/lludw/projects/test/sunsetBeach.jpg",
        "/mnt/c/users/lludw/projects/test/dogsPark.jpg", 
        "/mnt/c/users/lludw/projects/test/catCouch.jpg",
        "/mnt/c/users/lludw/projects/test/birdSky.jpg",
        "/mnt/c/users/lludw/projects/test/clown.jpg"
    ]
    
    # Call the main function
    results = main(reference_prompt, example_prompts, reference_image, example_images)