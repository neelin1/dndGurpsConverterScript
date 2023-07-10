# dndGURPsConverter

This converter automatically converts json files from 5e.tools (Dungeons and Dragons 5e statblocks) to .gcs files for GURPs Character Sheet. 

This is a rough conversion, it probably won't be exactly right and should be edited. In particular, health calculations are off.

# Instructions
1. Clone github repo
2. Go to 5e.tools. Find the monster you want to clone. Click Open Pop-Up in the top right corner of the statblock. Click the *{}* button and click copy code.
3. Paste code into *input.json*
4. Run *converter.py*
5. Types yes or no if you want the character to have combat reflexes or not
6. Copy *output.gcs* to wherever you store you gcs files and rename it to the correct monsters (*demogorgon.gcs* for example)

# Conversion Method

## Name
Name is transferred over

## Primary Attributes
Each attribute modifier is added to 10, to find the relevant stat
- STR -> ST
- DEX -> DX
- CON -> HT. If CON is 14 or higher, High-Pain Tolerance is added
- The higher of INT or WIS -> IQ
- The CHA modifier (if greater than 0) is taken as the number of levels in Diplomacy, if Pesuasion is not in the stat-block, and the number of levels in Fast-Talk if Deception is not in the statblock.

# Size
- Tiny: -4
- Small: -1
- Medium: +0
- Large: +2
    - +1 additional strength
    - +10 additional HP
- Huge: +3
    - +2 additional strength
    - +20 additional HP
- Gargantuan: +4
    - +3 additional strength
    - +30 additional HP

## Skills

The proficiency bonus of a skill is taken as the number of levels in the relevent skills. Note that non-int/wisdom skills are calculated by subtracting from the modifier. Otherwise, the level is just the proficiency bonus. 
- Acrobatics -> Climbing, Acrobatics
- Animal Handling -> Riding, Animal Handling (general), Veterinary (if high enough modifier)
- Arcana -> Occultism, Thaumatology
- Athletics -> Climbing, Hiking, Throwing, Wrestling, Running
- Deception -> Fast-Talk
- History -> History (General)
- Insight -> Detect Lie
- Intimidation -> Intimidation
- Investigation -> Scrounging, Search
- Medicine -> First-Aid, Diagnosis, Physician (if medium), Pharmacy (if medium) Surgery (if high)
- Nature -> Gardening and Biology (Botany)
- Perception -> Observation, Acute Vision (level based on modifier)
- Performance -> Acting, Dancing, Musical Instrument (any), and Singing
- Persuasion -> Diplomacy
- Religion -> Theology (General)
- Sleight of Hand -> Sleight of Hand
- Stealth -> Stealth
- Survival (any) -> Survival(General), Herb Lore (if character doesn't have nature)

# Abilities
- User can select if the creature is a hardened fighter. If so, Combat Reflexes are added. 

## Armor
- Natural Armor adds Damage Resistance (level based on AC-11 if AC is at least 12)
- Unarmored Defense adds Enhanced Dodge (level based on AC - 11)
- Leather / Leather Armor -> Leather Armor, Leather Pants, Heavy Leather Sleeves, Leather Helm, Boots
- Studded Leather / Studded Leather Armor -> Leather Armor, Heavy Leather Leggings, Heavy Leather Sleeves, Leather Helm, Studded Leather Skirts, Reinforced Boots, Leather Gloves
- Hide Armor / Hide -> Fur Tunic, Fur Loincloth, Leather Armor, Leather Pants, Leather Helm, Reinforced Boots, Leather Gloves, Heavy Leather Sleeves, Heavy Leather Leggings
- Padded -> Buff Coat, Leather Pants, Heavy Leather Sleeves, Leather Helm, Reinforced Boots, Leather Gloves
- Shield -> Medium Shield
- Scale Mail / Scale Mail Armor -> Scale Armor, Scale Leggings, Scale Sleeves, Pot Helm, Buff Coat, Leather Gloves, Reinforced Boots
- Chain Shirt / Chain Mail -> Mail Coif, Mail Shirt, Mail Leggings, Mail Sleeves, Pot Helm, Buff Coat, Leather Gloves, Reinforced Boots
- Breastplate / Breastplate Armor -> Breastplate, Mail Leggings, Mail Sleeves, Pot Helm, Buff Coat, Leather Gloves, Reinforced Boots
- Half Plate Armor / Half Plate -> Steel Corselet, Mail Sleeves, Pot Helm, Mail Coif, Buff Coat, Gauntlets, Mail Leggings, Sollerets
- Splint Armor / Splint Mail / SplintMail -> Steel Corselet, Plate Arms, Plate Legs, Sollerets, Gauntlets, Mail Hauberk, Buff Coat, Barrel Helm
- Plate Mail / Plate Mail Armor / Plate / Plate Armor -> Heavy Steel Corselet, Heavy Plate Arms, Heavy Plate Legs, Sollerets, Heavy Gauntlets, Mail Hauberk, Buff Coat, Mail Leggings, Mail Sleeves, Great Helm

## Resistances & Immunities
- Resistance adds Limited Damage Resistance 4 to that type of damage
- Immunity adds Immunity to that type of damage
    Currently bugging (run Iron golem)

## Traits
Add each ability as Custom Trait with the same Name and Description as the Ability. 
Automatically change:
- advantage to +3
- disadvantage to -3
- Constitution Saving Throws -> HT Check
- Wisdom Saving Throw -> Will Check
- Intelligence Saving Throw -> IQ Check
- Charisma Saving Throw -> Will Check
- Strength Saving Throw -> ST Check
- Dexterity Saving Throw -> DX Check 
- Damage -> comparable GURPs damage
- saving throw DC -> comparable GURPS DC


The following abilities have more specific abilities
- Nimble Escape ->  The [name] does not have a limit on the number of times it can use the Retreat active defense and can take 2 steps during a Retreat. The creatures step action size also becomes a minimum of 2 yards."
- Dive Attack -> If the [name] is flying and dives its full move on a Move and Attack maneuver and hits the target with a melee weapon attack, the attack deals an extra 1d damage to the target.      
- Keen Vision -> gain Acute Vision 3 trait (or increment it by 3 if it already has it)
- Keen Hearing -> gain Acute Hearing 3 trait
- Keen Smell -> gain Acute Taste & Smell 3 trait
- Keen Senses -> gain Acute Vision 3, Acute Hearing 3, Acute Taste & Smell 3
- Legendary Resistance -> Lucky (# of times)
- Undead Fortitude -> Undead Fortitude and Injury Tolerance

### Spells

### Legendary Actions
- Added as a custom trait reaction

## Actions
Unless specified below, actions are added as a Custom Trait and Attack with level as prof bonus.

- Dagger -> Knife Skill, Knife Equipment
- Light Crossbow -> Crossbow Skill, Crossbow (str 11) equipment
- Club -> Broadsword Skill, light club Equipment
- Scimitar -> Shortsword Skill, Shortsword Equipment
- Shortsword -> Shortsword Skill, Shortsword Equipment
- Greataxe -> Two-handed Axe/Mace Skill, Greataxe Equipment
- Hand Crossbow
- Heavy Crossbow
- Spear -> Spear Skill, Spear Equipment
- Javelin
- Longsword / Long Sword
- Longbow
- Shortbow
- Rapier
- Greatclub
- Sling
- Quarterstaff / Staff
- Maul
- Pike
- Hand Axe
- Trident
- Claws / Claw
- Fangs / Bite

## Reactions
Unless specified below, reactions are added as a Custom Trait that costs 1 fp.

# Bonus Action
Bonus actions are added as a special trait

## Languages
Adds each languge as a language trait

## Senses

## Size Modifier

## Extra Health

## Info

## Image