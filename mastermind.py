import random
from itertools import product

from belief_base import BeliefBase, Atom, Negation
from logicalEntailment import entails
from belief_revision_agent import expand, revise

COLORS = [1, 2, 3, 4, 5, 6]
CODE_LENGTH = 4


def pos_atom(pos, color):
    return Atom(f"p{pos}_{color}")


def get_feedback(secret, guess):
    blacks = sum(s == g for s, g in zip(secret, guess))
    whites = sum(min(secret.count(c), guess.count(c)) for c in COLORS) - blacks
    return blacks, whites


def all_codes(): # returns all possible codes, so 6^4 = 1296 codes in total.
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


def _safe_update(bb, phi, priority):
    """
    AGM-correct update: use full revision when phi contradicts existing beliefs,
    plain expansion otherwise.
    """
    if entails(bb, Negation(phi)):
        # New fact contradicts an existing belief — perform full AGM revision.
        return revise(bb, phi, priority)
    # No contradiction: expansion is equivalent to revision (vacuity postulate).
    return expand(bb, phi, priority)


def learn_from_feedback(bb, guess, blacks, whites, priority):
    """
    Four exhaustive cases cover all (blacks, whites) combinations:

    Case 1 — blacks == 4
        Perfect match. Each position's color is now known exactly.
         => Add p{pos}_{color} for every position.

    Case 2 — blacks == 0, whites == 0
        No guessed color appears anywhere in the secret.
         => Add -p{j}_{c} for every position j and every unique guessed color c.

    Case 3 — blacks == 0, whites > 0
        Every guessed color is present in the secret but displaced.
        blacks == 0 guarantees secret[i] ≠ guess[i] for all i, so we can safely 
         =>add -p{pos}_{color} for each (pos, color) pair in the guess.

    Case 4 — blacks > 0 (whites == 0 or whites > 0)
        At least one exact match exists but we cannot determine which positions are correct without additional information.
        The only constraint valid for all blacks > 0 scenarios is the disjunction that at least one guessed position must be an exact match).
    """

    # Case 1: perfect match — record every exact (position, color) pair.
    if blacks == CODE_LENGTH:
        for pos, color in enumerate(guess):
            bb = _safe_update(bb, pos_atom(pos, color), priority)
        return bb

    # Case 2: no guessed color appears in the secret at any position.
    if blacks == 0 and whites == 0:
        for color in set(guess):
            for pos in range(CODE_LENGTH):
                bb = _safe_update(bb, Negation(pos_atom(pos, color)), priority)
        return bb

    # Case 3: blacks == 0, whites > 0 — all guessed colors present but displaced.
    # Since blacks == 0, secret[i] ≠ guess[i] for every i, so each guessed color
    # is definitively absent from its guessed position.
    if blacks == 0:
        for pos, color in enumerate(guess):
            bb = _safe_update(bb, Negation(pos_atom(pos, color)), priority)
        return bb

    # Case 4: blacks > 0 , white >= 0 — at least one exact match exists.
    # We cannot identify WHICH positions are correct, so we add the disjunction: 
    # p{0}_{g[0]} | p{1}_{g[1]} | p{2}_{g[2]} | p{3}_{g[3]}
    disjunction = pos_atom(0, guess[0])
    for pos in range(1, CODE_LENGTH):
        disjunction = disjunction | pos_atom(pos, guess[pos])
    bb = _safe_update(bb, disjunction, priority)
    return bb


def filter_candidates(candidates, guess, blacks, whites):
    # Direct simulation: keep only codes whose feedback matches the observed feedback.
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

    # Opening guess — (1,1,2,2) is a proven strong opening for 4-peg 6-color Mastermind.
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

        # Update the belief base with propositional facts derived from this round's feedback.
        bb = learn_from_feedback(bb, guess, blacks, whites, priority=attempt)

        # Filter candidate list by direct simulation — 
        # The belief-base check in pick_next_guess then eliminates any remaining candidates that are inconsistent with accumulated inferred knowledge.
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


#test
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

    print("\n--- Performance test: 500 random games ---")
    results = []
    for _ in range(500):
        secret = random.choice(all_codes())
        r = play(secret=secret, verbose=False)
        results.append(r)

    solved = [r for r in results if r > 0]
    dist = dict(sorted({g: solved.count(g) for g in set(solved)}.items()))

    print(f"Solved:          {len(solved)}/500")
    print(f"Average guesses: {sum(solved)/len(solved):.2f}")
    print(f"Max guesses:     {max(solved)}")
    print(f"Distribution:    {dist}")
