import random
from itertools import product

from belief_base import BeliefBase, Atom, Negation
from logicalEntailment import entails
from belief_revision_agent import expand

COLORS = [1, 2, 3, 4, 5, 6]
CODE_LENGTH = 4


def pos_atom(pos, color):
    return Atom(f"p{pos}_{color}")


def get_feedback(secret, guess):
    blacks = sum(s == g for s, g in zip(secret, guess))
    whites = sum(min(secret.count(c), guess.count(c)) for c in COLORS) - blacks
    return blacks, whites


def all_codes():
    return list(product(COLORS, repeat=CODE_LENGTH))


def build_candidate_bb(code):
    bb = BeliefBase()
    for pos, color in enumerate(code):
        bb.beliefs.append((pos_atom(pos, color), 1))
        for other in COLORS:
            if other != color:
                bb.beliefs.append((Negation(pos_atom(pos, other)), 1))
    return bb


def candidate_consistent(bb, code):
    if bb.is_empty():
        return True
    code_bb = build_candidate_bb(code)
    for belief in bb.get_beliefs():
        if entails(code_bb, Negation(belief)):
            return False
    return True


def learn_from_feedback(bb, guess, blacks, whites, priority):
    # blacks = 4: perfect match — all positions known exactly
    if blacks == CODE_LENGTH:
        for pos, color in enumerate(guess):
            bb = expand(bb, pos_atom(pos, color), priority)
        return bb

    # blacks + whites = 0: no color in this guess appears in the secret
    if blacks + whites == 0:
        for color in set(guess):
            for pos in range(CODE_LENGTH):
                bb = expand(bb, Negation(pos_atom(pos, color)), priority)
        return bb

    # blacks = 0: every guessed color is in the wrong position
    # so we know ~p{i}_{guess[i]} for each position i
    if blacks == 0:
        for pos, color in enumerate(guess):
            bb = expand(bb, Negation(pos_atom(pos, color)), priority)
        return bb

    return bb


def filter_candidates(candidates, guess, blacks, whites):
    return [c for c in candidates if get_feedback(c, guess) == (blacks, whites)]


def pick_next_guess(candidates, bb):
    for code in candidates:
        if candidate_consistent(bb, code):
            return code
    return None


def play(secret=None, verbose=True):
    if secret is None:
        secret = random.choice(all_codes())

    if verbose:
        print(f"\nSecret code: {list(secret)}")
        print("-" * 40)

    bb = BeliefBase()
    candidates = all_codes()

    # First guess — (1,1,2,2) is a proven strong opening for 4-peg 6-color Mastermind
    guess = (1, 1, 2, 2)

    for attempt in range(1, 11):
        blacks, whites = get_feedback(secret, guess)

        if verbose:
            print(f"Guess {attempt}: {list(guess)}  →  {blacks} black  {whites} white")

        if blacks == CODE_LENGTH:
            if verbose:
                print(f"Solved in {attempt} guess(es)!")
                print(f"Belief base held {bb.size()} fact(s)")
            return attempt

        # Expand belief base with propositional facts from this feedback
        bb = learn_from_feedback(bb, guess, blacks, whites, priority=attempt)

        # Filter candidates — eliminate codes that can't be the secret
        candidates = filter_candidates(candidates, guess, blacks, whites)

        if verbose:
            print(f"  Belief base: {bb.size()} fact(s) | Candidates remaining: {len(candidates)}")

        guess = pick_next_guess(candidates, bb)

        if guess is None:
            if verbose:
                print("No valid guess found.")
            return -1

    if verbose:
        print("Failed to solve within 10 guesses.")
    return -1


if __name__ == "__main__":
    print("=" * 50)
    print("  MASTERMIND — AGM Belief Revision Code-Breaker")
    print("  (Group 45)")
    print("=" * 50)

    print("\n--- Demo 1: secret = [3, 1, 4, 2] ---")
    play(secret=(3, 1, 4, 2))

    print("\n--- Demo 2: secret = [6, 6, 6, 6] ---")
    play(secret=(6, 6, 6, 6))

    print("\n--- Demo 3: random secret ---")
    play()

    print("\n--- Performance test: 100 random games ---")
    results = []
    for _ in range(100):
        secret = random.choice(all_codes())
        r = play(secret=secret, verbose=False)
        results.append(r)

    solved = [r for r in results if r > 0]
    dist = dict(sorted({g: solved.count(g) for g in set(solved)}.items()))

    print(f"Solved:          {len(solved)}/100")
    print(f"Average guesses: {sum(solved)/len(solved):.2f}")
    print(f"Max guesses:     {max(solved)}")
    print(f"Distribution:    {dist}")
