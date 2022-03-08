#!/usr/bin/env python
# -*- coding: utf-8 -*-

# -----------------
# Реализуйте функцию best_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. У каждой карты есть масть(suit) и
# ранг(rank)
# Масти: трефы(clubs, C), пики(spades, S), червы(hearts, H), бубны(diamonds, D)
# Ранги: 2, 3, 4, 5, 6, 7, 8, 9, 10 (ten, T), валет (jack, J), дама (queen, Q), король (king, K), туз (ace, A)
# Например: AS - туз пик (ace of spades), TH - дестяка черв (ten of hearts), 3C - тройка треф (three of clubs)

# Задание со *
# Реализуйте функцию best_wild_hand, которая принимает на вход
# покерную "руку" (hand) из 7ми карт и возвращает лучшую
# (относительно значения, возвращаемого hand_rank)
# "руку" из 5ти карт. Кроме прочего в данном варианте "рука"
# может включать джокера. Джокеры могут заменить карту любой
# масти и ранга того же цвета, в колоде два джокерва.
# Черный джокер '?B' может быть использован в качестве треф
# или пик любого ранга, красный джокер '?R' - в качестве черв и бубен
# любого ранга.

# Одна функция уже реализована, сигнатуры и описания других даны.
# Вам наверняка пригодится itertools.
# Можно свободно определять свои функции и т.п.
# -----------------
from collections import Counter

RANKS_MAPPING = {
    "2": 2,
    "3": 3,
    "4": 4,
    "5": 5,
    "6": 6,
    "7": 7,
    "8": 8,
    "9": 9,
    "T": 10,
    "J": 11,
    "Q": 12,
    "K": 13,
    "A": 14,
}


def get_card_rank(str_card):
    """Возвращает ранг переданной карты"""
    return RANKS_MAPPING.get(str_card[0])


def get_card_suit(str_card):
    """Возвращает масть переданной карты"""
    return str_card[1]


def hand_rank(hand):
    """Возвращает значение определяющее ранг 'руки'"""
    ranks = card_ranks(hand)
    if straight(ranks) and flush(hand):
        return (8, max(ranks))
    elif kind(4, ranks):
        return (7, kind(4, ranks), kind(1, ranks))
    elif kind(3, ranks) and kind(2, ranks):
        return (6, kind(3, ranks), kind(2, ranks))
    elif flush(hand):
        return (5, ranks)
    elif straight(ranks):
        return (4, max(ranks))
    elif kind(3, ranks):
        return (3, kind(3, ranks), ranks)
    elif two_pair(ranks):
        return (2, two_pair(ranks), ranks)
    elif kind(2, ranks):
        return (1, kind(2, ranks), ranks)
    else:
        return (0, ranks)


def card_ranks(hand):
    """Возвращает список рангов (его числовой эквивалент),
    отсортированный от большего к меньшему"""
    sorted_ranks = sorted(map(lambda x: get_card_rank(x), hand))
    return sorted_ranks


def flush(hand):
    """Возвращает True, если все карты одной масти"""
    return all([get_card_suit(x) == get_card_suit(hand[0]) for x in hand])


def straight(ranks):
    """Возвращает True, если отсортированные ранги формируют последовательность 5ти,
    где у 5ти карт ранги идут по порядку (стрит)"""
    return all([x - ranks[0] == i for i, x in enumerate(ranks)])


def kind(n, ranks):
    """Возвращает первый ранг, который n раз встречается в данной руке.
    Возвращает None, если ничего не найдено"""
    cnt = Counter(ranks)
    return next((item for item in ranks if cnt[item] == n), None)


def two_pair(ranks):
    """Если есть две пары, то возвращает два соответствующих ранга,
    иначе возвращает None"""
    cnt = Counter(ranks)
    pairs = dict((key, value) for key, value in cnt.items() if value >= 2)

    if len(pairs) == 2:
        return list(pairs.keys())

    return None


def best_hand(hand):
    """Из "руки" в 7 карт возвращает лучшую "руку" в 5 карт"""
    hand_rank(hand)
    return


def best_wild_hand(hand):
    """best_hand но с джокерами"""
    return


def test_two_pair():
    print("two_pair")
    res1 = two_pair([2, 2, 3, 4, 4])
    res2 = two_pair([2, 2, 2, 4, 4])
    res3 = two_pair([2, 3, 2, 8, 4])
    res4 = two_pair([2, 3, 6, 8, 8])

    assert res1 == [2, 4]
    assert res2 == [2, 4]
    assert res3 is None
    assert res4 is None

    print("OK")


def test_kind():
    print("test_kind")
    res1 = kind(3, [2, 2, 3, 4, 2])
    res2 = kind(2, [4, 2, 3, 4, 2])
    res3 = kind(3, [4, 2, 3, 4, 2])
    res4 = kind(1, [7, 2, 3, 5, 6])

    assert res1 == 2
    assert res2 == 4
    assert res3 is None
    assert res4 == 7

    print("OK")


def test_flush():
    print("test_flush")
    res1 = flush("6C 7C 8C 9C TC".split())
    res2 = flush("6C 7S 8C 9C TC".split())
    res3 = flush("6H 7S 8C 9D TC".split())

    assert res1 is True
    assert res2 is False
    assert res3 is False
    print("OK")


def test_straight():
    print("test_straight")
    res1 = straight([5, 6, 7, 8, 9])
    res2 = straight([5, 6, 7, 9, 9])
    res3 = straight([5, 5, 7, 8, 9])
    res4 = straight([5, 6, 6, 8, 9])
    res5 = straight([5, 5, 5, 5, 5])

    assert res1 is True
    assert res2 is False
    assert res3 is False
    assert res4 is False
    assert res5 is False

    print("OK")


def test_card_ranks():
    print("test_card_ranks...")
    ranks = card_ranks("6C 9C TC 5C JS".split())
    assert ranks == [5, 6, 9, 10, 11]
    print("OK")


def test_card_getters():
    print("test_card_getters...")
    r1 = get_card_rank("7C")
    s1 = get_card_suit("7C")
    r2 = get_card_rank("KD")
    s2 = get_card_suit("KD")
    assert r1 == 7
    assert s1 == "C"
    assert r2 == 13
    assert s2 == "D"
    print("OK")


def test_best_hand():
    print("test_best_hand...")
    assert sorted(best_hand("6C 7C 8C 9C TC 5C JS".split())) == [
        "6C",
        "7C",
        "8C",
        "9C",
        "TC",
    ]
    assert sorted(best_hand("TD TC TH 7C 7D 8C 8S".split())) == [
        "8C",
        "8S",
        "TC",
        "TD",
        "TH",
    ]
    assert sorted(best_hand("JD TC TH 7C 7D 7S 7H".split())) == [
        "7C",
        "7D",
        "7H",
        "7S",
        "JD",
    ]
    print("OK")


def test_best_wild_hand():
    print("test_best_wild_hand...")
    assert sorted(best_wild_hand("6C 7C 8C 9C TC 5C ?B".split())) == [
        "7C",
        "8C",
        "9C",
        "JC",
        "TC",
    ]
    assert sorted(best_wild_hand("TD TC 5H 5C 7C ?R ?B".split())) == [
        "7C",
        "TC",
        "TD",
        "TH",
        "TS",
    ]
    assert sorted(best_wild_hand("JD TC TH 7C 7D 7S 7H".split())) == [
        "7C",
        "7D",
        "7H",
        "7S",
        "JD",
    ]
    print("OK")


if __name__ == "__main__":
    # test_best_hand()
    # test_best_wild_hand()
    test_card_getters()
    test_card_ranks()
    test_straight()
    test_flush()
    test_kind()
    test_two_pair()
