import json
import math
import uuid
import jsons
import re


# region HELPER FUNCTIONS
def convert_modifier_to_points(modifier):
    """
    Converts a skill modifier to character points
    """
    if modifier <= 2:
        return modifier
    elif modifier <= 4:
        return 2 * modifier
    else:
        return 4 * (modifier - 3) + 8


def expected_value(dice_roll: str) -> float:
    """
    Calculates the expected value of a dice roll of the form XdY or XdY + Z
    """
    mod = 0
    if "+" in dice_roll:
        dice_roll, modifier = dice_roll.split(" + ")
        mod = int(modifier)
    m, n = map(int, dice_roll.split("d"))
    return (m * (n + 1)) / 2 + mod


def hit_mod_to_gurps(hit_mod: int) -> str:
    """
    Converts a hit modifier to a GURPS hit modifier
    """
    dc = 10
    if hit_mod <= 0:
        dc = 9
    elif hit_mod == 1:
        dc = 9
    elif hit_mod == 2:
        dc = 10
    elif hit_mod == 3:
        dc = 10
    elif hit_mod == 4:
        dc = 10
    elif hit_mod == 5:
        dc = 11
    elif hit_mod == 6:
        dc = 11
    elif hit_mod == 7:
        dc = 12
    elif hit_mod == 8:
        dc = 12
    elif hit_mod == 9:
        dc = 13
    elif hit_mod == 10:
        dc = 13
    elif hit_mod == 11:
        dc = 14
    elif hit_mod == 12:
        dc = 15
    elif hit_mod == 13:
        dc = 16
    elif hit_mod == 14:
        dc = 17
    elif hit_mod >= 15:
        dc = 18
    return "DC " + str(dc)


def damage_to_gurps(dmg: float) -> str:
    """
    Converts an expected damage value (float) to the closest GURPS damage value (string dice roll)
    """
    if dmg < 28.571:
        gurpsExpDmg = 0.55 * dmg
    else:
        gurpsExpDmg = 0.25 * dmg + 10

    # returns closest multiple of 3.5 + x to gurpsExpDmg
    x = round(gurpsExpDmg - round(gurpsExpDmg / 3.5) * 3.5)
    if x < 0:
        return str(round(gurpsExpDmg / 3.5)) + "d - " + str(abs(x))
    if x == 0:
        return str(round(gurpsExpDmg / 3.5)) + "d"
    else:
        return str(round(gurpsExpDmg / 3.5)) + "d + " + str(x)


def saving_throws_to_gurps(save_throw: int) -> int:
    """
    Converts a D&D 5e saving throw to a GURPS saving throw
    """
    dc = 0
    if save_throw <= 12:
        dc = 0
    elif save_throw <= 14:
        dc = 1
    elif save_throw <= 16:
        dc = 2
    elif save_throw <= 18:
        dc = 3
    elif save_throw <= 20:
        dc = 4
    elif save_throw > 20:
        dc = 5

    return dc


def convert_to_gurps(description: str) -> str:
    """
    Converts a D&D 5e description to a GURPS description
    """
    # Replace all instances of " advantage" or "Advantage" with " +3" or "+3"
    description = description.replace(" advantage", " +3")
    description = description.replace("Advantage", "+3")

    # Replace all instances of " disadvantage" or "Disadvantage" with " -3" or "-3"
    description = description.replace(" disadvantage", " -3")
    description = description.replace("Disadvantage", "-3")

    # Replace all instances of "constitution saving trow" (ignoring case) with "HT roll"
    description = description.replace("constitution saving throw", "HT roll")
    description = description.replace("Constitution saving throw", "HT roll")
    description = description.replace("Constitution Saving Throw", "HT roll")

    # Replace all instances of "strength saving trow" (ignoring case) with "ST roll"
    description = description.replace("strength saving throw", "ST roll")
    description = description.replace("Strength saving throw", "ST roll")
    description = description.replace("Strength Saving Throw", "ST roll")

    # Replace all instances of "dexterity saving trow" (ignoring case) with "DX roll"
    description = description.replace("dexterity saving throw", "DX roll")
    description = description.replace("Dexterity saving throw", "DX roll")
    description = description.replace("Dexterity Saving Throw", "DX roll")

    # Replace all instances of "wisdom saving trow" (ignoring case) with "Will roll"
    description = description.replace("wisdom saving throw", "WL roll")
    description = description.replace("Wisdom saving throw", "WL roll")
    description = description.replace("Wisdom Saving Throw", "WL roll")

    # Replace all instances of "intelligence saving trow" (ignoring case) with "IQ roll"
    description = description.replace("intelligence saving throw", "IQ roll")
    description = description.replace("Intelligence saving throw", "IQ roll")
    description = description.replace("Intelligence Saving Throw", "IQ roll")

    # Replace all instances of "charisma saving trow" (ignoring case) with "Will roll"
    description = description.replace("charisma saving throw", "WL roll")
    description = description.replace("Charisma saving throw", "WL roll")
    description = description.replace("Charisma Saving Throw", "WL roll")

    # Replace all instances of {@h} with ""
    description = description.replace("{@h}", "")

    # Replace all instances of {@atk mw} with "Melee Weapon Attack,"
    description = description.replace("{@atk mw}", "Melee Weapon Attack,")

    # Replace all instances of {@atk rw} with "Ranged Weapon Attack,"
    description = description.replace("{@atk rw}", "Ranged Weapon Attack,")

    # Replace all instances of "{@condition text}" with text
    pattern = r"\{@condition (.+?)\}"
    description = re.sub(pattern, r"\1", description)

    # Replace all instances of "{@spell text}" with text
    pattern = r"\{@spell (.+?)\}"
    description = re.sub(pattern, r"\1", description)

    # Replace all instances of "X ({@damage YdZ})" or "X ({@damage YdZ + W})" with "YdZ" or "YdZ + W" where W, X, Y, Z are any integer
    pattern = r"\d+\s\({@damage (.+?)\}\)"
    description = re.sub(
        pattern,
        lambda match: damage_to_gurps(expected_value(match.group(1))),
        description,
    )

    # Replace all "{@hit X} with X
    pattern = r"\{@hit (.+?)\}"
    description = re.sub(
        pattern,
        lambda match: hit_mod_to_gurps(int(match.group(1))),
        description,
    )

    # Replace all "{@dc X} ST roll" where X is any integer and ST can be any string of length 2 with "ST - X roll"
    pattern = r"\{@dc (\d+)\} (\w{2}) roll"
    description = re.sub(
        pattern,
        lambda match: match.group(2)
        + " - "
        + str(saving_throws_to_gurps(int(match.group(1))))
        + " roll",
        description,
    )

    # pattern = r"\b(\d+)[dD](\d+)\b"
    # description = re.sub(
    #     pattern,
    #     lambda match: damage_to_gurps(expected_value(match.group())),
    #     description,
    # )

    # # replace all instances of {@word text} with text
    # pattern = r"\{@\w+\s(.+?)\}"
    # description = re.sub(pattern, r"\1", description)

    # # replace all instances of X (Yd + Z) with Yd + Z
    # pattern = r"\d+\s\((.+)\)"
    # description = re.sub(pattern, r"\1", description)

    # Saving throw DC -> comparable GURPS DC

    return description


# endregion
def run_convert(input_data, user_input: str):
    # region LOADING DATA

    # Load default file
    with open("default.json", "r") as f:
        default_data = json.load(f)
    # endregion

    # PROCESSING DATA

    # Proficiency Bonus
    if "cr" in input_data:
        if type(input_data["cr"]) == dict:
            profString = input_data["cr"]["cr"]
        else:
            profString = input_data["cr"]
        if profString == "0":
            profBonus = 2
        elif profString == "1/8":
            profBonus = 2
        elif profString == "1/4":
            profBonus = 2
        elif profString == "1/2":
            profBonus = 2
        else:
            profBonus = math.ceil(float(profString) / 4) + 1
    else:
        profBonus = 2

    # Update default data with name from input data
    creature_name = input_data["name"]
    default_data["profile"]["name"] = creature_name

    # Update default data with attributes from input data
    for attribute in default_data["attributes"]:
        if attribute["attr_id"] == "st":
            strAd = math.floor((input_data["str"] - 10) / 2)
            attribute["adj"] = strAd
            attribute["calc"]["points"] = strAd * 10
            attribute["calc"]["value"] = 10 + strAd

        if attribute["attr_id"] == "dx":
            dexAd = math.floor((input_data["dex"] - 10) / 2)
            attribute["adj"] = dexAd
            attribute["calc"]["points"] = dexAd * 20
            attribute["calc"]["value"] = 10 + dexAd

        if attribute["attr_id"] == "iq":
            iqAd = max(
                math.floor((input_data["int"] - 10) / 2),
                math.floor((input_data["wis"] - 10) / 2),
            )
            attribute["adj"] = iqAd
            attribute["calc"]["points"] = iqAd * 20
            attribute["calc"]["value"] = 10 + iqAd

        if attribute["attr_id"] == "ht":
            conAdd = math.floor((input_data["con"] - 10) / 2)
            attribute["adj"] = conAdd
            attribute["calc"]["points"] = conAdd * 10
            attribute["calc"]["value"] = 10 + conAdd
            if input_data["con"] >= 14:
                # region High Pain Threshold Trait
                highPainThreshold = {
                    "id": str(uuid.uuid4()),  # Generate a new unique ID
                    "type": "trait",
                    "name": "High Pain Threshold",
                    "reference": "B59",
                    "notes": "Never suffer shock penalties when injured",
                    "tags": ["Advantage", "Physical"],
                    "base_points": 10,
                    "features": [
                        {
                            "type": "conditional_modifier",
                            "situation": "on all HT rolls to avoid knockdown and stunning",
                            "amount": 3,
                        },
                        {
                            "type": "conditional_modifier",
                            "situation": "to resist torture",
                            "amount": 3,
                        },
                    ],
                    "calc": {"points": 10},
                }
                # endregion

                default_data["traits"].append(highPainThreshold)

    # Give default persuasion and deception if charisma is high enough and no profieciency is given
    charAd = math.floor((input_data["cha"] - 10) / 2)
    if charAd > 0:
        #  If Pesuasion is not in the stat-block, Diplomacy is added
        if "skill" not in input_data or "persuasion" not in input_data["skill"]:
            # region Diplomacy Skill
            diplomacySkill = {
                "id": str(uuid.uuid4()),
                "type": "skill",
                "name": "Diplomacy",
                "reference": "B187",
                "tags": ["Business", "Police", "Social"],
                "difficulty": "iq/h",
                "points": convert_modifier_to_points(charAd),
                "defaulted_from": {
                    "type": "iq",
                    "modifier": -6,
                    "level": 9,
                    "adjusted_level": 9,
                    "points": -9,
                },
                "defaults": [
                    {"type": "iq", "modifier": -6},
                    {"type": "skill", "name": "Politics", "modifier": -6},
                ],
                "calc": {"level": 13, "rsl": "IQ-2"},
            }
            # endregion
            default_data["skills"].append(diplomacySkill)
        # If Deception is not in the statblock, fast-talk is added
        if "skill" not in input_data or "deception" not in input_data["skill"]:
            # region Fast-Talk Skill
            fastTalkSkill = {
                "id": str(uuid.uuid4()),
                "type": "skill",
                "name": "Fast-Talk",
                "reference": "B195",
                "tags": ["Criminal", "Social", "Spy", "Street"],
                "difficulty": "iq/a",
                "points": convert_modifier_to_points(charAd),
                "defaulted_from": {
                    "type": "iq",
                    "modifier": -5,
                    "level": 10,
                    "adjusted_level": 10,
                    "points": -10,
                },
                "defaults": [
                    {"type": "iq", "modifier": -5},
                    {"type": "skill", "name": "Acting", "modifier": -5},
                ],
                "calc": {"level": 15, "rsl": "IQ+0"},
            }
            # endregion
            default_data["skills"].append(fastTalkSkill)

    # Give Size/Strength Bonus depending on character size
    if "size" in input_data:
        if input_data["size"][0] == "M":
            default_data["profile"]["SM"] = 0
        elif input_data["size"][0] == "S":
            default_data["profile"]["SM"] = -1
        elif input_data["size"][0] == "T":
            default_data["profile"]["SM"] = -4
        elif input_data["size"][0] == "L":
            default_data["profile"]["SM"] = 2
            default_data["attributes"][0]["adj"] = (
                default_data["attributes"][0]["adj"] + 1
            )
            default_data["attributes"][14]["adj"] = (
                default_data["attributes"][14]["adj"] + 10
            )
        elif input_data["size"][0] == "H":
            default_data["profile"]["SM"] = 3
            default_data["attributes"][0]["adj"] = (
                default_data["attributes"][0]["adj"] + 2
            )
            default_data["attributes"][14]["adj"] = (
                default_data["attributes"][14]["adj"] + 20
            )
        elif input_data["size"][0] == "G":
            default_data["profile"]["SM"] = 4
            default_data["attributes"][0]["adj"] = (
                default_data["attributes"][0]["adj"] + 3
            )
            default_data["attributes"][14]["adj"] = (
                default_data["attributes"][14]["adj"] + 30
            )
    # Give climbing and acrobatics if character has acrobatics
    if "skill" in input_data and "acrobatics" in input_data["skill"]:
        acrobatics_modifier_string = input_data["skill"]["acrobatics"]
        acrobatics_modifier = int(
            acrobatics_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(acrobatics_modifier - dexAd)

        # region Climbing Skill
        climbingSkill = {
            "id": str(uuid.uuid4()),  # Generate a new unique ID
            "type": "skill",
            "name": "Climbing",
            "reference": "B183",
            "tags": ["Athletic", "Criminal", "Exploration", "Outdoor", "Street"],
            "difficulty": "dx/a",
            "points": points,
            "encumbrance_penalty_multiplier": 1,
            "defaulted_from": {
                "type": "dx",
                "modifier": -5,
                "level": 5,
                "adjusted_level": 5,
                "points": -5,
            },
            "defaults": [{"type": "dx", "modifier": -5}],
            "calc": {"level": 9, "rsl": "DX-1"},
        }
        # endregionß
        default_data["skills"].append(climbingSkill)

        # region Acrobatics Skill
        acrobaticsSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Acrobatics",
            "reference": "B174,MA54",
            "tags": ["Athletic"],
            "difficulty": "dx/h",
            "points": points,
            "defaulted_from": {
                "type": "dx",
                "modifier": -6,
                "level": 5,
                "adjusted_level": 5,
                "points": -5,
            },
            "defaults": [
                {"type": "dx", "modifier": -6},
                {"type": "skill", "name": "Aerobatics", "modifier": -4},
                {"type": "skill", "name": "Aquabatics", "modifier": -4},
            ],
            "calc": {"level": 9, "rsl": "DX-2"},
        }
        # endregion
        default_data["skills"].append(acrobaticsSkill)

    # Give animal handling (general) and riding if character has Animal Handling. Give Veterinary if character has high Animal Handling
    if "skill" in input_data and "animal handling" in input_data["skill"]:
        animalHandling_modifier_string = input_data["skill"]["animal handling"]
        animalHandling_modifier = int(
            animalHandling_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(profBonus)

        # region Animal Handling Skill
        animalHandlingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Animal Handling",
            "reference": "B175",
            "tags": ["Animal"],
            "specialization": "General",
            "difficulty": "iq/a",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [{"type": "iq", "modifier": -5}],
            "calc": {"level": 14, "rsl": "IQ-1"},
        }
        # endregion
        default_data["skills"].append(animalHandlingSkill)

        # region Riding Skill
        ridingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Riding",
            "reference": "B217",
            "tags": ["Animal"],
            "specialization": "General",
            "difficulty": "dx/a",
            "points": points,
            "defaulted_from": {
                "type": "skill",
                "name": "Animal Handling",
                "specialization": "General",
                "modifier": -3,
                "level": 11,
                "adjusted_level": 11,
                "points": 2,
            },
            "defaults": [
                {"type": "dx", "modifier": -5},
                {
                    "type": "skill",
                    "name": "Animal Handling",
                    "specialization": "General",
                    "modifier": -3,
                },
            ],
            "calc": {"level": 11, "rsl": "DX+0"},
        }
        # endregion
        default_data["skills"].append(ridingSkill)

        if animalHandling_modifier >= 6:
            # region Veterinary Skill
            veterinarySkill = {
                "id": str(uuid.uuid4()),
                "type": "skill",
                "name": "Veterinary",
                "reference": "B228",
                "tags": ["Animal", "Medical"],
                "tech_level": "4",
                "difficulty": "iq/h",
                "points": points,
                "defaulted_from": {
                    "type": "skill",
                    "name": "Animal Handling",
                    "specialization": "General",
                    "modifier": -6,
                    "level": 8,
                    "adjusted_level": 8,
                    "points": -8,
                },
                "defaults": [
                    {"type": "skill", "name": "Animal Handling", "modifier": -6},
                    {"type": "skill", "name": "Physician", "modifier": -5},
                    {"type": "skill", "name": "Surgery", "modifier": -5},
                ],
                "calc": {"level": 13, "rsl": "IQ-2"},
            }
            # endregion
            default_data["skills"].append(veterinarySkill)

    # Give Thaumatology and Occultism if the character has Arcana
    if "skill" in input_data and "arcana" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Thaumatology Skill
        thaumatologySkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Thaumatology",
            "reference": "B225",
            "tags": ["Magical", "Occult"],
            "difficulty": "iq/vh",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -7,
                "level": 8,
                "adjusted_level": 8,
                "points": -8,
            },
            "defaults": [{"type": "iq", "modifier": -7}],
            "calc": {"level": 12, "rsl": "IQ-3"},
        }
        # endregion
        default_data["skills"].append(thaumatologySkill)

        # region Occultism Skill
        occultismSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Occultism",
            "reference": "B212",
            "tags": ["Magical", "Occult"],
            "difficulty": "iq/a",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [{"type": "iq", "modifier": -5}],
            "calc": {"level": 14, "rsl": "IQ-1"},
        }
        # endregion
        default_data["skills"].append(occultismSkill)

    # Give Climbing, Hiking, Brawling, and Running if the chracter has Athletics. Climbing is only added if the character doesn't have acrobatics
    if "skill" in input_data and "athletics" in input_data["skill"]:
        athletics_modifier_string = input_data["skill"]["athletics"]
        athletics_modifier = int(
            athletics_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(athletics_modifier - strAd)

        if "acrobatics" not in input_data["skill"]:
            # region Climbing Skill
            climbingSkill = {
                "id": str(uuid.uuid4()),
                "type": "skill",
                "name": "Climbing",
                "reference": "B175",
                "tags": ["Physical"],
                "difficulty": "dx/a",
                "points": points,
                "defaulted_from": {
                    "type": "dx",
                    "modifier": -5,
                    "level": 10,
                    "adjusted_level": 10,
                    "points": -10,
                },
                "defaults": [{"type": "dx", "modifier": -5}],
                "calc": {"level": 14, "rsl": "DX-1"},
            }
            # endregion
            default_data["skills"].append(climbingSkill)

        # region Hiking Skill
        hikingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Hiking",
            "reference": "B200",
            "tags": ["Athletic", "Exploration", "Outdoor"],
            "difficulty": "ht/a",
            "points": points,
            "defaulted_from": {
                "type": "ht",
                "modifier": -5,
                "level": 6,
                "adjusted_level": 6,
                "points": -6,
            },
            "defaults": [{"type": "ht", "modifier": -5}],
            "calc": {"level": 10, "rsl": "HT-1"},
        }
        # endregion
        default_data["skills"].append(hikingSkill)

        # region Brawling Skill
        brawlingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Brawling",
            "reference": "B182,MA55",
            "tags": ["Combat", "Melee Combat", "Weapon"],
            "difficulty": "dx/e",
            "points": points,
            "features": [
                {
                    "type": "weapon_bonus",
                    "selection_type": "weapons_with_required_skill",
                    "name": {"compare": "is", "qualifier": "Brawling"},
                    "level": {"compare": "at_least", "qualifier": 2},
                    "amount": 1,
                    "per_level": True,
                }
            ],
            "calc": {"level": 11, "rsl": "DX+0"},
        }
        # endregion
        default_data["skills"].append(brawlingSkill)

        # region Running Skill
        runningSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Running",
            "reference": "B218",
            "tags": ["Athletic"],
            "difficulty": "ht/a",
            "points": points,
            "defaulted_from": {
                "type": "ht",
                "modifier": -5,
                "level": 6,
                "adjusted_level": 6,
                "points": -6,
            },
            "defaults": [{"type": "ht", "modifier": -5}],
            "calc": {"level": 10, "rsl": "HT-1"},
        }
        # endregion
        default_data["skills"].append(runningSkill)

    # Give Fast-Talk if the character has Deception
    if "skill" in input_data and "deception" in input_data["skill"]:
        deception_modifier_string = input_data["skill"]["deception"]
        deception_modifier = int(
            deception_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(deception_modifier - charAd)

        # region Fast-Talk Skill
        fastTalkSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Fast-Talk",
            "reference": "B195",
            "tags": ["Criminal", "Social", "Spy", "Street"],
            "difficulty": "iq/a",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [
                {"type": "iq", "modifier": -5},
                {"type": "skill", "name": "Acting", "modifier": -5},
            ],
            "calc": {"level": 14, "rsl": "IQ-1"},
        }
        # endregion
        default_data["skills"].append(fastTalkSkill)

    # Give History (General) if the character has History
    if "skill" in input_data and "history" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region History (General) Skill
        historyGeneralSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "History",
            "reference": "B200",
            "tags": ["Humanities", "Social Sciences"],
            "specialization": "General",
            "difficulty": "iq/h",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -6,
                "level": 9,
                "adjusted_level": 9,
                "points": -9,
            },
            "defaults": [{"type": "iq", "modifier": -6}],
            "calc": {"level": 13, "rsl": "IQ-2"},
        }
        # endregion
        default_data["skills"].append(historyGeneralSkill)

    # Give Detect Lie if the characters have Insight
    if "skill" in input_data and "insight" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Detect Lies Skill
        detectLieSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Detect Lies",
            "reference": "B187",
            "tags": ["Police", "Social", "Spy"],
            "difficulty": "per/h",
            "points": points,
            "defaulted_from": {
                "type": "per",
                "modifier": -6,
                "level": 9,
                "adjusted_level": 9,
                "points": -9,
            },
            "defaults": [
                {"type": "per", "modifier": -6},
                {"type": "skill", "name": "Body Language", "modifier": -4},
                {"type": "skill", "name": "Psychology", "modifier": -4},
            ],
            "calc": {"level": 13, "rsl": "Per-2"},
        }
        # endregion
        default_data["skills"].append(detectLieSkill)

    # Give Intimidation if the character has Intimidation
    if "skill" in input_data and "intimidation" in input_data["skill"]:
        intimidation_modifier_string = input_data["skill"]["intimidation"]
        intimidation_modifier = int(
            intimidation_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(intimidation_modifier - charAd)

        # region Intimidation Skill
        intimidationSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Intimidation",
            "reference": "B202",
            "tags": ["Criminal", "Police", "Social", "Street"],
            "difficulty": "will/a",
            "points": points,
            "defaulted_from": {
                "type": "will",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [
                {"type": "will", "modifier": -5},
                {"type": "skill", "name": "Acting", "modifier": -3},
            ],
            "calc": {"level": 14, "rsl": "Will-1"},
        }
        # endregion
        default_data["skills"].append(intimidationSkill)

    # Give Scrouning and Search if the character has Investgation
    if "skill" in input_data and "investigation" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Scrounging Skill
        scroungingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Scrounging",
            "reference": "B218",
            "tags": ["Criminal", "Street"],
            "difficulty": "per/e",
            "points": points,
            "defaulted_from": {
                "type": "per",
                "modifier": -4,
                "level": 11,
                "adjusted_level": 11,
                "points": -11,
            },
            "defaults": [{"type": "per", "modifier": -4}],
            "calc": {"level": 15, "rsl": "Per+0"},
        }
        # endregion
        default_data["skills"].append(scroungingSkill)

        # region Search Skill
        searchSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Search",
            "reference": "B219",
            "tags": ["Police", "Spy"],
            "difficulty": "per/a",
            "points": points,
            "defaulted_from": {
                "type": "per",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [
                {"type": "per", "modifier": -5},
                {"type": "skill", "name": "Criminology", "modifier": -5},
            ],
            "calc": {"level": 14, "rsl": "Per-1"},
        }
        # endregion
        default_data["skills"].append(searchSkill)

    # Give First-Aid, Diagnosis, Physician (if medium), and Surgery (if high) if the character has Medicine
    if "skill" in input_data and "medicine" in input_data["skill"]:
        medicine_modifier_string = input_data["skill"]["medicine"]
        medicine_modifier = int(
            medicine_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(profBonus)

        # region First-Aid Skill
        firstAidSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "First Aid",
            "reference": "B195",
            "tags": ["Everyman", "Medical"],
            "tech_level": "4",
            "difficulty": "iq/e",
            "points": points,
            "defaulted_from": {
                "type": "skill",
                "name": "Physician",
                "level": 13,
                "adjusted_level": 13,
                "points": -13,
            },
            "defaults": [
                {"type": "iq", "modifier": -4},
                {"type": "skill", "name": "Esoteric Medicine"},
                {"type": "skill", "name": "Physician"},
                {"type": "skill", "name": "Veterinary", "modifier": -4},
            ],
            "calc": {"level": 15, "rsl": "IQ+0"},
        }
        # endregion
        default_data["skills"].append(firstAidSkill)

        # region Diagnosis Skill
        diagnosisSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Diagnosis",
            "reference": "B187",
            "tags": ["Medical"],
            "tech_level": "4",
            "difficulty": "iq/h",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -6,
                "level": 9,
                "adjusted_level": 9,
                "points": -9,
            },
            "defaults": [
                {"type": "iq", "modifier": -6},
                {"type": "skill", "name": "First Aid", "modifier": -8},
                {"type": "skill", "name": "Physician", "modifier": -4},
                {"type": "skill", "name": "Veterinary", "modifier": -5},
            ],
            "calc": {"level": 13, "rsl": "IQ-2"},
        }
        # endregion
        default_data["skills"].append(diagnosisSkill)

        if medicine_modifier >= 3:
            # region Physician Skill
            physicianSkill = {
                "id": str(uuid.uuid4()),
                "type": "skill",
                "name": "Physician",
                "reference": "B213",
                "tags": ["Medical"],
                "tech_level": "4",
                "difficulty": "iq/h",
                "points": points,
                "defaulted_from": {
                    "type": "iq",
                    "modifier": -7,
                    "level": 8,
                    "adjusted_level": 8,
                    "points": -8,
                },
                "defaults": [
                    {"type": "iq", "modifier": -7},
                    {"type": "skill", "name": "First Aid", "modifier": -11},
                    {"type": "skill", "name": "Veterinary", "modifier": -5},
                ],
                "calc": {"level": 13, "rsl": "IQ-2"},
            }
            # endregion
            default_data["skills"].append(physicianSkill)

        if medicine_modifier >= 6:
            # region Surgery Skill
            surgerySkill = {
                "id": str(uuid.uuid4()),
                "type": "skill",
                "name": "Surgery",
                "reference": "B223",
                "tags": ["Medical"],
                "tech_level": "4",
                "difficulty": "iq/vh",
                "points": points,
                "defaulted_from": {
                    "type": "skill",
                    "name": "Physician",
                    "modifier": -5,
                    "level": 8,
                    "adjusted_level": 8,
                    "points": -8,
                },
                "defaults": [
                    {"type": "skill", "name": "First Aid", "modifier": -12},
                    {"type": "skill", "name": "Physician", "modifier": -5},
                    {"type": "skill", "name": "Physiology", "modifier": -8},
                    {"type": "skill", "name": "Veterinary", "modifier": -5},
                ],
                "prereqs": {
                    "type": "prereq_list",
                    "all": False,
                    "prereqs": [
                        {
                            "type": "skill_prereq",
                            "has": True,
                            "name": {"compare": "is", "qualifier": "first aid"},
                        },
                        {
                            "type": "skill_prereq",
                            "has": True,
                            "name": {"compare": "is", "qualifier": "physician"},
                        },
                    ],
                },
                "calc": {"level": 12, "rsl": "IQ-3"},
            }
            # endregion
            default_data["skills"].append(surgerySkill)

    # Give Gardening and Biology (Botany) if the character has Nature
    if "skill" in input_data and "nature" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Gardening Skill
        gardeningSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Gardening",
            "reference": "B197",
            "tags": ["Plant"],
            "difficulty": "iq/e",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -4,
                "level": 11,
                "adjusted_level": 11,
                "points": -11,
            },
            "defaults": [
                {"type": "iq", "modifier": -4},
                {"type": "skill", "name": "Farming", "modifier": -3},
            ],
            "calc": {"level": 15, "rsl": "IQ+0"},
        }
        # endregion
        default_data["skills"].append(gardeningSkill)

        # region Botany Skill
        botanySkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Biology",
            "reference": "B180",
            "tags": ["Natural Science", "Plant"],
            "specialization": "Botany",
            "tech_level": "4",
            "difficulty": "iq/vh",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -6,
                "level": 9,
                "adjusted_level": 9,
                "points": -9,
            },
            "defaults": [
                {"type": "iq", "modifier": -6},
                {"type": "skill", "name": "Naturalist", "modifier": -6},
            ],
            "calc": {"level": 12, "rsl": "IQ-3"},
        }
        # endregion
        default_data["skills"].append(botanySkill)

    # Give Observation and Acute Vision Trait if the character has Perception
    if "skill" in input_data and "perception" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Observation Skill
        observationSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Observation",
            "reference": "B211",
            "tags": ["Criminal", "Military", "Police", "Spy", "Street"],
            "difficulty": "per/a",
            "points": points,
            "defaulted_from": {
                "type": "per",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [
                {"type": "per", "modifier": -5},
                {"type": "skill", "name": "Shadowing", "modifier": -5},
            ],
            "calc": {"level": 14, "rsl": "Per-1"},
        }
        # endregion
        default_data["skills"].append(observationSkill)

        # region Acute Vision Trait
        acuteVisionTrait = {
            "id": "e36a16e5-aba0-41d3-89a6-8825eb72565a",
            "type": "trait",
            "name": "Acute Vision",
            "reference": "B35",
            "tags": ["Advantage", "Physical"],
            "levels": profBonus,
            "points_per_level": 2,
            "features": [
                {
                    "type": "attribute_bonus",
                    "attribute": "vision",
                    "amount": 1,
                    "per_level": True,
                }
            ],
            "can_level": True,
            "calc": {"points": 2},
        }
        # endregion
        default_data["traits"].append(acuteVisionTrait)

    # Give Acting, Dancing, Musical Instrument (any), and Singing if the character has Performance
    if "skill" in input_data and "performance" in input_data["skill"]:
        performance_modifier_string = input_data["skill"]["performance"]
        performance_modifier = int(
            performance_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(performance_modifier - charAd)

        # region Acting Skill
        actingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Acting",
            "reference": "B174",
            "tags": ["Social", "Spy"],
            "difficulty": "iq/a",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [
                {"type": "iq", "modifier": -5},
                {"type": "skill", "name": "Performance", "modifier": -2},
                {"type": "skill", "name": "Public Speaking", "modifier": -5},
            ],
            "calc": {"level": 14, "rsl": "IQ-1"},
        }
        # endregion
        default_data["skills"].append(actingSkill)

        # region Dancing Skill
        dancingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Dancing",
            "reference": "B187",
            "tags": ["Arts", "Entertainment"],
            "difficulty": "dx/a",
            "points": points,
            "defaulted_from": {
                "type": "dx",
                "modifier": -5,
                "level": 6,
                "adjusted_level": 6,
                "points": -6,
            },
            "defaults": [{"type": "dx", "modifier": -5}],
            "calc": {"level": 10, "rsl": "DX-1"},
        }
        # endregion
        default_data["skills"].append(dancingSkill)

        # region Musical Instrument Skill
        musicalInstrumentSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Musical Instrument",
            "reference": "B211",
            "tags": ["Arts", "Entertainment"],
            "specialization": "Any",
            "difficulty": "iq/h",
            "points": points,
            "calc": {"level": 13, "rsl": "IQ-2"},
        }
        # endregion
        default_data["skills"].append(musicalInstrumentSkill)

        # region Singing Skill
        singingSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Singing",
            "reference": "B220",
            "tags": ["Arts", "Entertainment"],
            "difficulty": "ht/e",
            "points": points,
            "defaulted_from": {
                "type": "ht",
                "modifier": -4,
                "level": 7,
                "adjusted_level": 7,
                "points": -7,
            },
            "defaults": [{"type": "ht", "modifier": -4}],
            "calc": {"level": 11, "rsl": "HT+0"},
        }
        # endregion
        default_data["skills"].append(singingSkill)

    # Give Diplomacy if the character has Persuasion
    if "skill" in input_data and "persuasion" in input_data["skill"]:
        persuasion_modifier_string = input_data["skill"]["persuasion"]
        persuasion_modifier = int(
            persuasion_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(persuasion_modifier - charAd)

        # region Diplomacy Skill
        diplomacySkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Diplomacy",
            "reference": "B187",
            "tags": ["Business", "Police", "Social"],
            "difficulty": "iq/h",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -6,
                "level": 9,
                "adjusted_level": 9,
                "points": -9,
            },
            "defaults": [
                {"type": "iq", "modifier": -6},
                {"type": "skill", "name": "Politics", "modifier": -6},
            ],
            "calc": {"level": 13, "rsl": "IQ-2"},
        }
        # endregion
        default_data["skills"].append(diplomacySkill)

    # Give Theology (General) if the character has Religion
    if "skill" in input_data and "religion" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Theology (General) Skill
        theologySkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Theology",
            "reference": "B226",
            "tags": ["Humanities", "Social Sciences"],
            "specialization": "Any",
            "difficulty": "iq/h",
            "points": points,
            "defaulted_from": {
                "type": "iq",
                "modifier": -6,
                "level": 9,
                "adjusted_level": 9,
                "points": -9,
            },
            "defaults": [
                {"type": "iq", "modifier": -6},
                {
                    "type": "skill",
                    "name": "Religious Ritual",
                    "specialization": "Any",
                    "modifier": -4,
                },
            ],
            "calc": {"level": 13, "rsl": "IQ-2"},
        }
        # endregion
        default_data["skills"].append(theologySkill)

    # Give Sleight of Hand if the character has Sleight of Hand
    if "skill" in input_data and "sleight of hand" in input_data["skill"]:
        sof_modifier_string = input_data["skill"]["sleight of hand"]
        sof_modifier = int(sof_modifier_string.replace("+", ""))  # Remove '+' sign
        points = convert_modifier_to_points(sof_modifier - dexAd)

        # region Sleight of Hand Skill
        sleightOfHandSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Sleight of Hand",
            "reference": "B221",
            "tags": ["Arts", "Criminal", "Entertainment", "Street"],
            "difficulty": "dx/h",
            "points": points,
            "defaults": [{"type": "skill", "name": "Filch", "modifier": -5}],
            "calc": {"level": 9, "rsl": "DX-2"},
        }
        # endregion
        default_data["skills"].append(sleightOfHandSkill)

    # Give Stealth if the character has Stealth
    if "skill" in input_data and "stealth" in input_data["skill"]:
        stealth_modifier_string = input_data["skill"]["stealth"]
        stealth_modifier = int(
            stealth_modifier_string.replace("+", "")
        )  # Remove '+' sign
        points = convert_modifier_to_points(stealth_modifier - dexAd)

        # region Stealth Skill
        stealthSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Stealth",
            "reference": "B222",
            "tags": ["Criminal", "Police", "Spy", "Street"],
            "difficulty": "dx/a",
            "points": points,
            "encumbrance_penalty_multiplier": 1,
            "defaulted_from": {
                "type": "iq",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": 1,
            },
            "defaults": [
                {"type": "iq", "modifier": -5},
                {"type": "dx", "modifier": -5},
            ],
            "calc": {"level": 11, "rsl": "DX+0"},
        }
        # endregion
        default_data["skills"].append(stealthSkill)

    # Give Survival (any) if the character has Survival
    if "skill" in input_data and "survival" in input_data["skill"]:
        points = convert_modifier_to_points(profBonus)

        # region Survival (any) Skill
        survivalSkill = {
            "id": str(uuid.uuid4()),
            "type": "skill",
            "name": "Survival",
            "reference": "B223",
            "tags": ["Exploration", "Outdoor"],
            "specialization": "Any",
            "difficulty": "per/a",
            "points": points,
            "defaulted_from": {
                "type": "per",
                "modifier": -5,
                "level": 10,
                "adjusted_level": 10,
                "points": -10,
            },
            "defaults": [
                {"type": "per", "modifier": -5},
                {"type": "skill", "name": "Naturalist", "modifier": -3},
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "Bank",
                    "modifier": -4,
                },
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "Deep Ocean Vent",
                    "modifier": -4,
                },
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "Fresh-Water Lake",
                    "modifier": -4,
                },
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "Open Ocean",
                    "modifier": -4,
                },
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "Reef",
                    "modifier": -4,
                },
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "River/Stream",
                    "modifier": -4,
                },
                {
                    "type": "skill",
                    "name": "Survival",
                    "specialization": "Tropical Lagoon",
                    "modifier": -4,
                },
            ],
            "calc": {"level": 14, "rsl": "Per-1"},
        }
        # endregion
        default_data["skills"].append(survivalSkill)

    if user_input.lower() == "yes":
        # region Combat Reflexes Trait
        combatReflexesTrait = {
            "id": str(uuid.uuid4()),
            "type": "trait",
            "name": "Combat Reflexes",
            "reference": "B43",
            "notes": "Never freeze",
            "tags": ["Advantage", "Mental"],
            "base_points": 15,
            "prereqs": {
                "type": "prereq_list",
                "all": True,
                "prereqs": [
                    {
                        "type": "trait_prereq",
                        "has": False,
                        "name": {"compare": "is", "qualifier": "Enhanced Time Sense"},
                    }
                ],
            },
            "features": [
                {
                    "type": "skill_bonus",
                    "selection_type": "skills_with_name",
                    "name": {"compare": "starts_with", "qualifier": "fast-draw"},
                    "amount": 1,
                },
                {"type": "attribute_bonus", "attribute": "dodge", "amount": 1},
                {"type": "attribute_bonus", "attribute": "parry", "amount": 1},
                {"type": "attribute_bonus", "attribute": "block", "amount": 1},
                {"type": "attribute_bonus", "attribute": "fright_check", "amount": 2},
                {
                    "type": "conditional_modifier",
                    "situation": "on all IQ rolls to wake up or to recover from surprise or mental stun",
                    "amount": 6,
                },
                {
                    "type": "conditional_modifier",
                    "situation": "to initiative rolls for your side (+2 if you are the leader)",
                    "amount": 1,
                },
            ],
            "calc": {"points": 15},
        }
        # endregion
        default_data["traits"].append(combatReflexesTrait)

    # Adds appropriate armor according to equipment
    # region Armor Pieces
    # region Leather Armor
    leatherArmor = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Armor",
        "reference": "B283",
        "tech_level": "1",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 100,
        "weight": "10 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 2},
            {"type": "dr_bonus", "location": "vitals", "amount": 2},
            {"type": "dr_bonus", "location": "groin", "amount": 2},
        ],
        "equipped": True,
        "calc": {"extended_value": 100, "extended_weight": "10 lb"},
    }
    # endregion
    heavyLeatherLeggings = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Heavy Leather Leggings",
        "reference": "B283",
        "tech_level": "1",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 60,
        "weight": "4 lb",
        "features": [{"type": "dr_bonus", "location": "leg", "amount": 2}],
        "equipped": True,
        "calc": {"extended_value": 60, "extended_weight": "4 lb"},
    }
    heavyLeatherSleeves = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Heavy Leather Sleeves",
        "reference": "B283",
        "tech_level": "1",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 50,
        "weight": "2 lb",
        "features": [{"type": "dr_bonus", "location": "arm", "amount": 2}],
        "equipped": True,
        "calc": {"extended_value": 50, "extended_weight": "2 lb"},
    }
    studdedLeatherSkirts = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Studded Leather Skirt",
        "reference": "B283",
        "notes": "Flexible",
        "tech_level": "1",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 60,
        "weight": "4 lb",
        "features": [
            {"type": "dr_bonus", "location": "groin", "amount": 3},
            {"type": "dr_bonus", "location": "leg", "amount": 3},
            {
                "type": "dr_bonus",
                "location": "groin",
                "specialization": "crushing",
                "amount": -1,
            },
            {
                "type": "dr_bonus",
                "location": "leg",
                "specialization": "crushing",
                "amount": -1,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 60, "extended_weight": "4 lb"},
    }
    leatherHelm = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Helm",
        "reference": "B284",
        "tech_level": "1",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 20,
        "weight": "0.5 lb",
        "features": [
            {"type": "dr_bonus", "location": "skull", "amount": 2},
            {"type": "dr_bonus", "location": "face", "amount": 2},
        ],
        "equipped": True,
        "calc": {"extended_value": 20, "extended_weight": "0.5 lb"},
    }
    leatherGloves = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Gloves",
        "reference": "B284",
        "notes": "Flexible",
        "tech_level": "1",
        "tags": ["Gloves"],
        "quantity": 1,
        "value": 30,
        "features": [{"type": "dr_bonus", "location": "hand", "amount": 2}],
        "equipped": True,
        "calc": {"extended_value": 30, "extended_weight": "0 lb"},
    }
    leatherPants = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Pants",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 40,
        "weight": "3 lb",
        "features": [
            {"type": "dr_bonus", "location": "groin", "amount": 1},
            {"type": "dr_bonus", "location": "leg", "amount": 1},
        ],
        "equipped": True,
        "calc": {"extended_value": 40, "extended_weight": "3 lb"},
    }
    leatherLeggings = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Leggings",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 40,
        "weight": "2 lb",
        "features": [{"type": "dr_bonus", "location": "leg", "amount": 1}],
        "equipped": True,
        "calc": {"extended_value": 40, "extended_weight": "2 lb"},
    }
    leatherJacket = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Jacket",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 50,
        "weight": "4 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 1},
            {"type": "dr_bonus", "location": "vitals", "amount": 1},
            {"type": "dr_bonus", "location": "arm", "amount": 1},
        ],
        "equipped": True,
        "calc": {"extended_value": 50, "extended_weight": "4 lb"},
    }
    leatherCap = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Leather Cap",
        "reference": "B284",
        "notes": "Flexible",
        "tech_level": "1",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 32,
        "features": [{"type": "dr_bonus", "location": "skull", "amount": 1}],
        "equipped": True,
        "calc": {"extended_value": 32, "extended_weight": "0 lb"},
    }
    steelBreastPlate = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Steel Breastplate",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 500,
        "weight": "18 lb",
        "features": [
            {
                "type": "dr_bonus",
                "location": "torso",
                "specialization": "frontal",
                "amount": 5,
            },
            {
                "type": "dr_bonus",
                "location": "vitals",
                "specialization": "frontal",
                "amount": 5,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 500, "extended_weight": "18 lb"},
    }
    steelPot = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Steel Pot",
        "reference": "B285",
        "tech_level": "6",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 60,
        "weight": "3 lb",
        "features": [{"type": "dr_bonus", "location": "skull", "amount": 4}],
        "equipped": True,
        "calc": {"extended_value": 60, "extended_weight": "3 lb"},
    }
    steelCorselet = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Steel Corselet",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 1300,
        "weight": "35 lb",
        "features": [
            {"type": "dr_bonus", "location": "groin", "amount": 6},
            {"type": "dr_bonus", "location": "torso", "amount": 6},
            {"type": "dr_bonus", "location": "vitals", "amount": 6},
        ],
        "equipped": True,
        "calc": {"extended_value": 1300, "extended_weight": "35 lb"},
    }
    gauntlets = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Gauntlets",
        "reference": "B284",
        "tech_level": "2",
        "tags": ["Gloves"],
        "quantity": 1,
        "value": 100,
        "weight": "2 lb",
        "features": [{"type": "dr_bonus", "location": "hand", "amount": 4}],
        "equipped": True,
        "calc": {"extended_value": 100, "extended_weight": "2 lb"},
    }
    plateLegs = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Plate Legs",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 1100,
        "weight": "20 lb",
        "features": [{"type": "dr_bonus", "location": "leg", "amount": 6}],
        "equipped": True,
        "calc": {"extended_value": 1100, "extended_weight": "20 lb"},
    }
    plateArms = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Plate Arms",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 1000,
        "weight": "15 lb",
        "features": [{"type": "dr_bonus", "location": "arm", "amount": 6}],
        "equipped": True,
        "calc": {"extended_value": 1000, "extended_weight": "15 lb"},
    }
    mailShirt = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Mail Shirt",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "2",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 150,
        "weight": "16 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 4},
            {"type": "dr_bonus", "location": "vitals", "amount": 4},
            {
                "type": "dr_bonus",
                "location": "torso",
                "specialization": "crushing",
                "amount": -2,
            },
            {
                "type": "dr_bonus",
                "location": "vitals",
                "specialization": "crushing",
                "amount": -2,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 150, "extended_weight": "16 lb"},
    }
    mailCoif = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Mail Coif",
        "reference": "B284",
        "notes": "Flexible",
        "tech_level": "2",
        "legality_class": "3",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 55,
        "weight": "4 lb",
        "features": [
            {"type": "dr_bonus", "location": "skull", "amount": 4},
            {"type": "dr_bonus", "location": "neck", "amount": 4},
            {
                "type": "dr_bonus",
                "location": "skull",
                "specialization": "crushing",
                "amount": -2,
            },
            {
                "type": "dr_bonus",
                "location": "neck",
                "specialization": "crushing",
                "amount": -2,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 55, "extended_weight": "4 lb"},
    }
    mailLeggings = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Mail Leggings",
        "reference": "B283",
        "notes": "Flexible",
        "tech_level": "2",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 110,
        "weight": "15 lb",
        "features": [
            {"type": "dr_bonus", "location": "leg", "amount": 4},
            {
                "type": "dr_bonus",
                "location": "leg",
                "specialization": "crushing",
                "amount": -2,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 110, "extended_weight": "15 lb"},
    }
    mailSleeves = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Mail Sleeves",
        "reference": "B283",
        "notes": "Flexible",
        "tech_level": "2",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 70,
        "weight": "9 lb",
        "features": [
            {"type": "dr_bonus", "location": "arm", "amount": 4},
            {
                "type": "dr_bonus",
                "location": "arm",
                "specialization": "crushing",
                "amount": -2,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 70, "extended_weight": "9 lb"},
    }
    mailHauberk = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Mail Hauberk",
        "reference": "B283",
        "notes": "Flexible",
        "tech_level": "2",
        "legality_class": "3",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 230,
        "weight": "25 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 4},
            {"type": "dr_bonus", "location": "vitals", "amount": 4},
            {"type": "dr_bonus", "location": "groin", "amount": 4},
            {
                "type": "dr_bonus",
                "location": "torso",
                "specialization": "crushing",
                "amount": -2,
            },
            {
                "type": "dr_bonus",
                "location": "vitals",
                "specialization": "crushing",
                "amount": -2,
            },
            {
                "type": "dr_bonus",
                "location": "groin",
                "specialization": "crushing",
                "amount": -2,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 230, "extended_weight": "25 lb"},
    }
    greatHelm = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Greathelm",
        "reference": "B284",
        "notes": "No peripheral vision",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 340,
        "weight": "10 lb",
        "features": [
            {"type": "dr_bonus", "location": "neck", "amount": 7},
            {"type": "dr_bonus", "location": "face", "amount": 7},
            {"type": "dr_bonus", "location": "skull", "amount": 7},
        ],
        "equipped": True,
        "calc": {"extended_value": 340, "extended_weight": "10 lb"},
    }
    heavyPlateLegs = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Heavy Plate Legs",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 1600,
        "weight": "25 lb",
        "features": [{"type": "dr_bonus", "location": "leg", "amount": 7}],
        "equipped": True,
        "calc": {"extended_value": 1600, "extended_weight": "25 lb"},
    }
    heavyPlateArms = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Heavy Plate Arms",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 1500,
        "weight": "20 lb",
        "features": [{"type": "dr_bonus", "location": "arm", "amount": 7}],
        "equipped": True,
        "calc": {"extended_value": 1500, "extended_weight": "20 lb"},
    }
    heavySteelCorselet = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Heavy Steel Corselet",
        "reference": "B283",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 2300,
        "weight": "45 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 7},
            {"type": "dr_bonus", "location": "vitals", "amount": 7},
            {"type": "dr_bonus", "location": "groin", "amount": 7},
        ],
        "equipped": True,
        "calc": {"extended_value": 2300, "extended_weight": "45 lb"},
    }
    heavyGauntlets = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Heavy Gauntlets",
        "reference": "B284",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Gloves"],
        "quantity": 1,
        "value": 250,
        "weight": "2.5 lb",
        "features": [{"type": "dr_bonus", "location": "hand", "amount": 5}],
        "equipped": True,
        "calc": {"extended_value": 250, "extended_weight": "2.5 lb"},
    }
    sollerets = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Sollerets",
        "reference": "B284",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Footwear"],
        "quantity": 1,
        "value": 150,
        "weight": "7 lb",
        "features": [
            {"type": "dr_bonus", "location": "foot", "amount": 4},
            {
                "type": "weapon_bonus",
                "selection_type": "weapons_with_name",
                "specialization": {"compare": "is", "qualifier": "Kick"},
                "amount": 1,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 150, "extended_weight": "7 lb"},
    }
    scaleArmor = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Scale Armor",
        "reference": "B283",
        "tech_level": "2",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 420,
        "weight": "35 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 4},
            {"type": "dr_bonus", "location": "vitals", "amount": 4},
            {"type": "dr_bonus", "location": "groin", "amount": 4},
        ],
        "equipped": True,
        "calc": {"extended_value": 420, "extended_weight": "35 lb"},
    }
    scaleLeggings = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Scale Leggings",
        "reference": "B283",
        "tech_level": "2",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 250,
        "weight": "21 lb",
        "features": [{"type": "dr_bonus", "location": "leg", "amount": 4}],
        "equipped": True,
        "calc": {"extended_value": 250, "extended_weight": "21 lb"},
    }
    scaleSleeves = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Scale Sleeves",
        "reference": "B283",
        "tech_level": "2",
        "legality_class": "3",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 210,
        "weight": "14 lb",
        "features": [{"type": "dr_bonus", "location": "arm", "amount": 4}],
        "equipped": True,
        "calc": {"extended_value": 210, "extended_weight": "14 lb"},
    }
    barrelHelm = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Barrel Helm",
        "reference": "B284",
        "notes": "No peripheral vision",
        "tech_level": "3",
        "legality_class": "3",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 240,
        "weight": "10 lb",
        "features": [
            {"type": "dr_bonus", "location": "skull", "amount": 6},
            {"type": "dr_bonus", "location": "face", "amount": 6},
        ],
        "equipped": True,
        "calc": {"extended_value": 240, "extended_weight": "10 lb"},
    }
    buffCoat = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Buff Coat (Leather)",
        "reference": "B283",
        "notes": "Flexible",
        "tech_level": "4",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 210,
        "weight": "16 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 2},
            {"type": "dr_bonus", "location": "vitals", "amount": 2},
            {"type": "dr_bonus", "location": "arm", "amount": 2},
            {"type": "dr_bonus", "location": "leg", "amount": 2},
        ],
        "equipped": True,
        "calc": {"extended_value": 210, "extended_weight": "16 lb"},
    }
    clothArmor = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Cloth Armor",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 30,
        "weight": "6 lb",
        "features": [
            {"type": "dr_bonus", "location": "groin", "amount": 1},
            {"type": "dr_bonus", "location": "torso", "amount": 1},
            {"type": "dr_bonus", "location": "vitals", "amount": 1},
        ],
        "equipped": True,
        "calc": {"extended_value": 30, "extended_weight": "6 lb"},
    }
    clothGloves = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Cloth Gloves",
        "reference": "B284",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Gloves"],
        "quantity": 1,
        "value": 15,
        "features": [{"type": "dr_bonus", "location": "hand", "amount": 1}],
        "equipped": True,
        "calc": {"extended_value": 15, "extended_weight": "0 lb"},
    }
    clothCap = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Cloth Cap",
        "reference": "B284",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Headgear"],
        "quantity": 1,
        "value": 5,
        "features": [{"type": "dr_bonus", "location": "skull", "amount": 1}],
        "equipped": True,
        "calc": {"extended_value": 5, "extended_weight": "0 lb"},
    }
    clothSleeves = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Cloth Sleeves",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "1",
        "tags": ["Limb Armor"],
        "quantity": 1,
        "value": 20,
        "weight": "2 lb",
        "features": [{"type": "dr_bonus", "location": "arm", "amount": 1}],
        "equipped": True,
        "calc": {"extended_value": 20, "extended_weight": "2 lb"},
    }
    furLoincloth = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Fur Loincloth",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "0",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 10,
        "features": [{"type": "dr_bonus", "location": "groin", "amount": 1}],
        "equipped": True,
        "calc": {"extended_value": 10, "extended_weight": "0 lb"},
    }
    furTunic = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Fur Tunic",
        "reference": "B283",
        "notes": "Flexible, concealable",
        "tech_level": "0",
        "tags": ["Body Armor"],
        "quantity": 1,
        "value": 25,
        "weight": "2 lb",
        "features": [
            {"type": "dr_bonus", "location": "torso", "amount": 1},
            {"type": "dr_bonus", "location": "vitals", "amount": 1},
        ],
        "equipped": True,
        "calc": {"extended_value": 25, "extended_weight": "2 lb"},
    }
    boots = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Boots",
        "reference": "B284",
        "notes": "Flexible; Concealable",
        "tech_level": "2",
        "tags": ["Footwear"],
        "quantity": 1,
        "value": 80,
        "weight": "3 lb",
        "features": [
            {"type": "dr_bonus", "location": "foot", "amount": 2},
            {
                "type": "weapon_bonus",
                "selection_type": "weapons_with_name",
                "specialization": {"compare": "is", "qualifier": "Kick"},
                "amount": 1,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 80, "extended_weight": "3 lb"},
    }
    reinforcedBoots = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Reinforced Boots",
        "reference": "B284",
        "tech_level": "7",
        "tags": ["Footwear"],
        "quantity": 1,
        "value": 75,
        "weight": "3 lb",
        "features": [
            {"type": "dr_bonus", "location": "foot", "amount": 2},
            {
                "type": "weapon_bonus",
                "selection_type": "weapons_with_name",
                "specialization": {"compare": "is", "qualifier": "Kick"},
                "amount": 1,
            },
        ],
        "equipped": True,
        "calc": {"extended_value": 75, "extended_weight": "3 lb"},
    }
    mediumShield = {
        "id": str(uuid.uuid4()),
        "type": "equipment",
        "description": "Medium Shield",
        "reference": "B287",
        "tech_level": "1",
        "tags": ["Shield"],
        "quantity": 1,
        "value": 60,
        "weight": "15 lb",
        "weapons": [
            {
                "id": str(uuid.uuid4()),
                "type": "melee_weapon",
                "damage": {"type": "cr", "st": "thr"},
                "strength": "0",
                "usage": "Shield Bash",
                "reach": "1",
                "parry": "No",
                "block": "+0",
                "defaults": [
                    {"type": "dx", "modifier": -4},
                    {"type": "skill", "name": "Shield", "specialization": "Buckler"},
                    {
                        "type": "skill",
                        "name": "Shield",
                        "specialization": "Force Shield",
                    },
                    {"type": "skill", "name": "Shield", "specialization": "Shield"},
                ],
                "calc": {"level": 7, "parry": "No", "block": "8", "damage": "1d-2 cr"},
            }
        ],
        "features": [
            {"type": "attribute_bonus", "attribute": "dodge", "amount": 2},
            {"type": "attribute_bonus", "attribute": "parry", "amount": 2},
            {"type": "attribute_bonus", "attribute": "block", "amount": 2},
        ],
        "equipped": True,
        "calc": {"extended_value": 60, "extended_weight": "15 lb"},
    }
    # endregion

    for item in input_data["ac"]:
        # Nothing
        if type(item) is str or type(item) is int:
            continue
        # Natural Armor
        if ("from" in item and "natural armor" in item["from"]) and (item["ac"] > 11):
            levelFromAC = int(item["ac"]) - 11
            # region Damage Resistance
            damageResistance = {
                "id": str(uuid.uuid4()),
                "type": "trait",
                "name": "Damage Resistance",
                "reference": "B47,P45,MA43,PSI14",
                "tags": ["Advantage", "Exotic", "Physical"],
                "modifiers": [
                    {
                        "id": "71e0ea7a-bb0e-409d-b01d-aa247b4e66f6",
                        "type": "modifier",
                        "name": "Force Field",
                        "reference": "B47",
                        "cost": 20,
                        "disabled": True,
                    },
                    {
                        "id": "a5e89aca-0b61-483e-8ae3-d6086856cf9a",
                        "type": "modifier",
                        "name": "Hardened",
                        "reference": "B47",
                        "cost": 20,
                        "levels": 1,
                        "disabled": True,
                    },
                    {
                        "id": "0377b71f-5bfe-44a7-b1a0-db38c7952845",
                        "type": "modifier",
                        "name": "Absorption",
                        "reference": "B46",
                        "notes": "Enhances @Trait@",
                        "cost": 80,
                        "disabled": True,
                    },
                    {
                        "id": "db27da09-5815-4776-9af9-6d9741d8e52a",
                        "type": "modifier",
                        "name": "Absorption",
                        "reference": "B46",
                        "notes": "Healing only",
                        "cost": 80,
                        "disabled": True,
                    },
                    {
                        "id": "0e4c391b-1076-40f2-92b6-c5d3c60b78fd",
                        "type": "modifier",
                        "name": "Absorption",
                        "reference": "B46",
                        "notes": "Enhances any trait",
                        "cost": 100,
                        "disabled": True,
                    },
                    {
                        "id": "8b422514-296a-4b7c-b350-6b7e7d2be0e9",
                        "type": "modifier",
                        "name": "Reflection",
                        "reference": "B47",
                        "cost": 100,
                        "disabled": True,
                    },
                    {
                        "id": "419ab96d-ea87-4894-b6d8-a6ee32a5d416",
                        "type": "modifier",
                        "name": "Bane",
                        "reference": "H14",
                        "notes": "@Rare@",
                        "cost": -1,
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "a8c6d43d-430e-4773-a64c-200f75009e65",
                        "type": "modifier",
                        "name": "Bane",
                        "reference": "H14",
                        "notes": "@Occasional@",
                        "cost": -5,
                        "disabled": True,
                    },
                    {
                        "id": "e9503abd-7621-42c4-8ced-3981ec7c6d9a",
                        "type": "modifier",
                        "name": "Bane",
                        "reference": "H14",
                        "notes": "@Common@",
                        "cost": -10,
                        "disabled": True,
                    },
                    {
                        "id": "1585a884-94e2-4152-b7b7-d3b6cc253c58",
                        "type": "modifier",
                        "name": "Bane",
                        "reference": "H14",
                        "notes": "@Very Common@",
                        "cost": -15,
                        "disabled": True,
                    },
                    {
                        "id": "131c5627-2f5a-4f3f-8a52-08417003bc95",
                        "type": "modifier",
                        "name": "Directional",
                        "reference": "B47",
                        "notes": "Front",
                        "cost": -20,
                        "disabled": True,
                    },
                    {
                        "id": "132e7d43-7920-45f5-bcde-036029aa49f2",
                        "type": "modifier",
                        "name": "Flexible",
                        "reference": "B47",
                        "cost": -20,
                        "disabled": True,
                    },
                    {
                        "id": "d9e01c00-3ac2-4f4d-ae5f-45b34441df13",
                        "type": "modifier",
                        "name": "Limited",
                        "reference": "B46",
                        "notes": "@Very Common Attack Form@",
                        "cost": -20,
                        "disabled": True,
                    },
                    {
                        "id": "72f08aac-bc4a-43fe-875b-8747b7397bec",
                        "type": "modifier",
                        "name": "Semi-Ablative",
                        "reference": "B47",
                        "cost": -20,
                        "disabled": True,
                    },
                    {
                        "id": "13410164-cee1-4956-832c-47bcf41fdab8",
                        "type": "modifier",
                        "name": "Can't wear armor",
                        "reference": "B47",
                        "cost": -40,
                        "disabled": True,
                    },
                    {
                        "id": "9ad2a005-947f-4ef9-ba99-ed88a4adaa49",
                        "type": "modifier",
                        "name": "Directional",
                        "reference": "B47",
                        "notes": "@Direction: Back, Right, Left, Top or Underside@",
                        "cost": -40,
                        "disabled": True,
                    },
                    {
                        "id": "34ffce90-cba0-4d1a-a8ce-b3e6b12a51e3",
                        "type": "modifier",
                        "name": "Limited",
                        "reference": "B46",
                        "notes": "@Common Attack Form@",
                        "cost": -40,
                        "disabled": True,
                    },
                    {
                        "id": "10940926-bf24-4984-a984-d974384f0874",
                        "type": "modifier",
                        "name": "Tough Skin",
                        "notes": "Effects that just require skin contact or a scratch ignore this DR",
                        "cost": -40,
                        "disabled": True,
                    },
                    {
                        "id": "db046fce-bac2-4fae-98d4-ee66925c0e9e",
                        "type": "modifier",
                        "name": "Limited",
                        "reference": "B46",
                        "notes": "@Occasional Attack Form@",
                        "cost": -60,
                        "disabled": True,
                    },
                    {
                        "id": "b112e7ab-adac-40ef-a544-598ae0f7436f",
                        "type": "modifier",
                        "name": "Ablative",
                        "reference": "B47",
                        "cost": -80,
                        "disabled": True,
                    },
                    {
                        "id": "3b761122-5da1-46dd-992c-2f9df40890cb",
                        "type": "modifier",
                        "name": "Limited",
                        "reference": "B46",
                        "notes": "@Rare Attack Form@",
                        "cost": -80,
                        "disabled": True,
                    },
                    {
                        "id": "0ed89045-94df-4ab0-ac26-53103a2ad43f",
                        "type": "modifier",
                        "name": "Laminate",
                        "reference": "RSWL18",
                        "cost": 10,
                        "disabled": True,
                    },
                    {
                        "id": "a1baddab-14e3-402e-a209-1eee48ba98ec",
                        "type": "modifier",
                        "name": "Malediction-Proof",
                        "reference": "PSI14",
                        "cost": 50,
                        "disabled": True,
                    },
                    {
                        "id": "b1b407f3-24ca-4beb-8f3a-d362891e5af9",
                        "type": "modifier",
                        "name": "Maledictions Only",
                        "reference": "PSI14",
                        "disabled": True,
                    },
                    {
                        "id": "a48b115e-bf63-41f8-84cd-3b6d1e41653e",
                        "type": "modifier",
                        "name": "Partial (@Location, 1 level per -1 Per Hit Modifier, Torso is -10% thus level 1@)",
                        "reference": "B47",
                        "cost": -10,
                        "disabled": True,
                    },
                ],
                "levels": levelFromAC,
                "points_per_level": 5,
                "features": [
                    {
                        "type": "dr_bonus",
                        "location": "skull",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "face",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "neck",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "torso",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "vitals",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "groin",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "arm",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "hand",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "leg",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "foot",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "tail",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "wing",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "fin",
                        "amount": 1,
                        "per_level": True,
                    },
                    {
                        "type": "dr_bonus",
                        "location": "brain",
                        "amount": 1,
                        "per_level": True,
                    },
                ],
                "can_level": True,
                "calc": {"points": 5},
            }
            # endregion
            default_data["traits"].append(damageResistance)

        # Unarmored Defense adds Enhanced Dodge
        if ("from" in item and "unarmored" in item["from"]) and (item["ac"] > 11):
            levelFromAC = item["ac"] - 11
            # region Unarmored Defense
            unarmoredDefense = {
                "id": str(uuid.uuid4()),
                "type": "trait",
                "name": "Enhanced Dodge",
                "reference": "B51,MA43",
                "tags": ["Advantage", "Mental"],
                "levels": levelFromAC,
                "points_per_level": 15,
                "features": [
                    {
                        "type": "attribute_bonus",
                        "attribute": "dodge",
                        "amount": 1,
                        "per_level": True,
                    }
                ],
                "can_level": True,
                "calc": {"points": 15},
            }
            # endregion
            default_data["traits"].append(unarmoredDefense)

        # Leather / Leather Armor -> Leather Armor, Leather Pants, Heavy Leather Sleeves, Leather Helm, Boots
        elif "from" in item:
            for s in item["from"]:
                if "leather" in s and "studded" not in s:
                    default_data["equipment"].append(leatherArmor)
                    default_data["equipment"].append(leatherPants)
                    default_data["equipment"].append(heavyLeatherSleeves)
                    default_data["equipment"].append(leatherCap)
                    default_data["equipment"].append(boots)

        # Studded Leather / Studded Leather Armor -> Leather Armor, Heavy Leather Leggings, Heavy Leather Sleeves, Leather Helm, Studded Leather Skirts, Reinforced Boots, Leather Gloves
        if "from" in item:
            for s in item["from"]:
                if "studded leather" in s:
                    default_data["equipment"].append(leatherArmor)
                    default_data["equipment"].append(heavyLeatherLeggings)
                    default_data["equipment"].append(heavyLeatherSleeves)
                    default_data["equipment"].append(leatherHelm)
                    default_data["equipment"].append(studdedLeatherSkirts)
                    default_data["equipment"].append(reinforcedBoots)
                    default_data["equipment"].append(leatherGloves)

        # Hide Armor / Hide -> Fur Tunic, Fur Loincloth, Leather Armor, Leather Pants, Leather Helm, Reinforced Boots, Leather Gloves, Heavy Leather Sleeves, Heavy Leather Leggings
        if "from" in item:
            for s in item["from"]:
                if "hide" in s:
                    default_data["equipment"].append(furTunic)
                    default_data["equipment"].append(furLoincloth)
                    default_data["equipment"].append(leatherArmor)
                    default_data["equipment"].append(leatherPants)
                    default_data["equipment"].append(leatherHelm)
                    default_data["equipment"].append(reinforcedBoots)
                    default_data["equipment"].append(leatherGloves)
                    default_data["equipment"].append(heavyLeatherSleeves)
                    default_data["equipment"].append(heavyLeatherLeggings)

        # Padded -> Buff Coat, Leather Pants, Heavy Leather Sleeves, Leather Helm, Reinforced Boots, Leather Gloves
        if "from" in item:
            for s in item["from"]:
                if "padded" in s:
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(leatherPants)
                    default_data["equipment"].append(heavyLeatherSleeves)
                    default_data["equipment"].append(leatherHelm)
                    default_data["equipment"].append(reinforcedBoots)
                    default_data["equipment"].append(leatherGloves)

        # Shield -> Medium Shield
        if "from" in item:
            for s in item["from"]:
                if "shield" in s:
                    default_data["equipment"].append(mediumShield)

        # Scale Mail / Scale Mail Armor -> Scale Armor, Scale Leggings, Scale Sleeves, Pot Helm, Buff Coat, Leather Gloves, Reinforced Boots
        if "from" in item:
            for s in item["from"]:
                if "scale" in s:
                    default_data["equipment"].append(scaleArmor)
                    default_data["equipment"].append(scaleLeggings)
                    default_data["equipment"].append(scaleSleeves)
                    default_data["equipment"].append(steelPot)
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(leatherGloves)
                    default_data["equipment"].append(reinforcedBoots)

        # Chain Shirt / Chain Mail -> Mail Coif, Mail Shirt, Mail Leggings, Mail Sleeves, Pot Helm, Buff Coat, Leather Gloves, Reinforced Boots
        if "from" in item:
            for s in item["from"]:
                if "chain" in s:
                    default_data["equipment"].append(mailCoif)
                    default_data["equipment"].append(mailShirt)
                    default_data["equipment"].append(mailLeggings)
                    default_data["equipment"].append(mailSleeves)
                    default_data["equipment"].append(steelPot)
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(leatherGloves)
                    default_data["equipment"].append(reinforcedBoots)

        # Breastplate / Breastplate Armor -> Breastplate, Mail Leggings, Mail Sleeves, Pot Helm, Buff Coat, Leather Gloves, Reinforced Boots
        if "from" in item:
            for s in item["from"]:
                if "breastplate" in s:
                    default_data["equipment"].append(steelBreastPlate)
                    default_data["equipment"].append(mailLeggings)
                    default_data["equipment"].append(mailSleeves)
                    default_data["equipment"].append(steelPot)
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(leatherGloves)
                    default_data["equipment"].append(reinforcedBoots)
                    print("Test")

        # Half Plate Armor / Half Plate -> Steel Corselet, Mail Sleeves, Pot Helm, Mail Coif, Buff Coat, Gauntlets, Mail Leggings, Sollerets
        if "from" in item:
            for s in item["from"]:
                if "half plate" in s:
                    default_data["equipment"].append(steelCorselet)
                    default_data["equipment"].append(mailSleeves)
                    default_data["equipment"].append(steelPot)
                    default_data["equipment"].append(mailCoif)
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(gauntlets)
                    default_data["equipment"].append(mailLeggings)
                    default_data["equipment"].append(sollerets)

        # Splint Armor / Splint Mail / SplintMail -> Steel Corselet, Plate Arms, Plate Legs, Sollerets, Gauntlets, Mail Hauberk, Buff Coat, Barrel Helm
        if "from" in item:
            for s in item["from"]:
                if "splint" in s:
                    default_data["equipment"].append(steelCorselet)
                    default_data["equipment"].append(plateArms)
                    default_data["equipment"].append(plateLegs)
                    default_data["equipment"].append(sollerets)
                    default_data["equipment"].append(gauntlets)
                    default_data["equipment"].append(mailHauberk)
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(barrelHelm)

        # Plate Mail / Plate Mail Armor / Plate / Plate Armor -> Heavy Steel Corselet, Heavy Plate Arms, Heavy Plate Legs, Sollerets, Heavy Gauntlets, Mail Hauberk, Buff Coat, Mail Leggings, Mail Sleeves, Great Helm
        if "from" in item:
            for s in item["from"]:
                if "plate" in s:
                    default_data["equipment"].append(heavySteelCorselet)
                    default_data["equipment"].append(heavyPlateArms)
                    default_data["equipment"].append(heavyPlateLegs)
                    default_data["equipment"].append(sollerets)
                    default_data["equipment"].append(heavyGauntlets)
                    default_data["equipment"].append(mailHauberk)
                    default_data["equipment"].append(buffCoat)
                    default_data["equipment"].append(mailLeggings)
                    default_data["equipment"].append(mailSleeves)
                    default_data["equipment"].append(greatHelm)

    # Add resistances
    if "resist" in input_data:
        for res in input_data["resist"]:
            limDamageResistance = {
                "id": str(uuid.uuid4()),
                "type": "trait",
                "name": "Damage Resistance (0.5x)",
                "notes": "Limited (Fire)",
                "userdesc": "Half All Damage That Passed DR",
                "base_points": 20,
                "calc": {"points": 20},
            }
            # cold
            if "cold" in res:
                limDamageResistance["notes"] = "Limited (Cold)"
                default_data["traits"].append(limDamageResistance)
            # fire
            elif "fire" in res:
                limDamageResistance["notes"] = "Limited (Fire)"
                default_data["traits"].append(limDamageResistance)
            # poison
            elif "poison" in res:
                limDamageResistance["notes"] = "Limited (Poison)"
                default_data["traits"].append(limDamageResistance)
            # acid
            elif "acid" in res:
                limDamageResistance["notes"] = "Limited (Acid)"
                default_data["traits"].append(limDamageResistance)
            # lightning
            elif "lightning" in res:
                limDamageResistance["notes"] = "Limited (Lightning)"
                default_data["traits"].append(limDamageResistance)
            # necrotic
            elif "necrotic" in res:
                limDamageResistance["notes"] = "Limited (Necrotic)"
                default_data["traits"].append(limDamageResistance)
            # radiant
            elif "radiant" in res:
                limDamageResistance["notes"] = "Limited (Radiant)"
                default_data["traits"].append(limDamageResistance)
            # thunder
            elif "thunder" in res:
                limDamageResistance["notes"] = "Limited (Thunder)"
                default_data["traits"].append(limDamageResistance)
            # force
            elif "force" in res:
                limDamageResistance["notes"] = "Limited (Force)"
                default_data["traits"].append(limDamageResistance)
            # psychic
            elif "psychic" in res:
                limDamageResistance["notes"] = "Limited (Psychic)"
                default_data["traits"].append(limDamageResistance)
            # bludgeoning
            elif "bludgeoning" in res:
                limDamageResistance["notes"] = "Limited (Crushing)"
                default_data["traits"].append(limDamageResistance)
            # piercing
            elif "piercing" in res:
                limDamageResistance["notes"] = "Limited (Impaling and Piercing)"
                default_data["traits"].append(limDamageResistance)
            # slashing
            elif "slashing" in res:
                limDamageResistance["notes"] = "Limited (Cutting)"
                default_data["traits"].append(limDamageResistance)
            # bludgeoning, piercing, and slashing
            elif isinstance(res, dict) and "resist" in res:
                # Check if the value of 'resist' is a list that contains "bludgeoning", "piercing", "slashing"
                if set(["bludgeoning", "piercing", "slashing"]).issubset(res["resist"]):
                    limDamageResistance[
                        "notes"
                    ] = "Limited (Crushing, Impaling, Piercing, and Cutting From Nonmagical Weapons)"
                    default_data["traits"].append(limDamageResistance)

    # add immunities
    if "immune" in input_data:
        for imm in input_data["immune"]:
            immunity = {
                "id": str(uuid.uuid4()),
                "type": "trait",
                "name": "Damage Immunity",
                "notes": "Limited (Fire)",
                "base_points": 50,
                "calc": {"points": 50},
            }
            # cold
            if "cold" in imm:
                immunity["notes"] = "Limited (Cold)"
                default_data["traits"].append(immunity)
            # fire
            elif "fire" in imm:
                immunity["notes"] = "Limited (Fire)"
                default_data["traits"].append(immunity)
            # poison
            elif "poison" in imm:
                immunity["notes"] = "Limited (Poison)"
                default_data["traits"].append(immunity)
            # acid
            elif "acid" in imm:
                immunity["notes"] = "Limited (Acid)"
                default_data["traits"].append(immunity)
            # lightning
            elif "lightning" in imm:
                immunity["notes"] = "Limited (Lightning)"
                default_data["traits"].append(immunity)
            # necrotic
            elif "necrotic" in imm:
                immunity["notes"] = "Limited (Necrotic)"
                default_data["traits"].append(immunity)
            # radiant
            elif "radiant" in imm:
                immunity["notes"] = "Limited (Radiant)"
                default_data["traits"].append(immunity)
            # thunder
            elif "thunder" in imm:
                immunity["notes"] = "Limited (Thunder)"
                default_data["traits"].append(immunity)
            # force
            elif "force" in imm:
                immunity["notes"] = "Limited (Force)"
                default_data["traits"].append(immunity)
            # psychic
            elif "psychic" in imm:
                immunity["notes"] = "Limited (Psychic)"
                default_data["traits"].append(immunity)
            # bludgeoning
            elif "bludgeoning" in imm:
                immunity["notes"] = "Limited (Crushing)"
                default_data["traits"].append(immunity)
            # piercing
            elif "piercing" in imm:
                immunity["notes"] = "Limited (Piercing and Impaling)"
                default_data["traits"].append(immunity)
            # slashing
            elif "slashing" in imm:
                immunity["notes"] = "Limited (Cutting)"
                default_data["traits"].append(immunity)
            # bludgeoning, piercing, slashing
            elif isinstance(imm, dict) and "resist" in imm:
                # Check if the value of 'resist' is a list that contains "bludgeoning", "piercing", "slashing"
                if set(["bludgeoning", "piercing", "slashing"]).issubset(imm["immune"]):
                    immunity[
                        "notes"
                    ] = "Limited (Crushing, Piercing, Impaling, and Cutting From Nonmagical Weapons)"
                    default_data["traits"].append(immunity)

    # Add Traits
    if "trait" in input_data:
        for trait in input_data["trait"]:
            if trait["name"] == "Nimble Escape":
                nimble_escape_trait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "Nimble Escape",
                    "notes": "Description",
                    "base_points": 5,
                    "calc": {"points": 5},
                }
                nimble_escape_trait["notes"] = (
                    "The "
                    + creature_name
                    + " does not have a limit on the number of times it can use the Retreat active defense and can take 2 steps during a Retreat. The creatures step action size also becomes a minimum of 2 yards."
                )
                default_data["traits"].append(nimble_escape_trait)
            else:
                newTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "Trait Name",
                    "notes": "Description",
                    "base_points": 5,
                    "calc": {"points": 5},
                }
                newTrait["name"] = trait["name"]
                description = trait["entries"][0]
                newTrait["notes"] = convert_to_gurps(description)
                default_data["traits"].append(newTrait)

    # Spellcasting
    if "spellcasting" in input_data:
        newTrait = {
            "id": str(uuid.uuid4()),
            "type": "trait",
            "name": "Trait Name",
            "notes": "Description",
            "base_points": 5,
            "calc": {"points": 5},
        }
        if input_data["spellcasting"][0]["name"] == "Innate Spellcasting":
            newTrait["name"] = "Innate Spellcasting"
            description = convert_to_gurps(
                input_data["spellcasting"][0]["headerEntries"][0]
            )
            if "will" in input_data["spellcasting"][0]:
                description = (
                    description
                    + "\nAt Will: "
                    + convert_to_gurps(str(input_data["spellcasting"][0]["will"]))
                )
            if "daily" in input_data["spellcasting"][0]:
                description = (
                    description
                    + "\nDaily: "
                    + convert_to_gurps(str(input_data["spellcasting"][0]["daily"]))
                )
            newTrait["notes"] = description
            default_data["traits"].append(newTrait)
        else:
            newTrait["name"] = "Spellcasting"
            description = ""
            if "0" in input_data["spellcasting"][0]["spells"]:
                description = description + "0: "
                for spell in input_data["spellcasting"][0]["spells"]["0"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "1" in input_data["spellcasting"][0]["spells"]:
                description = description + "1: "
                for spell in input_data["spellcasting"][0]["spells"]["1"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "2" in input_data["spellcasting"][0]["spells"]:
                description = description + "2: "
                for spell in input_data["spellcasting"][0]["spells"]["2"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "3" in input_data["spellcasting"][0]["spells"]:
                description = description + "3: "
                for spell in input_data["spellcasting"][0]["spells"]["3"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "4" in input_data["spellcasting"][0]["spells"]:
                description = description + "4: "
                for spell in input_data["spellcasting"][0]["spells"]["4"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "5" in input_data["spellcasting"][0]["spells"]:
                description = description + "5: "
                for spell in input_data["spellcasting"][0]["spells"]["5"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "6" in input_data["spellcasting"][0]["spells"]:
                description = description + "6: "
                for spell in input_data["spellcasting"][0]["spells"]["6"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "7" in input_data["spellcasting"][0]["spells"]:
                description = description + "7: "
                for spell in input_data["spellcasting"][0]["spells"]["7"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "8" in input_data["spellcasting"][0]["spells"]:
                description = description + "8: "
                for spell in input_data["spellcasting"][0]["spells"]["8"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
                description = description[:-2] + "\n"
            if "9" in input_data["spellcasting"][0]["spells"]:
                description = description + "9: "
                for spell in input_data["spellcasting"][0]["spells"]["9"]["spells"]:
                    # remove {@ from begginging of spell and } from end of spell
                    description = description + spell[8:-1] + ", "
            newTrait["notes"] = description
            default_data["traits"].append(newTrait)

    # Add Actions
    profPoints = convert_modifier_to_points(profBonus)
    if "action" in input_data:
        for action in input_data["action"]:
            # Dagger -> Knife Skill, Knife Equipment
            if action["name"] == "Dagger":
                # region Knife Skill
                knifeSkill = {
                    "id": "5ea7070f-c321-48cf-83c2-0d9d090c41a9",
                    "type": "skill",
                    "name": "Knife",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/e",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -4,
                        "level": 7,
                        "adjusted_level": 7,
                        "points": -7,
                    },
                    "defaults": [
                        {"type": "skill", "name": "Force Sword", "modifier": -3},
                        {"type": "skill", "name": "Main-Gauche", "modifier": -3},
                        {"type": "skill", "name": "Shortsword", "modifier": -3},
                        {"type": "dx", "modifier": -4},
                    ],
                    "calc": {"level": 11, "rsl": "DX+0"},
                }
                # endregion
                default_data["skills"].append(knifeSkill)

                # region Knife Equipment
                daggerEquipment = {
                    "id": "0542c749-259f-401f-b977-58fd127d2db2",
                    "type": "equipment",
                    "description": "Dagger",
                    "reference": "B272",
                    "tech_level": "1",
                    "tags": ["Melee Weapon", "Missile Weapon"],
                    "quantity": 1,
                    "value": 20,
                    "weight": "0.25 lb",
                    "weapons": [
                        {
                            "id": "7ba39755-8571-43fa-a9af-4d6cc53df929",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "-1"},
                            "strength": "5",
                            "usage": "Thrust",
                            "reach": "C",
                            "parry": "-1",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {"type": "skill", "name": "Knife"},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -3,
                                },
                                {
                                    "type": "skill",
                                    "name": "Main-Gauche",
                                    "modifier": -3,
                                },
                                {"type": "skill", "name": "Shortsword", "modifier": -3},
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 11,
                                "parry": "7",
                                "block": "No",
                                "damage": "1d-3 imp",
                            },
                        },
                        {
                            "id": "7d6f591f-516a-4cc3-92bf-8971b0537f84",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "-1"},
                            "strength": "5",
                            "usage": "Thrown",
                            "accuracy": "+0",
                            "range": "x0.5/x1",
                            "rate_of_fire": "1",
                            "shots": "T(1)",
                            "bulk": "-1",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Thrown Weapon",
                                    "specialization": "Knife",
                                },
                            ],
                            "calc": {"level": 7, "range": "5/10", "damage": "1d-3 imp"},
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 20, "extended_weight": "0.25 lb"},
                }
                # endregion
                default_data["equipment"].append(daggerEquipment)
            # Light Crossbow -> Crossbow Skill, Crossbow (str 11) equipment
            elif action["name"] == "Light Crossbow":
                # region Crossbow Skill
                crossbowSkill = {
                    "id": "d01481f1-7182-42d0-bf21-ab074ce090b2",
                    "type": "skill",
                    "name": "Crossbow",
                    "reference": "B186",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "difficulty": "dx/e",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -4,
                        "level": 7,
                        "adjusted_level": 7,
                        "points": -7,
                    },
                    "defaults": [{"type": "dx", "modifier": -4}],
                    "calc": {"level": 11, "rsl": "DX+0"},
                }
                # endregion
                default_data["skills"].append(crossbowSkill)
                # region Crossbow Equipment
                crossbowEquipment = {
                    "id": "02b33894-bf95-4d8b-81f6-2ee4ae858bb1",
                    "type": "equipment",
                    "description": "Crossbow",
                    "reference": "B276",
                    "tech_level": "2",
                    "tags": ["Missile Weapon", "UsesAmmoType:Bolt"],
                    "rated_strength": 7,
                    "quantity": 1,
                    "value": 150,
                    "weight": "6 lb",
                    "weapons": [
                        {
                            "id": "dff3833e-b0dc-4362-b65e-4628d2ba454a",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "4"},
                            "strength": "7†",
                            "accuracy": "4",
                            "range": "x20/x25",
                            "rate_of_fire": "1",
                            "shots": "1(4)",
                            "bulk": "-6",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {"type": "skill", "name": "Crossbow"},
                            ],
                            "calc": {
                                "level": 11,
                                "range": "140/175",
                                "damage": "1d+1 imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 150, "extended_weight": "6 lb"},
                }
                # endregion
                default_data["equipment"].append(crossbowEquipment)
            # Club -> Broadsword Skill, light club Equipment
            elif action["name"] == "Club":
                # region Broadsword Skill
                broadswordSkill = {
                    "id": "9bc4310b-f446-4fc5-b882-d8cce9b0918a",
                    "type": "skill",
                    "name": "Broadsword",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "skill", "name": "Force Sword", "modifier": -4},
                        {"type": "skill", "name": "Rapier", "modifier": -4},
                        {"type": "skill", "name": "Saber", "modifier": -4},
                        {"type": "skill", "name": "Shortsword", "modifier": -2},
                        {"type": "skill", "name": "Two-Handed Sword", "modifier": -4},
                        {"type": "dx", "modifier": -5},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(broadswordSkill)
                # region Light Club Equipment
                lightClubEquipment = {
                    "id": "4fd55de1-10a2-4d24-9179-27798c4a51bd",
                    "type": "equipment",
                    "description": "Light Club",
                    "reference": "B271",
                    "tech_level": "0",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 5,
                    "weight": "3 lb",
                    "weapons": [
                        {
                            "id": "3865e69a-4d81-406e-844d-e8cc2b0bcddb",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "sw", "base": "1"},
                            "strength": "10",
                            "usage": "Swung",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Broadsword"},
                                {"type": "skill", "name": "Rapier", "modifier": -4},
                                {"type": "skill", "name": "Saber", "modifier": -4},
                                {"type": "skill", "name": "Shortsword", "modifier": -2},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d+1 cr",
                            },
                        },
                        {
                            "id": "480b3768-4946-4e04-b117-3d1b843b36f3",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "thr", "base": "1"},
                            "strength": "10",
                            "usage": "Thrust",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Broadsword"},
                                {"type": "skill", "name": "Rapier", "modifier": -4},
                                {"type": "skill", "name": "Saber", "modifier": -4},
                                {"type": "skill", "name": "Shortsword", "modifier": -2},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d-1 cr",
                            },
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 5, "extended_weight": "3 lb"},
                }
                # endregion
                default_data["equipment"].append(lightClubEquipment)
            # Scimitar or Shortsword -> Shortsword Skill, Shortsword Equipment
            elif action["name"] == "Scimitar" or action["name"] == "Shortsword":
                # region Shortsword Skill
                shortswordSkill = {
                    "id": "360f5f71-5201-47a5-a511-af7159565b9c",
                    "type": "skill",
                    "name": "Shortsword",
                    "reference": "B209",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "skill", "name": "Broadsword", "modifier": -2},
                        {"type": "skill", "name": "Force Sword", "modifier": -4},
                        {"type": "skill", "name": "Jitte/Sai", "modifier": -3},
                        {"type": "skill", "name": "Knife", "modifier": -4},
                        {"type": "skill", "name": "Saber", "modifier": -4},
                        {"type": "skill", "name": "Smallsword", "modifier": -4},
                        {"type": "skill", "name": "Tonfa", "modifier": -3},
                        {"type": "dx", "modifier": -5},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(shortswordSkill)
                # region Shortsword Equipment
                shortswordEquipment = {
                    "id": "dd4eb08c-679a-4e4b-834e-8d610f4d64cf",
                    "type": "equipment",
                    "description": "Shortsword",
                    "reference": "B273",
                    "tech_level": "2",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 400,
                    "weight": "2 lb",
                    "weapons": [
                        {
                            "id": "12c9f475-1517-434b-9a98-b89941370fd2",
                            "type": "melee_weapon",
                            "damage": {"type": "cut", "st": "sw"},
                            "strength": "8",
                            "usage": "Swung",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Shortsword"},
                                {"type": "skill", "name": "Broadsword", "modifier": -2},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Jitte/Sai", "modifier": -3},
                                {"type": "skill", "name": "Knife", "modifier": -4},
                                {"type": "skill", "name": "Saber", "modifier": -4},
                                {"type": "skill", "name": "Smallsword", "modifier": -4},
                                {"type": "skill", "name": "Tonfa", "modifier": -3},
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d cut",
                            },
                        },
                        {
                            "id": "c0366cd4-e9df-4ea5-b114-3fa3850b6dd5",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr"},
                            "strength": "8",
                            "usage": "Thrust",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Shortsword"},
                                {"type": "skill", "name": "Broadsword", "modifier": -2},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Jitte/Sai", "modifier": -3},
                                {"type": "skill", "name": "Knife", "modifier": -4},
                                {"type": "skill", "name": "Saber", "modifier": -4},
                                {"type": "skill", "name": "Smallsword", "modifier": -4},
                                {"type": "skill", "name": "Tonfa", "modifier": -3},
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d-2 imp",
                            },
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 400, "extended_weight": "2 lb"},
                }
                # endregion
                default_data["equipment"].append(shortswordEquipment)
            # Greataxe or Great Axe -> Two-Handed Axe/Mace Skill, Great Axe Equipment
            elif action["name"] == "Greataxe" or action["name"] == "Great Axe":
                # region Two-Handed Axe/Mace Skill
                twoHandedAxeMaceSkill = {
                    "id": "0f2e8a3a-8fb5-427d-8490-2233e3fa664e",
                    "type": "skill",
                    "name": "Two-Handed Axe/Mace",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Axe/Mace", "modifier": -3},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Two-Handed Flail", "modifier": -4},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(twoHandedAxeMaceSkill)
                # region Greate Axe Equipment
                greatAxeEquipment = {
                    "id": "459ab90c-7aab-4cf6-9613-32e582ac6b8d",
                    "type": "equipment",
                    "description": "Great Axe",
                    "reference": "B274",
                    "tech_level": "1",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 100,
                    "weight": "8 lb",
                    "weapons": [
                        {
                            "id": "f6860129-d553-43d0-a82a-3bae8210a992",
                            "type": "melee_weapon",
                            "damage": {"type": "cut", "st": "sw", "base": "3"},
                            "strength": "12‡",
                            "usage": "Swung",
                            "reach": "1,2*",
                            "parry": "0U",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Two-Handed Axe/Mace"},
                                {"type": "skill", "name": "Axe/Mace", "modifier": -3},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Flail",
                                    "modifier": -4,
                                },
                            ],
                            "calc": {
                                "level": 8,
                                "parry": "7U",
                                "block": "No",
                                "damage": "1d+3 cut",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 100, "extended_weight": "8 lb"},
                }
                # endregion
                default_data["equipment"].append(greatAxeEquipment)
            # Hand Crossbow -> Crossbow Skill, Pistol Crossbow Equipment
            elif action["name"] == "Hand Crossbow":
                # region Crossbow Skill
                crossbowSkill = {
                    "id": "d01481f1-7182-42d0-bf21-ab074ce090b2",
                    "type": "skill",
                    "name": "Crossbow",
                    "reference": "B186",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "difficulty": "dx/e",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -4,
                        "level": 7,
                        "adjusted_level": 7,
                        "points": -7,
                    },
                    "defaults": [{"type": "dx", "modifier": -4}],
                    "calc": {"level": 11, "rsl": "DX+0"},
                }
                # endregion
                default_data["skills"].append(crossbowSkill)
                # region Hand Crossbow Equipment
                handCrossbowEquipment = {
                    "id": "00941d41-0574-4d80-a6a3-54f2586b2cca",
                    "type": "equipment",
                    "description": "Pistol Crossbow",
                    "reference": "B276",
                    "tech_level": "3",
                    "tags": ["Missile Weapon", "UsesAmmoType:Bolt"],
                    "rated_strength": 7,
                    "quantity": 1,
                    "value": 150,
                    "weight": "4 lb",
                    "weapons": [
                        {
                            "id": "5e3257b7-30d3-431d-8f2a-e6bc491f02e2",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "2"},
                            "strength": "7",
                            "accuracy": "1",
                            "range": "x15/x20",
                            "rate_of_fire": "1",
                            "shots": "1(4)",
                            "bulk": "-4",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {"type": "skill", "name": "Crossbow"},
                            ],
                            "calc": {
                                "level": 7,
                                "range": "105/140",
                                "damage": "1d-1 imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 150, "extended_weight": "4 lb"},
                }
                # endregion
                default_data["equipment"].append(handCrossbowEquipment)
            # Heavy Crossbow -> Crossbow Skill, Heavy Crossbow Equipment
            elif action["name"] == "Heavy Crossbow":
                # region Crossbow Skill
                crossbowSkill = {
                    "id": "d01481f1-7182-42d0-bf21-ab074ce090b2",
                    "type": "skill",
                    "name": "Crossbow",
                    "reference": "B186",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "difficulty": "dx/e",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -4,
                        "level": 7,
                        "adjusted_level": 7,
                        "points": -7,
                    },
                    "defaults": [{"type": "dx", "modifier": -4}],
                    "calc": {"level": 11, "rsl": "DX+0"},
                }
                # endregion
                default_data["skills"].append(crossbowSkill)
                # region Heavy Crossbow Equipment
                heavyCrossbowEquipment = {
                    "id": "86cc2a19-4adf-4dd2-8ce7-c798946f1035",
                    "type": "equipment",
                    "description": "Military Crossbow",
                    "reference": "LT74",
                    "notes": "Steel crossbow (See LT78, Note 6)",
                    "tech_level": "4",
                    "tags": ["Missile Weapon"],
                    "quantity": 1,
                    "value": 750,
                    "weight": "15 lb",
                    "weapons": [
                        {
                            "id": "d0a00dea-04b6-4381-a827-13d8553dbd66",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "5"},
                            "strength": "12†",
                            "usage": "Fire Bolt",
                            "accuracy": "4",
                            "range": "x25/x30",
                            "rate_of_fire": "1",
                            "shots": "1(32)",
                            "bulk": "-6",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {"type": "skill", "name": "Crossbow"},
                            ],
                            "calc": {
                                "level": 12,
                                "range": "300/360",
                                "damage": "1d+4 imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 750, "extended_weight": "15 lb"},
                }
                # endregion
                default_data["equipment"].append(heavyCrossbowEquipment)
            # Spear -> Spear Skill, Spear Equipment
            elif action["name"] == "Spear":
                # region Spear Skill
                spearSkill = {
                    "id": "71d611f4-adef-4c59-9e29-7828a5832a64",
                    "type": "skill",
                    "name": "Spear",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Staff", "modifier": -2},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(spearSkill)
                # region Spear Equipment
                spearEquipment = {
                    "id": "25ddaedf-0710-4902-8eb3-36885c64219a",
                    "type": "equipment",
                    "description": "Spear",
                    "reference": "B273",
                    "tech_level": "0",
                    "tags": ["Melee Weapon", "Missile Weapon"],
                    "quantity": 1,
                    "value": 40,
                    "weight": "4 lb",
                    "weapons": [
                        {
                            "id": "a0ab4b29-3d89-4e1a-b631-242a5dd9061a",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "2"},
                            "strength": "9",
                            "usage": "Thrust",
                            "reach": "1*",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Spear"},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {"type": "skill", "name": "Staff", "modifier": -2},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d+1 imp",
                            },
                        },
                        {
                            "id": "c08a3872-56ac-438a-91af-b5164b8af563",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "3"},
                            "strength": "9†",
                            "usage": "Thrust",
                            "reach": "1,2*",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Spear"},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {"type": "skill", "name": "Staff", "modifier": -2},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d+2 imp",
                            },
                        },
                        {
                            "id": "144a40da-e63e-47c5-86df-45782f6c5c35",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "3"},
                            "strength": "9",
                            "usage": "Thrown",
                            "accuracy": "+2",
                            "range": "x1/x1.5",
                            "rate_of_fire": "1",
                            "shots": "T(1)",
                            "bulk": "-6",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Thrown Weapon",
                                    "specialization": "Spear",
                                },
                                {
                                    "type": "skill",
                                    "name": "Spear Thrower",
                                    "modifier": -4,
                                },
                                {
                                    "type": "skill",
                                    "name": "Thrown Weapon",
                                    "specialization": "Harpoon",
                                    "modifier": -2,
                                },
                            ],
                            "calc": {
                                "level": 7,
                                "range": "12/18",
                                "damage": "1d+2 imp",
                            },
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 40, "extended_weight": "4 lb"},
                }
                # endregion
                default_data["equipment"].append(spearEquipment)
            # Javelin -> Spear Skill, Spear Throw Skill, Javelin Equipment
            elif action["name"] == "Javelin":
                # region Spear Skill
                spearSkill = {
                    "id": "71d611f4-adef-4c59-9e29-7828a5832a64",
                    "type": "skill",
                    "name": "Spear",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Staff", "modifier": -2},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(spearSkill)
                # region Spear Throw Skill
                spearThrowSkill = {
                    "id": "4f5ec478-8673-40ba-9a08-b6650b523ed3",
                    "type": "skill",
                    "name": "Thrown Weapon",
                    "reference": "B226",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "specialization": "Spear",
                    "difficulty": "dx/e",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -4,
                        "level": 7,
                        "adjusted_level": 7,
                        "points": -7,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -4},
                        {"type": "skill", "name": "Spear Thrower", "modifier": -4},
                        {
                            "type": "skill",
                            "name": "Thrown Weapon",
                            "specialization": "Harpoon",
                            "modifier": -2,
                        },
                    ],
                    "calc": {"level": 11, "rsl": "DX+0"},
                }
                # endregion
                default_data["skills"].append(spearThrowSkill)
                # region Javelin Equipment
                javelinEquipment = {
                    "id": "c08950a3-f4ca-40ba-9ed2-995dbe78ade1",
                    "type": "equipment",
                    "description": "Javelin",
                    "reference": "B273",
                    "tech_level": "1",
                    "tags": ["AmmoType:Javelin", "Melee Weapon", "Missile Weapon"],
                    "quantity": 1,
                    "value": 30,
                    "weight": "2 lb",
                    "weapons": [
                        {
                            "id": "707acb6e-2ee2-49ae-a12d-86e8a805256b",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "1"},
                            "strength": "6",
                            "usage": "Thrust",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Spear"},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {"type": "skill", "name": "Staff", "modifier": -2},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d imp",
                            },
                        },
                        {
                            "id": "fb94724e-fb6c-48d9-85b2-5c95a3a66a53",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "1"},
                            "strength": "6",
                            "usage": "Thrown",
                            "accuracy": "+3",
                            "range": "x1.5/x2.5",
                            "rate_of_fire": "1",
                            "shots": "T(1)",
                            "bulk": "-4",
                            "defaults": [
                                {"type": "dx", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Thrown Weapon",
                                    "specialization": "Spear",
                                },
                                {
                                    "type": "skill",
                                    "name": "Spear Thrower",
                                    "modifier": -4,
                                },
                                {
                                    "type": "skill",
                                    "name": "Thrown Weapon",
                                    "specialization": "Harpoon",
                                    "modifier": -2,
                                },
                            ],
                            "calc": {"level": 11, "range": "18/30", "damage": "1d imp"},
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 30, "extended_weight": "2 lb"},
                }
                # endregion
                default_data["equipment"].append(javelinEquipment)
            # Longsword / Long Sword -> Broadsword Skill, Broadsword Equipment
            elif action["name"] == "Longsword" or action["name"] == "Long Sword":
                # region Broadsword Skill
                broadswordSkill = {
                    "id": "2041b1b5-68df-4978-bf0e-c09dcb997a73",
                    "type": "skill",
                    "name": "Broadsword",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "skill", "name": "Force Sword", "modifier": -4},
                        {"type": "skill", "name": "Rapier", "modifier": -4},
                        {"type": "skill", "name": "Saber", "modifier": -4},
                        {"type": "skill", "name": "Shortsword", "modifier": -2},
                        {"type": "skill", "name": "Two-Handed Sword", "modifier": -4},
                        {"type": "dx", "modifier": -5},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(broadswordSkill)
                # region Broadsword Equipment
                broadswordEquipment = {
                    "id": "8df98dbb-c1d5-4cc9-83a1-350fba6aaa1c",
                    "type": "equipment",
                    "description": "Broadsword",
                    "reference": "B271",
                    "tech_level": "2",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 500,
                    "weight": "3 lb",
                    "weapons": [
                        {
                            "id": "294c4e7e-c390-4660-8c70-008dba5dad1a",
                            "type": "melee_weapon",
                            "damage": {"type": "cut", "st": "sw", "base": "1"},
                            "strength": "10",
                            "usage": "Swung",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Broadsword"},
                                {"type": "skill", "name": "Rapier", "modifier": -4},
                                {"type": "skill", "name": "Saber", "modifier": -4},
                                {"type": "skill", "name": "Shortsword", "modifier": -2},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d+3 cut",
                            },
                        },
                        {
                            "id": "43ac8fd1-cfdf-4c93-8850-d276f4987761",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "thr", "base": "1"},
                            "strength": "10",
                            "usage": "Thrust",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Broadsword"},
                                {"type": "skill", "name": "Rapier", "modifier": -4},
                                {"type": "skill", "name": "Saber", "modifier": -4},
                                {"type": "skill", "name": "Shortsword", "modifier": -2},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d cr",
                            },
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 500, "extended_weight": "3 lb"},
                }
                # endregion
                default_data["equipment"].append(broadswordEquipment)
            # Longbow -> Longbow equipment, Bow Skill
            elif action["name"] == "Longbow":
                # region Longbow equipment
                longbowEquipment = {
                    "id": "99bbf283-906b-4993-8eb1-78ed83a4e61f",
                    "type": "equipment",
                    "description": "Longbow",
                    "reference": "B275",
                    "tech_level": "0",
                    "tags": ["Missile Weapon", "UsesAmmoType:Arrow"],
                    "rated_strength": 11,
                    "quantity": 1,
                    "value": 200,
                    "weight": "3 lb",
                    "weapons": [
                        {
                            "id": "8759c6ab-39fa-475c-9378-5329ad63a91c",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "2"},
                            "strength": "11†",
                            "accuracy": "3",
                            "range": "x15/x20",
                            "rate_of_fire": "1",
                            "shots": "1(2)",
                            "bulk": "-8",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Bow"},
                            ],
                            "calc": {
                                "level": 10,
                                "range": "165/220",
                                "damage": "1d+1 imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 200, "extended_weight": "3 lb"},
                }
                # endregion
                default_data["equipment"].append(longbowEquipment)
                # region Bow Skill
                bowSkill = {
                    "id": "41a2c7dd-3283-4782-a7d8-20e85ff1d368",
                    "type": "skill",
                    "name": "Bow",
                    "reference": "B182",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [{"type": "dx", "modifier": -5}],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(bowSkill)
            # Shortbow -> Shortbow equipment, Bow Skill
            elif action["name"] == "Shortbow":
                # region Shortbow equipment
                shortbowEquipment = {
                    "id": "99bbf283-906b-4993-8eb1-78ed83a4e61f",
                    "type": "equipment",
                    "description": "Longbow",
                    "reference": "B275",
                    "tech_level": "0",
                    "tags": ["Missile Weapon", "UsesAmmoType:Arrow"],
                    "rated_strength": 11,
                    "quantity": 1,
                    "value": 200,
                    "weight": "3 lb",
                    "weapons": [
                        {
                            "id": "8759c6ab-39fa-475c-9378-5329ad63a91c",
                            "type": "ranged_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "2"},
                            "strength": "11†",
                            "accuracy": "3",
                            "range": "x15/x20",
                            "rate_of_fire": "1",
                            "shots": "1(2)",
                            "bulk": "-8",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Bow"},
                            ],
                            "calc": {
                                "level": 10,
                                "range": "165/220",
                                "damage": "1d+1 imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 200, "extended_weight": "3 lb"},
                }
                # endregion
                default_data["equipment"].append(shortbowEquipment)
                # region Bow Skill
                bowSkill = {
                    "id": "41a2c7dd-3283-4782-a7d8-20e85ff1d368",
                    "type": "skill",
                    "name": "Bow",
                    "reference": "B182",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [{"type": "dx", "modifier": -5}],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(bowSkill)
            # Rapier -> Rapier Skill, Rapier Equipment
            elif action["name"] == "Rapier":
                # region Rapier Skill
                rapierSkill = {
                    "id": "cd367975-81e9-4869-ac6d-e716f9188339",
                    "type": "skill",
                    "name": "Rapier",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Broadsword", "modifier": -4},
                        {"type": "skill", "name": "Main-Gauche", "modifier": -3},
                        {"type": "skill", "name": "Saber", "modifier": -3},
                        {"type": "skill", "name": "Smallsword", "modifier": -3},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(rapierSkill)
                # region Rapier Equipment
                rapierEquipment = {
                    "id": "a8baa8c1-8cd5-497c-a4e8-e6ac5b038f80",
                    "type": "equipment",
                    "description": "Rapier",
                    "reference": "B273",
                    "tech_level": "4",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 500,
                    "weight": "2.75 lb",
                    "weapons": [
                        {
                            "id": "faed2269-9c35-4b6c-b478-4d353e824920",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "1"},
                            "strength": "9",
                            "usage": "Thrust",
                            "reach": "1,2",
                            "parry": "0F",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Rapier"},
                                {"type": "skill", "name": "Broadsword", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Main-Gauche",
                                    "modifier": -3,
                                },
                                {"type": "skill", "name": "Saber", "modifier": -3},
                                {"type": "skill", "name": "Smallsword", "modifier": -3},
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8F",
                                "block": "No",
                                "damage": "1d imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 500, "extended_weight": "2.75 lb"},
                }
                # endregion
                default_data["equipment"].append(rapierEquipment)
            # Greatclub or Great Club -> Axe/Mace Skill, Knobbed Club Equipment
            elif action["name"] == "Greatclub" or action["name"] == "Great Club":
                # region Axe/Mace Skill
                axeMaceSkill = {
                    "id": "9a8f4d0c-b66b-4605-a01f-e3534c2fd006",
                    "type": "skill",
                    "name": "Axe/Mace",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {
                            "type": "skill",
                            "name": "Two-Handed Axe/Mace",
                            "modifier": -3,
                        },
                        {"type": "skill", "name": "Flail", "modifier": -4},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(axeMaceSkill)
                # region Knobbed Club Equipment
                knobbedClubEquipment = {
                    "id": "8e7ed5b8-fed2-4c1f-a3f5-023bc19fde02",
                    "type": "equipment",
                    "description": "Knobbed Club",
                    "reference": "LT58",
                    "tech_level": "0",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 20,
                    "weight": "2 lb",
                    "weapons": [
                        {
                            "id": "9bbcb7f6-447b-4905-a888-9a3834c5bb4d",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "sw", "base": "1"},
                            "strength": "8",
                            "usage": "Swung",
                            "reach": "1",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Axe/Mace"},
                                {"type": "skill", "name": "Flail", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Axe/Mace",
                                    "modifier": -3,
                                },
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8",
                                "block": "No",
                                "damage": "1d+3 cr",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 20, "extended_weight": "2 lb"},
                }
                # endregion
                default_data["equipment"].append(knobbedClubEquipment)
            # Sling -> Sling Equipment, Sling Skill
            elif action["name"] == "Sling":
                # region Sling Equipment
                slingEquipment = {
                    "id": "7288b4d9-0c11-4b09-8ad4-e781cb5e13b9",
                    "type": "equipment",
                    "description": "Sling",
                    "reference": "B276",
                    "tech_level": "0",
                    "tags": ["Missile Weapon", "UsesAmmoType:Sling"],
                    "quantity": 1,
                    "value": 20,
                    "weight": "0.5 lb",
                    "weapons": [
                        {
                            "id": "b566ba0b-ea56-4701-8f84-186385028e7b",
                            "type": "ranged_weapon",
                            "damage": {"type": "pi", "st": "sw"},
                            "strength": "6",
                            "accuracy": "0",
                            "range": "x6/x10",
                            "rate_of_fire": "1",
                            "shots": "1(2)",
                            "bulk": "-4",
                            "defaults": [
                                {"type": "dx", "modifier": -6},
                                {"type": "skill", "name": "Sling"},
                            ],
                            "calc": {
                                "level": 9,
                                "range": "72/120",
                                "damage": "1d+2 pi",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 20, "extended_weight": "0.5 lb"},
                }
                # endregion
                default_data["equipment"].append(slingEquipment)
                # region Sling Skill
                slingSkill = {
                    "id": "eecbbb0c-c1a9-4c8a-b536-62ccd2f1109d",
                    "type": "skill",
                    "name": "Sling",
                    "reference": "B221",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "difficulty": "dx/h",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -6,
                        "level": 5,
                        "adjusted_level": 5,
                        "points": -5,
                    },
                    "defaults": [{"type": "dx", "modifier": -6}],
                    "calc": {"level": 9, "rsl": "DX-2"},
                }
                # endregion
                default_data["skills"].append(slingSkill)
            # Quarterstaff or Staff or Quarter Staff -> Staff Skill, Quarterstaff Equipment
            elif (
                action["name"] == "Quarterstaff"
                or action["name"] == "Staff"
                or action["name"] == "Quarter Staff"
            ):
                # region Staff Skill
                staffSkill = {
                    "id": "c1704e0f-ba0b-4896-8a7b-f93e2762f8c2",
                    "type": "skill",
                    "name": "Staff",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Spear", "modifier": -2},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(staffSkill)
                # region Quarterstaff Equipment
                quarterstaffEquipment = {
                    "id": "49b5ba32-584f-4b8f-97b9-f3f5415b4a6c",
                    "type": "equipment",
                    "description": "Quarterstaff",
                    "reference": "B273",
                    "tech_level": "0",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 10,
                    "weight": "4 lb",
                    "weapons": [
                        {
                            "id": "ad65dc1c-caf5-4c71-a880-84587832d8ea",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "sw", "base": "2"},
                            "strength": "7†",
                            "usage": "Swung",
                            "usage_notes": "Staff",
                            "reach": "1,2",
                            "parry": "+2",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Staff"},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {"type": "skill", "name": "Spear", "modifier": -2},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "10",
                                "block": "No",
                                "damage": "1d+4 cr",
                            },
                        },
                        {
                            "id": "0f333350-cfd8-4fba-a202-b2bf19773be5",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "thr", "base": "2"},
                            "strength": "7†",
                            "usage": "Thrust",
                            "usage_notes": "Staff",
                            "reach": "1,2",
                            "parry": "+2",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Staff"},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {"type": "skill", "name": "Spear", "modifier": -2},
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "10",
                                "block": "No",
                                "damage": "1d+1 cr",
                            },
                        },
                        {
                            "id": "cbc835a1-cf24-479a-bd41-0e8a7b4b8c37",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "sw", "base": "2"},
                            "strength": "9†",
                            "usage": "Swung",
                            "usage_notes": "Two-Handed Sword",
                            "reach": "1,2",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Two-Handed Sword"},
                                {"type": "skill", "name": "Broadsword", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 6,
                                "parry": "6",
                                "block": "No",
                                "damage": "1d+4 cr",
                            },
                        },
                        {
                            "id": "3cb8cfdd-ea36-4144-b25e-406f4a105764",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "thr", "base": "1"},
                            "strength": "9†",
                            "usage": "Thrust",
                            "usage_notes": "Two-Handed Sword",
                            "reach": "2",
                            "parry": "0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Two-Handed Sword"},
                                {"type": "skill", "name": "Broadsword", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Force Sword",
                                    "modifier": -4,
                                },
                                {"type": "skill", "name": "Sword!"},
                            ],
                            "calc": {
                                "level": 6,
                                "parry": "6",
                                "block": "No",
                                "damage": "1d cr",
                            },
                        },
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 10, "extended_weight": "4 lb"},
                }
                # endregion
                default_data["equipment"].append(quarterstaffEquipment)
            # Maul -> Two-Handed Axe/Mace Skill, Maul Equipment
            elif action["name"] == "Maul":
                # region Two-Handed Axe/Mace Skill
                twoHandedAxeMaceSkill = {
                    "id": "0f2e8a3a-8fb5-427d-8490-2233e3fa664e",
                    "type": "skill",
                    "name": "Two-Handed Axe/Mace",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Axe/Mace", "modifier": -3},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Two-Handed Flail", "modifier": -4},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(twoHandedAxeMaceSkill)
                # region Maul Equipment
                maulEquipment = {
                    "id": "13d9287b-4699-4a62-a2b1-8b17d51b0f74",
                    "type": "equipment",
                    "description": "Maul",
                    "reference": "B274",
                    "tech_level": "0",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 80,
                    "weight": "12 lb",
                    "weapons": [
                        {
                            "id": "a381d818-2974-407e-823d-1db893882778",
                            "type": "melee_weapon",
                            "damage": {"type": "cr", "st": "sw", "base": "4"},
                            "strength": "13‡",
                            "usage": "Swung",
                            "reach": "1,2*",
                            "parry": "0U",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Two-Handed Axe/Mace"},
                                {"type": "skill", "name": "Axe/Mace", "modifier": -3},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Flail",
                                    "modifier": -4,
                                },
                            ],
                            "calc": {
                                "level": 5,
                                "parry": "5U",
                                "block": "No",
                                "damage": "1d+6 cr",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 80, "extended_weight": "12 lb"},
                }
                # endregion
                default_data["equipment"].append(maulEquipment)
            # Pike -> Spear Skill, Pike Equipment
            elif action["name"] == "Pike":
                # region Spear Skill
                spearSkill = {
                    "id": "71d611f4-adef-4c59-9e29-7828a5832a64",
                    "type": "skill",
                    "name": "Spear",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Staff", "modifier": -2},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(spearSkill)
                # region Pike Equipment
                pikeEquipment = {
                    "id": "b634189c-139f-4ee1-874a-cad639b8730b",
                    "type": "equipment",
                    "description": "Pike",
                    "reference": "LT60",
                    "tech_level": "2",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 80,
                    "weight": "13 lb",
                    "weapons": [
                        {
                            "id": "7fd9a17a-ca6b-4c11-b5df-a5851d962c6b",
                            "type": "melee_weapon",
                            "damage": {"type": "imp", "st": "thr", "base": "3"},
                            "strength": "12†",
                            "usage": "Thrust",
                            "reach": "4, 5*",
                            "parry": "0U / 0",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Spear"},
                                {"type": "skill", "name": "Polearm", "modifier": -4},
                                {"type": "skill", "name": "Staff", "modifier": -2},
                            ],
                            "calc": {
                                "level": 6,
                                "parry": "6U / 0",
                                "block": "No",
                                "damage": "1d+2 imp",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 80, "extended_weight": "13 lb"},
                }
                # endregion
                default_data["equipment"].append(pikeEquipment)
            # Hand Axe -> Axe/Mace Skill, Axe Equipment
            elif action["name"] == "Hand Axe":
                # region Axe/Mace Skill
                axeMaceSkill = {
                    "id": "8a428136-80a2-489e-9e0d-fa113e1f99cd",
                    "type": "skill",
                    "name": "Axe/Mace",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {
                            "type": "skill",
                            "name": "Two-Handed Axe/Mace",
                            "modifier": -3,
                        },
                        {"type": "skill", "name": "Flail", "modifier": -4},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(axeMaceSkill)
                # region Axe Equipment
                axeEquipment = {
                    "id": "9211d2df-bf12-4cc5-bf15-096fb119da14",
                    "type": "equipment",
                    "description": "Axe",
                    "reference": "B271",
                    "tech_level": "0",
                    "tags": ["Melee Weapon"],
                    "quantity": 1,
                    "value": 50,
                    "weight": "4 lb",
                    "weapons": [
                        {
                            "id": "50000db7-86e6-4251-aa90-cd0424209d96",
                            "type": "melee_weapon",
                            "damage": {"type": "cut", "st": "sw", "base": "2"},
                            "strength": "11",
                            "usage": "Swung",
                            "reach": "1",
                            "parry": "0U",
                            "block": "No",
                            "defaults": [
                                {"type": "dx", "modifier": -5},
                                {"type": "skill", "name": "Axe/Mace"},
                                {"type": "skill", "name": "Flail", "modifier": -4},
                                {
                                    "type": "skill",
                                    "name": "Two-Handed Axe/Mace",
                                    "modifier": -3,
                                },
                            ],
                            "calc": {
                                "level": 10,
                                "parry": "8U",
                                "block": "No",
                                "damage": "1d+4 cut",
                            },
                        }
                    ],
                    "equipped": True,
                    "calc": {"extended_value": 50, "extended_weight": "4 lb"},
                }
                # endregion
                default_data["equipment"].append(axeEquipment)
            # Trident -> Spear Skill, Spear Throw Skill, Trident Equipment
            elif action["name"] == "Trident":
                # region Spear Skill
                spearSkill = {
                    "id": "71d611f4-adef-4c59-9e29-7828a5832a64",
                    "type": "skill",
                    "name": "Spear",
                    "reference": "B208",
                    "tags": ["Combat", "Melee Combat", "Weapon"],
                    "difficulty": "dx/a",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -5,
                        "level": 6,
                        "adjusted_level": 6,
                        "points": -6,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -5},
                        {"type": "skill", "name": "Polearm", "modifier": -4},
                        {"type": "skill", "name": "Staff", "modifier": -2},
                    ],
                    "calc": {"level": 10, "rsl": "DX-1"},
                }
                # endregion
                default_data["skills"].append(spearSkill)
                # region Spear Throw Skill
                spearThrowSkill = {
                    "id": "4f5ec478-8673-40ba-9a08-b6650b523ed3",
                    "type": "skill",
                    "name": "Thrown Weapon",
                    "reference": "B226",
                    "tags": ["Combat", "Ranged Combat", "Weapon"],
                    "specialization": "Spear",
                    "difficulty": "dx/e",
                    "points": profPoints,
                    "defaulted_from": {
                        "type": "dx",
                        "modifier": -4,
                        "level": 7,
                        "adjusted_level": 7,
                        "points": -7,
                    },
                    "defaults": [
                        {"type": "dx", "modifier": -4},
                        {"type": "skill", "name": "Spear Thrower", "modifier": -4},
                        {
                            "type": "skill",
                            "name": "Thrown Weapon",
                            "specialization": "Harpoon",
                            "modifier": -2,
                        },
                    ],
                    "calc": {"level": 11, "rsl": "DX+0"},
                }
                # endregion
                default_data["skills"].append(spearThrowSkill)

                tridentEquipment = jsons.tridentEquipment
                default_data["equipment"].append(tridentEquipment)
            # Claws / Claw -> Sharp Claws
            elif action["name"] == "Claws" or action["name"] == "Claw":
                default_data["traits"].append(jsons.sharpClawsTrait)
            # Fangs -> Fangs Trait
            elif action["name"] == "Fangs":
                default_data["traits"].append(jsons.fangsTrait)
            # Bite -> Sharp Teeth Trait
            elif action["name"] == "Bite":
                default_data["traits"].append(jsons.sharpTeethTrait)
            else:
                newActionTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "action",
                    "name": "Action Name",
                    "notes": "Description",
                    "base_points": 5,
                    "calc": {"points": 5},
                }
                newActionTrait["name"] = action["name"]
                newActionTrait["notes"] = convert_to_gurps(action["entries"][0])
                default_data["traits"].append(newActionTrait)

    # Add Legendary Actions as Trait
    if "legendary" in input_data:
        for action in input_data["legendary"]:
            newActionTrait = {
                "id": str(uuid.uuid4()),
                "type": "action",
                "name": "Action Name",
                "notes": "Description",
                "base_points": 5,
                "calc": {"points": 5},
            }
            newActionTrait["name"] = action["name"]
            newActionTrait["notes"] = (
                "For 1 fp, the following can be done following the turn of another creature. "
                + convert_to_gurps(action["entries"][0])
            )
            default_data["traits"].append(newActionTrait)

    # Bonus Action
    if "bonus" in input_data:
        for action in input_data["bonus"]:
            newActionTrait = {
                "id": str(uuid.uuid4()),
                "type": "action",
                "name": "Action Name",
                "notes": "Description",
                "base_points": 5,
                "calc": {"points": 5},
            }
            newActionTrait["name"] = action["name"]
            newActionTrait["notes"] = (
                "For 1 fp do the following on your turn in addition to a maneuver. "
                + convert_to_gurps(action["entries"][0])
            )
            default_data["traits"].append(newActionTrait)

    # Reaction
    if "reaction" in input_data:
        for reaction in input_data["reaction"]:
            newActionTrait = {
                "id": str(uuid.uuid4()),
                "type": "action",
                "name": "Action Name",
                "notes": "Description",
                "base_points": 5,
                "calc": {"points": 5},
            }
            newActionTrait["name"] = reaction["name"]
            newActionTrait["notes"] = (
                "For 1 fp, the following can be done following the turn of another creature. "
                + convert_to_gurps(reaction["entries"][0])
            )
            default_data["traits"].append(newActionTrait)

    # Size and Health Benefits from Size

    # Extra Health

    # Senses
    if "senses" in input_data:
        for sense in input_data["senses"]:
            if "darkvision" in sense:
                # region Darkvision Trait
                darkvisionTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "Dark Vision",
                    "reference": "B47,P46",
                    "tags": ["Advantage", "Exotic", "Physical"],
                    "modifiers": [
                        {
                            "id": "d8886d7f-b079-4e07-9f7a-749f509e1bc0",
                            "type": "modifier",
                            "name": "Can see colors in the dark",
                            "cost": 20,
                            "disabled": True,
                        },
                        {
                            "id": "f515b6a5-62d7-4105-9622-ffc131556f64",
                            "type": "modifier",
                            "name": "Hypersensory",
                            "reference": "P46",
                            "cost": 40,
                            "disabled": True,
                        },
                    ],
                    "base_points": 25,
                    "calc": {"points": 25},
                }
                # endregion
                default_data["traits"].append(darkvisionTrait)
            elif "blindsight" in sense:
                blindsightTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "Blindsight",
                    "userdesc": "Can perceive its surroundings without relying on sight, within 60 ft.",
                    "base_points": 40,
                    "calc": {"points": 40},
                }
                default_data["traits"].append(blindsightTrait)
            elif "tremor" in sense:
                tremorsenseTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "Tremorsense",
                    "userdesc": "Can sense its surroundings via vibrations in the ground. Can automaticaly pinpoint the location of anything in contact with the ground within 60 ft.",
                    "base_points": 40,
                    "calc": {"points": 40},
                }
                default_data["traits"].append(tremorsenseTrait)
            elif "true" in sense:
                truesightTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "True Sight",
                    "userdesc": "Can see normally in magical and nonmagical darkness, see invisible creatures and objects, automatically detect visual illusions and succeed on saving throws against them, and perceive the original form of a shapechanger or a creature that is transformed by magic. Within 120 ft.",
                    "base_points": 60,
                    "calc": {"points": 60},
                }
                default_data["traits"].append(truesightTrait)
            elif "devil" in sense:
                devilssightTrait = {
                    "id": str(uuid.uuid4()),
                    "type": "trait",
                    "name": "Devil's Sight",
                    "userdesc": "Can see normally in magical and nonmagical darkness, within 120 ft.",
                    "base_points": 30,
                    "calc": {"points": 30},
                }
                default_data["traits"].append(devilssightTrait)

    # Languages
    if "languages" in input_data:
        for language in input_data["languages"]:
            # region Language Trait
            languageTrait = {
                "id": str(uuid.uuid4()),
                "type": "trait",
                "name": "Language: Any",
                "reference": "B24",
                "tags": ["Advantage", "Language", "Mental"],
                "modifiers": [
                    {
                        "id": "ff972d9a-b925-4895-a489-f3d14999074d",
                        "type": "modifier",
                        "name": "Native",
                        "reference": "B23",
                        "cost": -6,
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "e9f38c71-c4bd-45ee-a5e2-b47a33029f96",
                        "type": "modifier",
                        "name": "Spoken",
                        "reference": "B24",
                        "notes": "None",
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "6cd10ab4-c4f9-4764-a47d-0e77d105d862",
                        "type": "modifier",
                        "name": "Spoken",
                        "reference": "B24",
                        "notes": "Broken",
                        "cost": 1,
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "3c7caa3c-055e-4422-ac8e-6a2d632b391c",
                        "type": "modifier",
                        "name": "Spoken",
                        "reference": "B24",
                        "notes": "Accented",
                        "cost": 2,
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "231ba28d-11ce-44e1-8d23-074d40ca57c6",
                        "type": "modifier",
                        "name": "Spoken",
                        "reference": "B24",
                        "notes": "Native",
                        "cost": 3,
                        "cost_type": "points",
                    },
                    {
                        "id": "152ad20b-dc58-4abb-b256-71da14dbb89c",
                        "type": "modifier",
                        "name": "Written",
                        "reference": "B24",
                        "notes": "None",
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "6304a0d6-80f3-4a5f-b3cc-3ba2ae0c8063",
                        "type": "modifier",
                        "name": "Written",
                        "reference": "B24",
                        "notes": "Broken",
                        "cost": 1,
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "5818ab4a-2c4b-4c3e-a711-c4b6332daaca",
                        "type": "modifier",
                        "name": "Written",
                        "reference": "B24",
                        "notes": "Accented",
                        "cost": 2,
                        "cost_type": "points",
                        "disabled": True,
                    },
                    {
                        "id": "1b77515e-5789-49a0-8238-7242900c8c2c",
                        "type": "modifier",
                        "name": "Written",
                        "reference": "B24",
                        "notes": "Native",
                        "cost": 3,
                        "cost_type": "points",
                    },
                ],
                "calc": {"points": 6},
            }
            # endregion
            languageTrait["name"] = language
            default_data["traits"].append(languageTrait)

    # # Info
    # if "fluff" in input_data:
    #     if "entries" in input_data["fluff"]:
    #         for entry in input_data["fluff"]["entries"]:
    #             # checks if type is string
    #             if type(entry) == str:
    #                 pass
    #             else:
    #                 subsections = entry["entries"][0]
    #                 for subentry in subsections["entries"]:
    #                     description = subentry["entries"]
    #                     for paragraph in description:
    #                         pass

    # # Image
    # if "fluff" in input_data:
    #     if "images" in input_data["fluff"]:
    #         image_url = input_data["fluff"]["images"][0]["href"]["url"]
    #         pass

    # WRITE OUTPUT FILE
    with open("output.json", "w") as f:
        json.dump(default_data, f, indent=4)


# Run main function
# Ask the user if the character is battle-hardened
user_input = input("Is the character battle-hardened? (Yes/No): ")
# Load input file
with open("input.json", "r") as f:
    input = json.load(f)

# Run main function
run_convert(input, user_input)
