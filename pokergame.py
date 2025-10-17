import random
from itertools import combinations
from collections import Counter
import sys

#!/usr/bin/env python3
# Simple, fast Texas Hold'em showdown for 2-9 players (CLI)
# Save as untitled_poker.py and run with Python 3


RANKS = list(range(2, 15))  # 2..14 (14 is Ace)
RANK_TO_STR = {14: "A", 13: "K", 12: "Q", 11: "J", 10: "T",
               9: "9", 8: "8", 7: "7", 6: "6", 5: "5", 4: "4", 3: "3", 2: "2"}
SUITS = ["♠", "♥", "♦", "♣"]
HAND_NAMES = {
    9: "Straight Flush",
    8: "Four of a Kind",
    7: "Full House",
    6: "Flush",
    5: "Straight",
    4: "Three of a Kind",
    3: "Two Pair",
    2: "One Pair",
    1: "High Card",
}


class Card:
    __slots__ = ("rank", "suit")

    def __init__(self, rank, suit):
        self.rank = rank
        self.suit = suit

    def __repr__(self):
        return f"{RANK_TO_STR[self.rank]}{self.suit}"


class Deck:
    def __init__(self):
        self.cards = [Card(r, s) for r in RANKS for s in SUITS]
        random.shuffle(self.cards)

    def deal(self, n=1):
        return [self.cards.pop() for _ in range(n)]


def is_straight(ranks):
    # ranks is list of ints, may contain duplicates
    s = sorted(set(ranks))
    if len(s) < 5:
        return (False, None)
    # check normal straights by sliding window on sorted unique ranks
    for i in range(len(s) - 4):
        window = s[i:i + 5]
        if window[-1] - window[0] == 4:
            return True, window[-1]
    # check wheel A-2-3-4-5
    if set([14, 2, 3, 4, 5]).issubset(s):
        return True, 5
    return False, None


def evaluate_5(cards):
    # cards: list of 5 Card objects
    ranks = [c.rank for c in cards]
    suits = [c.suit for c in cards]
    counts = Counter(ranks)
    counts_by_freq = sorted(((freq, rank) for rank, freq in counts.items()), reverse=True)
    freqs = sorted(counts.values(), reverse=True)
    is_flush = len(set(suits)) == 1
    straight, top_straight = is_straight(ranks)

    # Straight flush
    if is_flush and straight:
        return (9, top_straight)

    # Four of a Kind
    if freqs[0] == 4:
        four_rank = counts_by_freq[0][1]
        kicker = max(r for r in ranks if r != four_rank)
        return (8, four_rank, kicker)

    # Full House
    if freqs[0] == 3 and freqs[1] == 2:
        three_rank = counts_by_freq[0][1]
        pair_rank = counts_by_freq[1][1]
        return (7, three_rank, pair_rank)

    # Flush
    if is_flush:
        return (6, sorted(ranks, reverse=True))

    # Straight
    if straight:
        return (5, top_straight)

    # Three of a Kind
    if freqs[0] == 3:
        three_rank = counts_by_freq[0][1]
        kickers = sorted((r for r in ranks if r != three_rank), reverse=True)
        return (4, three_rank, kickers)

    # Two Pair
    if freqs[0] == 2 and freqs[1] == 2:
        pair_ranks = sorted([r for r, f in counts.items() if f == 2], reverse=True)
        kicker = max(r for r in ranks if counts[r] == 1)
        return (3, pair_ranks[0], pair_ranks[1], kicker)

    # One Pair
    if freqs[0] == 2:
        pair_rank = counts_by_freq[0][1]
        kickers = sorted((r for r in ranks if r != pair_rank), reverse=True)
        return (2, pair_rank, kickers)

    # High Card
    return (1, sorted(ranks, reverse=True))


def best_hand(seven_cards):
    # generate all 5-card combos and pick the best evaluation
    best = None
    best_combo = None
    for combo in combinations(seven_cards, 5):
        val = evaluate_5(combo)
        if best is None or val > best:
            best = val
            best_combo = combo
    return best, best_combo


def show_cards(cards):
    return " ".join(map(str, cards))


def main():
    # CLI quick setup
    try:
        arg = sys.argv[1]
        num_players = int(arg)
    except Exception:
        try:
            num_players = int(input("Number of players (2-9) [4]: ") or 4)
        except Exception:
            num_players = 4
    num_players = max(2, min(9, num_players))

    deck = Deck()
    players = {f"P{idx+1}": deck.deal(2) for idx in range(num_players)}
    # burn + flop + burn + turn + burn + river (we won't model burns explicitly, just deal community)
    community = deck.deal(3) + deck.deal(1) + deck.deal(1)

    print("\n--- Texas Hold'em showdown ---")
    for name, hole in players.items():
        print(f"{name}: {show_cards(hole)}")

    print(f"\nCommunity: {show_cards(community)}\n")

    results = {}
    for name, hole in players.items():
        seven = hole + community
        score, combo = best_hand(seven)
        results[name] = (score, combo)

    # find winner(s)
    best_score = max(score for score, combo in results.values())
    winners = [p for p, (score, combo) in results.items() if score == best_score]

    # print per-player best hands
    for name, (score, combo) in results.items():
        hname = HAND_NAMES[score[0]] if isinstance(score, tuple) else HAND_NAMES[score]
        # score may be tuple; the first element is category id
        cat = score[0] if isinstance(score, tuple) else score
        print(f"{name}: Best = {show_cards(combo)}  -> {HAND_NAMES[cat]}  (score={score})")

    print("\nWinner(s): " + ", ".join(winners))
    print("Good luck and have fun.")


if __name__ == "__main__":
    main()