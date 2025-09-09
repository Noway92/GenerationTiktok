import numpy as np
import matplotlib.pyplot as plt
import os
import re
import json
import base64
from PIL import Image
from io import BytesIO
import time
import requests
from openai import OpenAI

def create_subject(input_text, print_infos=False, client=None):
    if client is None:
        
        client = OpenAI(api_key=os.environ["API_KEY_OPENAI"])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "user", 
                "content": input_text
            }
        ]
    )
    
    if print_infos:
        print(response.choices[0].message.content)
    
    results = response.choices[0].message.content
    # On test si c'est bien un string
    if not isinstance(results, str):
        raise TypeError(f"Expected a string, but got {type(results).__name__}")
    
    return results


def generate_text(subject: str,):
    prompt = f"""You're an expert in generating speech for TikTok videos. So do not be formal, be funny!
    Your job will be to generate the text for a TikTok video which will tell the creation of {subject}.
    The story should be detailed and long enough to take 45 seconds to be read.
    The intro should be attractive for teenagers 
    The outro should ask the listeners which invention they would like to hear about in the next video.
    the size is in metters (just write the float)
    
    Give me the result in a JSON format with intro, the text, the size_m of {subject}, outro and the hashtags i have to put for the video.
    Do not answer anything else than the JSON."""
    
    try:
        # Call the create_subject function to get the response
        response_text = create_subject(prompt, print_infos=True)

        # Enlever le ''' JSON 
        response_text_json = re.search(r'{.*}', response_text, re.DOTALL).group(0)

        # Parse the response as JSON
        text = json.loads(response_text_json)
        return text
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        return None
    """
    response_text = create_subject(prompt, print_infos=True)
    return response_text
    """
def create_background(input_text, output_path, client = None):
    if client is None:
        client = OpenAI(api_key=os.environ["API_KEY_OPENAI"])
    response = client.images.generate(
    model="dall-e-3",
    response_format = "b64_json",
    prompt=input_text,
    size="1024x1024",
    quality="standard",
    n=1,
    )
        
        

    image_data_b64 = response.data[0].b64_json
    # Décoder les données en base64
    image_data = base64.b64decode(image_data_b64)
    image = Image.open(BytesIO(image_data))
    image.save(output_path)

def create_background_google(input_text, output_path):

    API_KEY=os.environ["API_KEY_GOOGLE"]   
    CX = os.environ["MOTEUR_RECHERCHE_GOOGLE"]

    url = f"https://www.googleapis.com/customsearch/v1"

    # Paramètres de l'API
    params = {
        "q": input_text,         # Terme de recherche
        "cx": CX,                  # ID du moteur de recherche
        "key": API_KEY,            # Clé d'API
        "searchType": "image",     # Recherche d'images
        #"fileType": "png",
        "hl" : "fr",              # Images françaises
        "tbs": "iar:s",           # Image carré
        "num": 10                 # Nombre de résultats (max 10 par requête)
    }

    urlreturn = []
    # Appel API
    response = requests.get(url, params=params)
    # Traitement de la réponse
     # Traitement de la réponse
    if response.status_code == 200:
        results = response.json()
        for i, item in enumerate(results.get("items", [])):
            image_url = item['link']
            image_title = item['title']

            # Vérification du type MIME de l'image
            image_head = requests.head(image_url, allow_redirects=False)
            content_type = image_head.headers.get('Content-Type', '')

            # Vérification si l'image est valide (formats populaires comme jpeg, png, gif)
            if "image" in content_type:
                # Télécharger l'image si elle est valide
                image_data = requests.get(image_url).content
                    
                # Définir le chemin du fichier (avec un numéro pour éviter les conflits de nom)
                image_path = os.path.join(output_path, f"image_{i+1}.png")

                # Sauvegarder l'image dans le répertoire spécifié
                with open(image_path, 'wb') as file:
                    
                    file.write(image_data)

                print(f"Image '{image_title}' téléchargée et enregistrée sous {image_path}")
                urlreturn.append(image_url)
            else:
                print(f"L'image '{image_title}' n'est pas compatible (format non valide). Ignorée.")
    else:
        print(f"Erreur: {response.status_code}, {response.text}")

    return urlreturn

def create_video_google(input_text, output_path):

    API_KEY=os.environ["API_KEY_GOOGLE"]   
    CX = os.environ["MOTEUR_RECHERCHE_GOOGLE"]

    url = f"https://www.googleapis.com/customsearch/v1"

    # Paramètres de l'API
    params = {
        "q": input_text,         # Terme de recherche
        "cx": CX,                  # ID du moteur de recherche
        "key": API_KEY,            # Clé d'API
        "searchType": "video",     # Recherche d'images
        #"fileType": "png",
        "hl" : "fr",              # Images françaises
        "tbs": "iar:s",           # Image carré
        "num": 10                 # Nombre de résultats (max 10 par requête)
    }

    urlreturn = []
    # Appel API
    response = requests.get(url, params=params)
    # Traitement de la réponse
     # Traitement de la réponse
    if response.status_code == 200:
        results = response.json()
        for i, item in enumerate(results.get("items", [])):
            image_url = item['link']
            image_title = item['title']

            # Vérification du type MIME de l'image
            image_head = requests.head(image_url, allow_redirects=False)
            content_type = image_head.headers.get('Content-Type', '')

            # Vérification si l'image est valide (formats populaires comme jpeg, png, gif)
            if "image" in content_type:
                # Télécharger l'image si elle est valide
                image_data = requests.get(image_url).content
                    
                # Définir le chemin du fichier (avec un numéro pour éviter les conflits de nom)
                image_path = os.path.join(output_path, f"image_{i+1}.png")

                # Sauvegarder l'image dans le répertoire spécifié
                with open(image_path, 'wb') as file:
                    
                    file.write(image_data)

                print(f"Image '{image_title}' téléchargée et enregistrée sous {image_path}")
                urlreturn.append(image_url)
            else:
                print(f"L'image '{image_title}' n'est pas compatible (format non valide). Ignorée.")
    else:
        print(f"Erreur: {response.status_code}, {response.text}")

    return urlreturn


def create_audio(input_text, output_path,size = None ,client = None):
    if client is None:
        client = OpenAI(api_key=os.environ["API_KEY_OPENAI"])
    voice = choisir_voix(size)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=input_text
    )
    response.write_to_file(output_path)
    return voice

def choisir_voix(size_m):
    """
    Choisit une voix adaptée en fonction de la taille de l'objet en mètres.

    :param size_m: Taille de l'objet en mètres.
    :return: Nom de la voix recommandée.
    """
    if(size_m is None):
        return "shimmer"
    
    size_m = float(size_m) 
    if size_m < 1:
        return "echo"
    elif size_m < 3:
        return "echo"#"ash"
    elif size_m < 5:
        return "alloy"
    elif size_m < 10:
        return "onyx"
    elif size_m < 15:
        return "nova"#"coral"
    elif size_m < 20:
        return "nova"
    elif size_m < 25:
        return "fable"
    else:
        return "fable"#"sage"
    
    return voix
    
