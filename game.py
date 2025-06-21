import os
from dotenv import load_dotenv
import replicate

# Load environment variables from .env file
load_dotenv()

# Get the API token
api_token = os.getenv("REPLICATE_API_TOKEN")
client = replicate.Client(api_token=api_token)

def main():
    print("Welcome to AI Image Telephone (CLI Prototype)!")
    
    # Prompt for number of players
    while True:
        try:
            num_players = int(input("How many players? (2-6): ").strip())
            if 2 <= num_players <= 6:
                break
            else:
                print("Please enter a number between 2 and 6.")
        except ValueError:
            print("Invalid input. Please enter a number.")

    image_path = input("Enter the path to your input image (JPG/PNG): ").strip()
    if not os.path.isfile(image_path):
        print("File does not exist. Exiting.")
        return
    if not (image_path.lower().endswith('.jpg') or image_path.lower().endswith('.jpeg') or image_path.lower().endswith('.png')):
        print("File must be a JPG or PNG image. Exiting.")
        return
    
    # Ensure images directory exists
    images_dir = os.path.join(os.path.dirname(__file__), "images")
    if not os.path.exists(images_dir):
        os.makedirs(images_dir)

    for player_num in range(1, num_players + 1):
        print(f"\n--- Player {player_num}'s turn ---")
        user_guess = input("What do you think the prompt was for the modification?\n> ")
        print(f"You guessed: {user_guess}")

        input_params = {
            "image": open(image_path, "rb"),  # Always use the original image
            "prompt": user_guess,
            "prompt_upsampling": True
        }
        output = client.run(
            "black-forest-labs/flux-1.1-pro",
            input=input_params
        )
        user_img_path = os.path.join(images_dir, f"user{player_num}.jpg")
        with open(user_img_path, "wb") as file:
            file.write(output.read())
        print(f"AI-generated image saved as {user_img_path}")

    print("\n(Game round complete! All images saved in the ./images folder.)")

if __name__ == "__main__":
    main()
