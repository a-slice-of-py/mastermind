import random
import itertools
from textwrap import dedent
from collections import Counter
from typing import Optional

class MasterMind:

    def __init__(self, N_SLOTS: int = 4, N_COLORS: int = 6) -> None:
        """Initialize class.

        Args:
            N_SLOTS (int, optional): length of code. Defaults to 4.
            N_COLORS (int, optional): number of distinct available colors. Defaults to 6.
        """

        self.N_COLORS = N_COLORS
        self.N_SLOTS = N_SLOTS

        self.omega = list(itertools.product(range(self.N_COLORS), repeat=self.N_SLOTS))
        self.complement = set(self.omega).difference
        self.memory = set()
        self.turns = []

        self.secret_code = random.choice(self.omega)
        self.user_code = None
        self.trials = 0
        self.history = []
        self.success = False

        colors = ("📕", "📘", "📗", "📒", "📓", "📔")
        # colors = ("🔴", "🔵", "🟢", "🟡", "🟣", "🟤")
        self.colors = colors[:N_COLORS]
        self.secret = '❔'
        self.hints = ("◼️", "◻️")
        self.colors_dict = dict(enumerate(self.colors))
        self.inv_dict = dict((v,k) for k,v in self.colors_dict.items())
        self.possible_hints = []
        for _ in range(self.N_SLOTS + 1):
            self.possible_hints.extend(list(itertools.combinations_with_replacement(self.hints, _)))

    def make_code(self) -> tuple:
        """Generates a code.

        Returns:
            tuple: mastermind code
        """
        return random.choice(list(self.complement(self.memory)))

    def paint(self, number_code: tuple) -> str:
        """Visualize a code through colors

        Args:
            number_code (tuple): code to be colored

        Returns:
            str: Color version of the given code via emoji
        """
        if number_code is None:
            return ''.join(self.N_SLOTS*[self.secret])
        else:
            return ' '.join(
                self.colors_dict.get(number_code[k])
                for k in range(len(number_code))
                )

    def get_hint(self, guess: tuple, versus: Optional[str] = None) -> tuple:
        """Check the submitted code versus another code (secret one by default).

        credits to https://stackoverflow.com/questions/45792466/mastermind-python-coding

        Args:
            guess (tuple): code to be checked
            versus (Optional[str], optional): the groundtruth. Defaults to None.

        Returns:
            Tuple: Corresponding hint, number of right colors in right locations and right colors in wrong locations
        """
        if versus is None:
            versus = self.secret_code
        right_colors = sum((Counter(guess) & Counter(versus)).values())
        right_locations = sum(i==j for i,j in zip(guess, versus))
        return right_locations, right_colors - right_locations

    def translate_hint(self, painted_hint: str) -> tuple:
        """Turns a colored hint into a numerical one

        Args:
            painted_hint (str): the hint to be translated

        Returns:
            tuple: translated numerical hint
        """
        return painted_hint.count(self.hints[0]), painted_hint.count(self.hints[1])

    def memorize(self, code: tuple) -> None:
        """Add to game memory the given code

        Args:
            code (tuple): code to be recorded
        """
        self.trials += 1
        self.memory.add(code)
        self.turns.append(code)

    def user_guess(self, code: tuple) -> None:
        """Submit a user guess and save to game history the hint log

        Args:
            code (tuple): Submitted user guess
        """
        self.memorize(code)
        right_locations, wrong_locations = self.get_hint(code)
        self.history.append(
            f'''
            ## **Turn #{self.trials}**<br>
            ## _Code_: {self.paint(code)}<br>
            ## _Hint_: {''.join((right_locations*self.hints[0], wrong_locations*self.hints[1]))}
            ---
            '''
            )
        if right_locations == self.N_SLOTS:
            self.success = True

    def agent_guess(self) -> None:
        """Submit an agent guess
        """
        guess = self.make_code()
        self.memorize(guess)
        self.history.append(
            dedent(f'''
            ## **Turn #{self.trials}**<br>
            ## _Code_: {self.paint(guess)}
            ''')
            )

    def calculate_win_odds(self) -> float:
        """Calculate win odds for next turn

        Returns:
            float: next turn winning odds
        """
        try:
            return 1.0/len(self.complement(self.memory))
        except ZeroDivisionError:
            return 1.0