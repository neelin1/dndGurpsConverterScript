# region Armor
# endregion

# region EQUIPMENT
# region Trident Equipment
tridentEquipment = {
    "id": "600aabd6-678d-4ea2-9821-f4235e7874c8",
    "type": "equipment",
    "description": "Trident",
    "reference": "LT64",
    "tech_level": "2",
    "tags": ["Melee Weapon"],
    "quantity": 1,
    "value": 80,
    "weight": "5 lb",
    "weapons": [
        {
            "id": "6a91c0a5-72c1-4fbd-89d1-5f9beaa2ffed",
            "type": "melee_weapon",
            "damage": {"type": "imp", "st": "thr", "base": "3", "armor_divisor": 0.5},
            "strength": "11",
            "usage": "Thrust",
            "reach": "1*",
            "parry": "0U",
            "block": "No",
            "defaults": [
                {"type": "dx", "modifier": -5},
                {"type": "skill", "name": "Spear"},
                {"type": "skill", "name": "Polearm", "modifier": -4},
                {"type": "skill", "name": "Staff", "modifier": -2},
            ],
            "calc": {
                "level": 6,
                "parry": "6U",
                "block": "No",
                "damage": "1d+2(0.5) imp",
            },
        },
        {
            "id": "c6122b99-f1e3-4530-9539-48b592fda8c3",
            "type": "melee_weapon",
            "damage": {"type": "imp", "st": "thr", "base": "4", "armor_divisor": 0.5},
            "strength": "10†",
            "usage": " Thrust - two hands",
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
                "level": 6,
                "parry": "6",
                "block": "No",
                "damage": "1d+3(0.5) imp",
            },
        },
    ],
    "equipped": True,
    "calc": {"extended_value": 80, "extended_weight": "5 lb"},
}
# endregion

# endregion

# region TRAITS

# region Sharp Claws Trait
sharpClawsTrait = {
    "id": "11ba8078-778b-4823-b194-56ab4eea7785",
    "type": "trait",
    "name": "Sharp Claws",
    "reference": "B42",
    "tags": ["Advantage", "Physical"],
    "base_points": 5,
    "weapons": [
        {
            "id": "6947bdb1-dbf7-4467-818a-7a97925995c1",
            "type": "melee_weapon",
            "damage": {"type": "cut", "st": "thr", "base": "-1"},
            "usage": "Slash",
            "reach": "C",
            "parry": "0",
            "block": "No",
            "defaults": [
                {"type": "dx"},
                {"type": "skill", "name": "Brawling"},
                {"type": "skill", "name": "Boxing"},
                {"type": "skill", "name": "Karate"},
            ],
            "calc": {"level": 11, "parry": "8", "block": "No", "damage": "1d-2 cut"},
        },
        {
            "id": "8067b74a-214b-41cf-93dd-6b11f5a31584",
            "type": "melee_weapon",
            "damage": {"type": "cut", "st": "thr"},
            "usage": "Kick",
            "reach": "C,1",
            "parry": "No",
            "block": "No",
            "defaults": [
                {"type": "dx", "modifier": -2},
                {"type": "skill", "name": "Karate", "modifier": -2},
                {"type": "skill", "name": "Brawling", "modifier": -2},
            ],
            "calc": {"level": 9, "parry": "No", "block": "No", "damage": "1d-1 cut"},
        },
    ],
    "calc": {"points": 5},
}
# endregion

# region Fangs Trait
fangsTrait = {
    "id": "95bb6a7b-e928-48c3-b583-5d37757f1a1a",
    "type": "trait",
    "name": "Fangs",
    "reference": "B91",
    "tags": ["Advantage", "Exotic", "Physical"],
    "base_points": 2,
    "weapons": [
        {
            "id": "5b7be883-a73f-415d-ba4a-38ca4f67f125",
            "type": "melee_weapon",
            "damage": {"type": "imp", "st": "thr", "base": "-1"},
            "usage": "Bite",
            "reach": "C",
            "parry": "No",
            "block": "No",
            "defaults": [{"type": "skill", "name": "Brawling"}, {"type": "dx"}],
            "calc": {"level": 11, "parry": "No", "block": "No", "damage": "1d-2 imp"},
        }
    ],
    "calc": {"points": 2},
}
# endregion

# region Sharp Teeth Trait
sharpTeethTrait = {
    "id": "c56a0be5-8487-4acc-bcaf-20cbab7c5320",
    "type": "trait",
    "name": "Sharp Teeth",
    "reference": "B91",
    "tags": ["Exotic", "Perk", "Physical"],
    "modifiers": [
        {
            "id": "c32922a5-c187-48a9-8109-61776dc618f1",
            "type": "modifier",
            "name": "Provided by Vampiric Bite",
            "reference": "B96",
            "cost": -1,
            "cost_type": "points",
            "disabled": True,
        }
    ],
    "base_points": 1,
    "weapons": [
        {
            "id": "dbf194fc-0933-473c-8708-1704bb1dbb50",
            "type": "melee_weapon",
            "damage": {"type": "cut", "st": "thr", "base": "-1"},
            "usage": "Bite",
            "reach": "C",
            "parry": "No",
            "block": "No",
            "defaults": [{"type": "skill", "name": "Brawling"}, {"type": "dx"}],
            "calc": {"level": 11, "parry": "No", "block": "No", "damage": "1d-2 cut"},
        }
    ],
    "calc": {"points": 1},
}
# endregion

# endregion

# region Skills
# endregion
