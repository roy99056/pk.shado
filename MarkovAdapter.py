from __future__ import unicode_literals
from chatterbot.conversation import Statement
from chatterbot.logic.best_match import BestMatch

from botlib.processor.Markov import Markov


class MarkovAdapter(BestMatch):
    def __init__(self, **kwargs):
        super(MarkovAdapter, self).__init__(**kwargs)

        self.confidence_threshold = kwargs.get('threshold', 0.6)
        self.default_response = kwargs.get(
            'default_response',
            "I'm learning..."
        )

    def process(self, input_statement):
        """
        Return a default response with a high confidence if
        a high confidence response is not known.
        """
        # Select the closest match to the input statement
        confidence, closest_match = self.get(input_statement)

        markov = Markov()
        markov.add_to_brain(input_statement.text)
        # Confidence should be high only if it is less than the threshold
        if confidence < self.confidence_threshold:
            confidence = 1
        else:
            confidence = 0

        if confidence:
            output = markov.generate_sentence()
        else:
            output = None

        if output is None:
            output = self.default_response

        return confidence, Statement(output)