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
import random

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


def generate_text(subject: str,nb : int):
    
    prompt = f"""You're an expert in generating speech for TikTok videos. So do not be formal, be funny!
    Your job will be to generate the text for a TikTok video which will tell the story of a funny date 
    that took in place in a {subject}.
    You have to give the point of view of the date of Eva and the point of view of Mike knowing it's their date number {nb}, 
    it should take 30 seconds to read for each.
    You have to start with something that will keep the followers watching.
    You have to end with a sentence that tells the listeners to suscribe if they want to know the other point of view.
   
    Give me the result in a JSON format with both texts and the hashtags I have to put for the videos.
    Do not answer anything else than the JSON with this format : "text_Eva" :...,"text_Mike" :... and  "hashtags : ... """
    
    try:
        # Call the create_subject function to get the response
        response_text = create_subject(prompt, print_infos=False)

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
    print("\n")
    return urlreturn


def create_audio(input_text, output_path,client = None):
    if client is None:
        client = OpenAI(api_key=os.environ["API_KEY_OPENAI"])
    voice = choisir_voix()
    response = client.audio.speech.create(
        model="tts-1",
        voice=voice,
        input=input_text
    )
    response.write_to_file(output_path)
    return voice

def choisir_voix():
    """
    Choisit une voix adaptée random
    :return: Nom de la voix recommandée.
    """
    #"ash", "coral","sage"
    voices = ["echo" , "alloy", "onyx", "nova", "fable"]
    return random.choice(voices)
    
    return voix

def creer_avatar(nb,input_text, output_path,url,Character):
        #API_KEY = os.environ["API_KEY_HEYGEN"]
        API_KEYS = [
            "NjhmYjdkNjJjMjc4NDE2OGFjMTg3MTY3NTk2MjFmMGUtMTczODE5NDE2NQ==",
            "N2M3NjUyOTNjODU5NGRjODg3Nzg3MTk1ZWU4ODAxZmEtMTczODE5NDI0Mw==",
            "Njk5MDhmMGEwMTliNGExMWJhZGU5Zjg5MTg2N2ZkMWUtMTczODE5NDMyMw=="
        ]
        API_KEY = API_KEYS[0]
        if(nb>=12 and nb<16):
            API_KEY = API_KEYS[1]
        elif(nb>=16):
            API_KEY = API_KEYS[2]
            
        if(Character=="Eva"):
            avatar_id="Imelda_Casual_Side_public"
            voix="c4313f9f0b214a7a8189c134736ce897"
        else:
            avatar_id= "nik_blue_expressive_20240910"
            voix="76d38d2180e74bf29baf916be2578bac"
        # 1. Envoyer la requête pour générer la vidéo
        url_generate = "https://api.heygen.com/v2/video/generate"
        payload = {
            "caption": False,
            "title": "Avatar Video",
            "callback_id": "test_callback",
            "dimension": {
                "width": 1280,
                "height": 720
            },
            "video_inputs": [
                {
                    "character": {
                        "type": "avatar",
                        "avatar_id": avatar_id,
                        "scale": 1,
                        "avatar_style": "normal",
                        "offset": {"x": 0, "y": 0}
                    },
                    "voice": {
                        "type": "text",
                        "voice_id": voix,
                        "input_text": input_text,
                        "emotion": 'Excited'
                    },
                    "background": {
                        "type": "image",
                        "url": url
                    }
                }
            ],
        }
        
        headers = {
            "accept": "application/json",
            "content-type": "application/json",
            "x-api-key": API_KEY
        }

        response = requests.post(url_generate, json=payload, headers=headers)
        
        if response.status_code != 200:
            print("Erreur lors de la génération de la vidéo:", response.text)
            return

        response_data = response.json()
        video_id = response_data.get("data", {}).get("video_id")  # Récupération correcte de l'ID
        
        if not video_id:
            print("Erreur : Impossible de récupérer l'ID de la vidéo.")
            return

        print(f"Vidéo en cours de génération... ID: {video_id}")

        # 2️⃣ Vérifier le statut de la vidéo
        url_check_status = "https://api.heygen.com/v1/video_status.get"
        while True:
            response_status = requests.get(url_check_status, headers=headers, params={"video_id": video_id})
            
            if response_status.status_code == 400:
                print(" Erreur 400 : Requête incorrecte, l'ID vidéo est peut-être invalide.")
                return
            elif response_status.status_code != 200:
                print(" Erreur lors de la récupération du statut:", response_status.text)
                return

            status_data = response_status.json()
            video_status = status_data.get("data", {}).get("status")
            video_url = status_data.get("data", {}).get("video_url")

            if video_status == "completed":
                print(f" Vidéo prête ! URL: {video_url}")
                break
            elif video_status == "failed":
                print(" La génération de la vidéo a échoué.")
                return
            else:
                print(f" Statut : {video_status}... Patientez.")
                time.sleep(30)  # Attente de 10 secondes avant de re-vérifier

        # 3 Télécharger la vidéo
        if video_url:
            video_response = requests.get(video_url)

            if video_response.status_code == 200:
                with open(output_path, "wb") as f:
                    f.write(video_response.content)
                print(f" Vidéo téléchargée avec succès dans : {output_path}")
            else:
                print(" Erreur lors du téléchargement de la vidéo.")
        else:
            print(" Aucun lien de vidéo disponible après le rendu.")


    
