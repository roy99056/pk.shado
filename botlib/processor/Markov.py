
import markovify
import os


class Markov():
    def __init__(self):
        self.text_model = self.load_brain()


    def add_to_brain(self, msg):
        f = open('training_text.txt', 'a')
        f.write(str(msg) + '\n')
        f.close()

    def generate_sentence(self):
        return self.text_model.make_short_sentence(300)

    def load_brain(self):
        if os.path.exists('training_text.txt'):
            with open("training_text.txt") as f:
                text = f.read()
            print('Brain Reloaded')
            f.close()
            return markovify.NewlineText(text)

