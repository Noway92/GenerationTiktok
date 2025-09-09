from text_to_video import generate_video
from text_to_video import get_video_status
import time
import requests
import os

# page avatar https://docs.heygen.com/page/tools
# Fonctionne : 

list_id_work = [
    "Jin_Vest_Front_public", # pas de fond
    "Brent_sitting_office_front", # il y a un fond
    "Masha_sitting_sofacasual_front", # il y a un fond
    "nik_blue_expressive_20240910", # Pas de fond oui
    "Imelda_Casual_Side_public", # pas de fond  oui

]

list_id = [
    "Abigail_sitting_sofa_side","c4313f9f0b214a7a8189c134736ce897"
    "Imelda_Casual_Side_public","3193b827155a485c9ba08adc05a4a509"  # oui
    "Masha_sitting_sofacasual_front","72a90016199b4a31bd6d8a003eef8ee2"
    "nik_blue_expressive_20240910","76d38d2180e74bf29baf916be2578bac" # oui
    "Byron_Casual_Sitting_Side_public","e1a429dbe823406dbae5fa7c3612314d"
]

text = "Yo gamers! Ever wondered how the chaotic world of Fortnite came to be? Buckle up because this wild ride is about to get a whole lot crazier than your friend’s dance moves at a wedding! So, picture this: it was 2011, and a bunch of super nerds at Epic Games gathered around. They were brainstorming ideas like it was the last slice of pizza at a party. Suddenly, someone shouted, 'Hey! What if we threw zombies AND building into a blender?!' And thus, Fortnite was born, like a weird science experiment gone right. But it wasn’t an instant hit! In fact, the first Fortnite was more like a quiet library than a wild party. Then in 2017, they dropped the Battle Royale mode, and BOOM! It exploded like a piñata at a birthday bash! Teens swapped homework for victory dances, and everyone suddenly became a pro builder, crafting forts faster than I can find my other shoe! Now, we’ve got Fortnite kids dancing in the streets and forming squads like they’re planning world domination – all thanks to a group of devs that just wanted to have some fun! Can you imagine explaining to a caveman that people would be smashing their buttons to outbuild each other while doing the floss? Mind-blown! So, tell me—what crazy invention do you want to hear about next? Leave a comment and let’s keep this brain party poppin’!"
text = "I am just trying to make a video. Please could you work or i will cry"
if __name__ == "__main__":
    #generate_video(text, input_avatar_id)

    def creer_avatar(input_text, output_path):
        API_KEY = os.environ["API_KEY_HEYGEN"]

        # 1. Envoyer la requête pour générer la vidéo
        url_generate = "https://api.heygen.com/v2/video/generate"
        payload = {
            "caption": True,
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
                        "avatar_id": "nik_blue_expressive_20240910",
                        "scale": 1,
                        "avatar_style": "normal",
                        "offset": {"x": 0, "y": 0}
                    },
                    "voice": {
                        "type": "text",
                        "voice_id": "76d38d2180e74bf29baf916be2578bac",
                        "input_text": input_text,
                        "emotion": 'Excited'
                    },
                    "background": {
                        "type": "image",
                        "url": "https://images.wondershare.com/repairit/aticle/2021/08/png-jpg-or-jpeg-2.jpg"
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
            video_url = status_data.get("data", {}).get("video_url_caption")

            if video_status == "completed":
                print(f" Vidéo prête ! URL: {video_url}")
                break
            elif video_status == "failed":
                print(" La génération de la vidéo a échoué.")
                return
            else:
                print(f" Statut : {video_status}... Patientez.")
                time.sleep(10)  # Attente de 10 secondes avant de re-vérifier

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

    # Exemple d'utilisation :
    creer_avatar("Bonjour, ceci est un test.", "output_video.mp4")



        