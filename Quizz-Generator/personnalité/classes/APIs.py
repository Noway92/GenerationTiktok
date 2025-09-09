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
    Your job will be to generate the text for a TikTok video which will tell the story of {subject}.
    The story should be detailed and long enough to take 45 seconds to be read.
    
    Can you give me a JSON object with the text, the gender and the age of {subject}
    Do not answer anything else than the JSON.

    Give me the result in a JSON format with intro, the text, the gender,the age of {subject}, outro and the hashtags i have to put for the video."""
    
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


def create_audio(input_text, output_path,age = None,gender = None ,client = None):
    if client is None:
        client = OpenAI(api_key=os.environ["API_KEY_OPENAI"])
    voice = choisir_voix(gender,age)
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=input_text
    )
    response.write_to_file(output_path)
    return voice

def choisir_voix(gender, age):
    """
    Choisit une voix adaptée en fonction du genre et de l'âge.

    :param genre: Genre de la personne ("male", "female").
    :param age: Âge de la personne (en années).
    :return: Nom de la voix recommandée.
    """
    if(age is None or gender is None):
        return "shimmer"

    int_age = int(age)
    voix_mapping = {
        "enfant": {
            "male": "echo",
            #"female": "coral"
        },
        "adolescent": {
            #"male": "ash",
            "female": "nova"
        },
        "adulte": {
            "male": "alloy",
            "female": "fable"
        },
        "senior": {
            "male": "onyx",
            #"female": "sage"
        }
    }

    # Déterminer la catégorie d'âge
    if int_age < 13:
        categorie_age = "enfant"
    elif 13 <= int_age < 30:
        categorie_age = "adolescent"
    elif 30 <= int_age < 60:
        categorie_age = "adulte"
    else:
        categorie_age = "senior"

    # Obtenir la voix correspondant au genre et à la catégorie d'âge
    voix = voix_mapping.get(categorie_age, {}).get(gender.lower(), "shimmer")
    return voix


def get_transcript(input_path, client = None):
    if client is None:
        client = OpenAI(api_key=os.environ["API_KEY_OPENAI"])
    audio_file = open(input_path, "rb")
    transcript = client.audio.transcriptions.create(
        file=audio_file,
        model="whisper-1",
        response_format="verbose_json",
        timestamp_granularities=["word"]
    )
    return transcript
