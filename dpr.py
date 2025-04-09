import argparse
import re
import random

def average_damage(dice_str):
    dice_parts = re.findall(r'(\d+)d(\d+)', dice_str)
    modifier = 0

    # Remove dice parts from the string and evaluate the rest as flat modifiers
    cleaned = re.sub(r'\d+d\d+', '', dice_str)
    mod_parts = re.findall(r'[+-]?\d+', cleaned)
    modifier = sum(int(m) for m in mod_parts)

    total = 0
    for count, die in dice_parts:
        count = int(count)
        die = int(die)
        total += count * (die + 1) / 2

    return total + modifier


def average_crit_damage(dice_str):
    dice_parts = re.findall(r'(\d+)d(\d+)', dice_str)
    modifier = 0

    # Remove dice parts from the string and evaluate the rest as flat modifiers
    cleaned = re.sub(r'\d+d\d+', '', dice_str)
    mod_parts = re.findall(r'[+-]?\d+', cleaned)
    modifier = sum(int(m) for m in mod_parts)

    total = 0
    for count, die in dice_parts:
        count = int(count) * 2  # double the dice for crit
        die = int(die)
        total += count * (die + 1) / 2

    return total + modifier



def hit_chance(attack_bonus, target_ac, advantage=False, disadvantage=False):
    """Compute chance to hit (excluding crits), factoring in 1s, 20s, and advantage/disadvantage."""
    def roll_chance(threshold):
        # Counts how many d20 results hit AC (not including nat 20, which is always hit+crit)
        hits = sum(1 for roll in range(2, 20) if roll + attack_bonus >= target_ac)
        return hits / 20

    def with_advantage(threshold):
        return sum(
            1 for d1 in range(1, 21)
              for d2 in range(1, 21)
              if max(d1, d2) >= threshold and max(d1, d2) != 1
        ) / 400

    def with_disadvantage(threshold):
        return sum(
            1 for d1 in range(1, 21)
              for d2 in range(1, 21)
              if min(d1, d2) >= threshold and min(d1, d2) != 1
        ) / 400

    needed = target_ac - attack_bonus
    needed = max(2, min(20, needed))  # Clamp between 2 and 20

    if advantage:
        hit = with_advantage(needed)
    elif disadvantage:
        hit = with_disadvantage(needed)
    else:
        hit = roll_chance(needed)

    return hit

def crit_chance(advantage=False, disadvantage=False):
    """5% base chance, adjusted for adv/disadv."""
    if advantage:
        return 1 - ((19 / 20) ** 2)  # chance at least one die is 20
    elif disadvantage:
        return 1 / 400  # both dice must be 20
    else:
        return 1 / 20

def expected_damage_per_round(attack_bonus, target_ac, damage_str, num_attacks=1, advantage=False, disadvantage=False):
    normal_avg = average_damage(damage_str)
    crit_avg = average_crit_damage(damage_str)

    crit = crit_chance(advantage, disadvantage)
    hit = hit_chance(attack_bonus, target_ac, advantage, disadvantage) - crit  # remove crits from hits

    expected = num_attacks * (
        hit * normal_avg +
        crit * crit_avg
    )
    return round(expected, 2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Calculate expected DPR in D&D 5e")
    parser.add_argument("--attack_bonus", type=int, required=True, help="Attack modifier (e.g. 6)")
    parser.add_argument("--target_ac", type=int, required=True, help="Target Armor Class (e.g. 18)")
    parser.add_argument("--damage", type=str, required=True, help="Damage expression (e.g. 1d8+2)")
    parser.add_argument("--num_attacks", type=int, default=1, help="Number of attacks per round")

    adv_group = parser.add_mutually_exclusive_group()
    adv_group.add_argument("--advantage", action="store_true", help="Rolls made with advantage")
    adv_group.add_argument("--disadvantage", action="store_true", help="Rolls made with disadvantage")

    args = parser.parse_args()

    dpr = expected_damage_per_round(
        attack_bonus=args.attack_bonus,
        target_ac=args.target_ac,
        damage_str=args.damage,
        num_attacks=args.num_attacks,
    )

    dpra = expected_damage_per_round(
        attack_bonus=args.attack_bonus,
        target_ac=args.target_ac,
        damage_str=args.damage,
        num_attacks=args.num_attacks,
        advantage=True,
        disadvantage=False
    )

    dprd = expected_damage_per_round(
        attack_bonus=args.attack_bonus,
        target_ac=args.target_ac,
        damage_str=args.damage,
        num_attacks=args.num_attacks,
        advantage=False,
        disadvantage=True
    )

    print(f"Expected DPR-a: {dpra:.2f}")
    print(f"Expected DPR: {dpr:.2f}")
    print(f"Expected DPR-d: {dprd:.2f}")

    # dpr = expected_damage_per_round(
    #     attack_bonus=args.attack_bonus,
    #     target_ac=args.target_ac,
    #     damage_str=args.damage,
    #     num_attacks=args.num_attacks,
    #     advantage=args.advantage,
    #     disadvantage=args.disadvantage
    # )

    # print(f"Expected DPR: {dpr:.2f}")

