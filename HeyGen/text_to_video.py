import requests
import os

HEYGEN_API_KEY = os.environ["API_KEY_HEYGEN"]


def generate_video(text, avatar_id):
    url = "https://api.heygen.com/v2/video/generate"
    headers = {
        "X-Api-Key": HEYGEN_API_KEY,
        "accept": "application/json",
        "Content-Type": "application/json"
    }
    payload = {
        "caption": False,
        "dimension": {
                "width": 1080,
                "height": 1080
            },
        "video_inputs": [
        { 
            "character": {
                "type": "avatar",
                "scale": 1,
                "avatar_id": avatar_id
            },
            "voice": {
                "type": "text",
                "voice_id": "e1a429dbe823406dbae5fa7c3612314d",
                "input_text": text,
                "emotion":'Excited'
            },
            "background": {
                "type": "color",
                "value": "#f6f6fc"

            }
        }
        ]
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code == 200:
        print("Vidéo créée avec succès :", response.json())
    else:
        print("Erreur :", response.status_code, response.json())


def get_video_status(video_id):
    url = f"https://api.heygen.com/v1/video_status.get?video_id={video_id}"
    headers = {
        "X-Api-Key": HEYGEN_API_KEY
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        print("Statut de la vidéo :", response.json())
        return response.json()
    else:
        print("Erreur :", response.status_code, response.json())
        return None

def recup_voix():
    url = "https://api.heygen.com/v2/voices"

    headers = {
        "accept": "application/json",
        "x-api-key": os.environ["API_KEY_HEYGEN"]
    }

    response = requests.get(url, headers=headers)

    print(response.text)

def recup_avatar():
    import requests

    url = "https://api.heygen.com/v2/avatars"

    headers = {
        "accept": "application/json",
        "x-api-key": os.environ["API_KEY_HEYGEN"]
    }

    response = requests.get(url, headers=headers)

    print(response.text)
