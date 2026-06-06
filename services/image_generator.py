import os
from PIL import Image
import io

def generate_character_image(character_description, character_name):
    """
    Generate an image from character description using Hugging Face SDXL.
    
    Args:
        character_description: Description of the character for image generation
        character_name: Name of the character for file naming
    
    Returns:
        Path to saved image or None if generation fails
    """
    try:
        from diffusers import DiffusionPipeline
        import torch
        
        # Create assets directory if it doesn't exist
        os.makedirs("assets/generated", exist_ok=True)
        
        # Use faster pipeline
        pipe = DiffusionPipeline.from_pretrained(
            "stabilityai/sdxl-turbo",
            torch_dtype=torch.float16,
            use_safetensors=True
        )
        
        # Generate prompt from character description
        prompt = f"A detailed fantasy character portrait: {character_description}"
        
        # Generate image
        image = pipe(
            prompt=prompt,
            num_inference_steps=1,
            guidance_scale=0.0
        ).images[0]
        
        # Save image
        filename = f"assets/generated/{character_name.replace(' ', '_')}.png"
        image.save(filename)
        
        return filename
    
    except Exception as e:
        print(f"Error generating image: {e}")
        return None

def create_placeholder_image(character_name):
    """
    Create a placeholder image if generation fails.
    
    Args:
        character_name: Name of the character
    
    Returns:
        Path to placeholder image
    """
    try:
        os.makedirs("assets/generated", exist_ok=True)
        
        # Create a simple placeholder
        img = Image.new('RGB', (512, 512), color=(70, 40, 100))
        filename = f"assets/generated/{character_name.replace(' ', '_')}_placeholder.png"
        img.save(filename)
        
        return filename
    except Exception as e:
        print(f"Error creating placeholder: {e}")
        return None

def get_character_image(character_name):
    """
    Get the image path for a character if it exists.
    
    Args:
        character_name: Name of the character
    
    Returns:
        Path to image if exists, None otherwise
    """
    filename = f"assets/generated/{character_name.replace(' ', '_')}.png"
    if os.path.exists(filename):
        return filename
    return None
