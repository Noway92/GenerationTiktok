import classes.APIs as APIs

class Speech():
    def __init__(self, subject:str, nb:int):
        self.subject = subject
        self.text = APIs.generate_text(subject,nb)
        self.Mike_view = self.text["text_Mike"]
        self.Eva_view = self.text["text_Eva"]
    
    def __str__(self):
        return (f"Speech about '{self.subject}':\n"
                f"Full Mike's History: {self.Mike_view}\n"
                f"Full Eva's History: {self.Eva_view}\n"
                f"Hashtags : {self.text['hashtags']}\n" )