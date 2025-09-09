import classes.APIs as APIs

class Speech():
    def __init__(self, subject:str):
        self.subject = subject
        self.text = APIs.generate_text(subject)
        self.intro = self.text["intro"]
        self.outro = self.text["outro"]
        self.history = self.text["text"]
    
    def __str__(self):
        return (f"Speech about '{self.subject}':\n"
                f"Introduction: {self.intro}\n"
                f"Outro: {self.outro}\n"
                f"Full Text History: {self.history}\n"
                f"Size : {self.text['size_m']}\n"
                f"Hashtags : {self.text['hashtags']}" )