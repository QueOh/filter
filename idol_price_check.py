#!/usr/bin/env python3
"""
Price-check Magic Idols for Path of Exile using the official trade API.

Requirements covered:
- Fetch stat IDs from /api/trade/data/stats
- Search Magic Idols in a league with online status
- Fetch first 5 listings and report the minimum chaos price per affix
- Include User-Agent header, POESESSID cookie, and 1s delay between requests
"""

from __future__ import annotations

import argparse
import time
from typing import Dict, List, Tuple, Optional
from urllib.parse import quote

import requests

# ==========================
# Configuration
# ==========================
LEAGUE_NAME = "Phrecia 2.0"
USER_AGENT = "MyIdolScanner/1.0"
POESESSID = "YOUR_POESESSID_HERE"  # <-- insert your session id

# Affixes grouped by idol base type (exact text as shown in the trade UI)
AFFIX_NAMES = {
    "Minor Idol": [
        "#% chance for Scouting Reports to drop as Blighted Scouting Reports instead in your Maps",
        "#% chance for Scouting Reports to drop as Comprehensive Scouting Reports instead in your Maps",
        "#% chance for Scouting Reports to drop as Delirious Scouting Reports instead in your Maps",
        "#% chance for Scouting Reports to drop as Operative's Scouting Reports instead in your Maps",
        "#% chance for Scouting Reports to drop as Singular Scouting Reports instead in your Maps",
        "#% chance for Scouting Reports to drop as Vaal Scouting Reports instead in your Maps",
        "#% chance for your Maps to attract Beyond Demons",
        "#% chance to create a copy of Beasts Captured in your Maps",
        "#% increased Atlas Scouting Reports found in your Maps",
        "#% increased Cost of Building and Upgrading Towers",
        "#% increased Explosive Radius in your Maps",
        "#% increased Heist Contracts found in your Maps",
        "#% increased Maps found in Area",
        "#% increased Quantity of Expedition Logbooks dropped by Runic Monsters in your Maps",
        "#% increased Rarity of Items Dropped by Abyssal Troves and Stygian Spires in your Maps",
        "#% increased Scarabs found in your Maps",
        "#% increased chance for Ore Deposits found in your Maps to be Bismuth",
        "#% increased chance for Ore Deposits found in your Maps to be Crimson Iron",
        "#% increased chance for Ore Deposits found in your Maps to be Orichalcum",
        "#% increased chance for Ore Deposits found in your Maps to be Petrified Amber",
        "#% increased chance for Ore Deposits found in your Maps to be Verisium",
        "#% increased duration of Shrine Buffs on players granted by Shrines in your Maps",
        "Abyssal Troves and Stygian Spires in your Maps have #% chance to drop a Rare Item with an Abyssal Socket",
        "Abyssal Troves and Stygian Spires in your Maps have #% increased chance to contain or drop an Abyss Jewel",
        "Beyond Demons in your Maps have #% increased chance to be followers of Beidat",
        "Beyond Demons in your Maps have #% increased chance to be followers of Ghorr",
        "Beyond Demons in your Maps have #% increased chance to be followers of K'tash",
        "Blight Chests in your Maps have #% more chance to contain Blighted Maps",
        "Delirious Monsters Killed in your Maps provide #% increased Reward Progress",
        "Delirium Bosses in your Maps drop #% increased Simulacrum Splinters",
        "Delirium Encounters in your Maps are #% more likely to spawn Unique Bosses",
        "Delirium Encounters in your Maps have #% chance to generate an additional Reward type",
        "Delirium Monsters in your Maps have #% increased Pack Size",
        "Eldritch Ichor found in your Maps influenced by The Eater of Worlds have #% chance to be Duplicated",
        "Favours Deferred at Ritual Altars in your Maps reappear #% sooner",
        "Harbingers in your Maps have #% increased Cooldown Recovery Rate",
        "Harvest Crops in your Maps have #% increased chance to grow Blue Plants",
        "Harvest Crops in your Maps have #% increased chance to grow Purple Plants",
        "Harvest Crops in your Maps have #% increased chance to grow Yellow Plants",
        "Harvest Monsters in your Maps grant #% increased Experience",
        "Heist Contracts found in your Maps are #% more likely to require Agility, Deception or Engineering",
        "Heist Contracts found in your Maps are #% more likely to require Demolition, Counter-Thaumaturgy or Trap Disarmament",
        "Heist Contracts found in your Maps are #% more likely to require Lockpicking, Brute Force or Perception",
        "Immortal Syndicate Members Executed in your Maps have #% chance to gain an additional Rank",
        "Immortal Syndicate Members in your Maps are #% more likely to be accompanied by their Leader",
        "Imprisoned Monsters in your Maps have #% chance to drop an additional Rare Item with an Essence Modifier",
        "Imprisoned Monsters in your Maps have #% chance to have an additional Essence",
        "Incursions in your Maps have #% increased Pack Size",
        "Items dropped by Rare Monsters have #% chance to be Corrupted",
        "Items found in your Corrupted Maps have #% chance to be Corrupted",
        "Legion Chests released from Stasis in your Maps release other Monsters and Chests with #% increased Range",
        "Legion Encounters in your Maps are #% more likely to include a General",
        "Legion Sergeants in your Maps have #% additional chance to have Rewards",
        "Map Bosses have #% chance to be accompanied by two Rogue Exile Bodyguards",
        "Map Bosses have #% chance to be accompanied by two Rogue Exiles",
        "Map Bosses have #% increased chance to drop a Conqueror Map",
        "Monster Packs Influenced by The Searing Exarch in your Maps have #% increased Pack Size",
        "Ore Deposits in your Maps contain #% increased Ore",
        "Red Beasts in your Maps have #% increased chance to be from The Caverns",
        "Red Beasts in your Maps have #% increased chance to be from The Deep",
        "Red Beasts in your Maps have #% increased chance to be from The Sands",
        "Red Beasts in your Maps have #% increased chance to be from The Wilds",
        "Rerolling Favours at Ritual Altars in your Maps costs #% increased Tribute",
        "Smuggler's Caches in your Maps have #% increased chance to drop Blueprints",
        "Strongboxes in your Maps have #% increased chance to be a Cartographer's Strongbox",
        "Strongboxes in your Maps have #% increased chance to be a Diviner's Strongbox",
        "Strongboxes in your Maps have #% increased chance to be a Gemcutter's Strongbox",
        "Strongboxes in your Maps have #% increased chance to be an Arcanist's Strongbox",
        "Sulphite Veins and Chests in your Maps have #% chance to also contain an equal amount of Azurite",
        "Tier 1-15 Maps found have #% chance to become 1 tier higher",
        "Tormented Spirits in your Maps have #% increased Duration",
        "Ultimatum Encounters in your Maps have #% increased chance for\nthe final Round to include a Boss",
        "Ultimatum Encounters in your Maps have #% increased chance to\nonly require you to Survive",
        "Ultimatum Encounters in your Maps have #% increased chance to\nrequire you to Stand in the Stone Circles",
        "Ultimatum Encounters in your Maps have #% increased chance to\nrequire you to defeat waves of Enemies",
        "Ultimatum Encounters in your Maps have #% increased chance to\nrequire you to protect the Altar",
        "Ultimatum Rewards in your Maps have #% increased chance to be Currency Items",
        "Ultimatum Rewards in your Maps have #% increased chance to be Divination Cards",
        "Ultimatum Rewards in your Maps have #% increased chance to be Gems",
        "Ultimatum Rewards in your Maps have #% increased chance to be Jewellery",
        "Ultimatum Rewards in your Maps have #% increased chance to be Unique Items",
        "Unique Monsters in your Maps have #% increased chance to drop Scarabs",
        "Unique Monsters slain at Ritual Altars in your Maps grant #% less Tribute",
        "Vaal Side Areas in your Maps have #% chance to be an Alluring Vaal Side Area",
        "Your Maps contain #% more Monster Packs consisting of difficult and rewarding Monsters",
        "Your Maps have #% chance to award double progress towards encountering The Eater of Worlds",
        "Your Maps have #% chance to contain an additional Imprisoned Monster",
        "Your Maps have #% increased chance to contain Alva",
        "Your Maps have #% increased chance to contain Einhar",
        "Your Maps have #% increased chance to contain Jun",
        "Your Maps have #% increased chance to contain Niko",
        "Your Maps have #% increased chance to contain Ritual Altars",
        "Your Maps have #% increased chance to contain The Sacred Grove",
        "Your Maps have #% increased chance to contain a Blight Encounter",
        "Your Maps have #% increased chance to contain a Legion Encounter",
        "Your Maps have #% increased chance to contain a Mirror of Delirium",
        "Your Maps have #% increased chance to contain a Smuggler's Cache",
        "Your Maps have #% increased chance to contain an Abyss",
        "Your Maps have #% increased chance to contain an Expedition Encounter",
        "Your Maps have #% increased chance to contain an Ultimatum Encounter",
        "Your Maps have +#% chance to be haunted by a Tormented Spirit",
        "Your Maps have +#% chance to contain Alva",
        "Your Maps have +#% chance to contain Einhar",
        "Your Maps have +#% chance to contain Jun",
        "Your Maps have +#% chance to contain Niko",
        "Your Maps have +#% chance to contain Ore Deposits",
        "Your Maps have +#% chance to contain Ritual Altars",
        "Your Maps have +#% chance to contain The Sacred Grove",
        "Your Maps have +#% chance to contain a Blight Encounter",
        "Your Maps have +#% chance to contain a Legion Encounter",
        "Your Maps have +#% chance to contain a Mirror of Delirium",
        "Your Maps have +#% chance to contain a Rogue Exile",
        "Your Maps have +#% chance to contain a Shrine",
        "Your Maps have +#% chance to contain a Smuggler's Cache",
        "Your Maps have +#% chance to contain a Strongbox",
        "Your Maps have +#% chance to contain an Abyss",
        "Your Maps have +#% chance to contain an Expedition Encounter",
        "Your Maps have +#% chance to contain an Imprisoned Monster",
        "Your Maps have +#% chance to contain an Ultimatum Encounter",
        "Your Maps have a #% chance to be haunted by an additional Tormented Spirit",
        "Your Maps have a #% chance to contain an additional Harbinger",
        "Your Maps have a #% chance to contain an additional Rogue Exile",
        "Your Maps have a #% chance to contain an additional Shrine",
        "Your Red Tier Maps grant # additional Voltaxic Sulphite on Completion",
        "Your White Tier Maps grant # additional Voltaxic Sulphite on Completion",
        "Your Yellow Tier Maps grant # additional Voltaxic Sulphite on Completion",
    ],
    "Kamasan Idol": [
        "#% chance for Blight Chests to contain an additional Reward",
        "#% chance for one Monster in each of your Maps to drop an additional connected Map",
        "#% chance for your Maps to attract Beyond Demons",
        "#% increased Blueprints found in your Maps",
        "#% increased Quantity of Items contained in Strongboxes in your Maps",
        "#% increased Quantity of Tainted Currency dropped by Beyond Demons in your Maps",
        "#% increased Quantity of Vendor Refresh Currencies dropped by Monsters in your Maps",
        "#% increased Rarity of Items Dropped by Legion Sergeants in your Maps",
        "#% increased Rarity of Items Dropped by Wild Rogue Exiles in your Maps",
        "#% increased Rarity of items from Defeated Syndicate Members in your Maps per Equipment Item they have",
        "#% increased chance for Memory Threads to lead towards the Incarnation of Dread",
        "#% increased chance for Memory Threads to lead towards the Incarnation of Fear",
        "#% increased chance for Memory Threads to lead towards the Incarnation of Neglect",
        "#% increased chance for your Maps to contain Memory Tears (Tier 16+)",
        "#% increased chance of Ritual Altars with Special Rewards",
        "#% increased effect of Shrine Buffs on players granted by Shrines in your Maps",
        "#% increased number of Explosives in your Maps",
        "#% increased quantity of Artifacts dropped by Monsters",
        "+#% chance for a Synthesis Map to drop from Final Map Boss in each Map (Tier 14+)",
        "Abyss Cracks in your Maps have #% chance to spawn 100% increased Monsters",
        "Abyss Cracks in your Maps have #% chance to spawn all Monsters as Magic for each prior Pit in that Abyss",
        "Abyss Monsters in your Maps grant #% increased Experience",
        "Abyss Pits in your Maps have #% chance to spawn 100% increased Monsters",
        "Abysses in your Maps spawn #% increased Monsters",
        "Beyond Portals in your Maps have #% increased Merging Radius",
        "Blight Bosses in your Maps have #% chance to add an additional Reward Chest to their Lane",
        "Blight Monsters in your Maps spawn #% faster",
        "Blighted Chests in your Maps have #% increased chance to contain an Oil",
        "Cluster Jewels from Delirium Rewards have a #% chance to be Rare and Corrupted",
        "Delirium Bosses in your Maps have #% increased chance to drop Unique Cluster Jewels",
        "Delirium Fog in your Maps dissipates #% faster",
        "Delirium Monsters in your Maps have #% increased chance to drop Cluster Jewels",
        "Einhar deals #% more Damage to Unique Monsters in your Maps",
        "Einhar has #% increased Cooldown Recovery Rate in your Maps",
        "Expedition Detonation Chains in your Maps travel #% slower",
        "Favours Rerolled at Ritual Altars in your Maps have #% chance to cost no Tribute",
        "Final Map Boss in each Map has +#% chance to drop a Shaper Guardian Map (Tier 14+)",
        "Final Map Boss in each Map has +#% chance to drop an Elder Guardian Map (Tier 14+)",
        "Harbingers in your Maps have #% chance to drop an additional Stack of Currency Shards",
        "Harvest Crops in your Maps have #% increased chance to contain Tier 3 Plants",
        "Harvest Crops in your Maps have #% increased chance to contain a Tier 4 Plant",
        "Heist Contracts found in your Maps are #% more likely to require level 3 Jobs",
        "Heist Contracts found in your Maps are #% more likely to require level 4 Jobs",
        "Heist Contracts found in your Maps are #% more likely to require level 5 Jobs",
        "Immortal Syndicate Members in your Maps are #% more\nlikely to offer to Bargain for Items",
        "Incursions in your Maps have #% chance for all Monsters to be at least Magic",
        "Lanes of Blight Encounters in your Maps have #% chance for an additional Reward Chest",
        "Legion Encounters in your Maps have #% increased Duration",
        "Legion Monsters in your Maps have #% increased Pack Size",
        "Legion Monsters in your Maps take #% increased Damage while in Stasis",
        "Map Bosses have #% chance to be surrounded by Tormented Spirits",
        "Monster Packs Influenced by Conquerors in your Maps have #% increased Pack Size",
        "Monsters Imprisoned by Essences have a #% chance to contain a Remnant of Corruption",
        "Monsters Influenced by The Searing Exarch in your Maps have #% chance to drop an Item with a Searing Exarch Implicit Modifier",
        "Ritual Altars in your Maps can have #% increased number of Spawned Monsters at once",
        "Ritual Splinters offered at Ritual Altars in your Maps have #% increased Stack Size",
        "Rogue Exiles in your Maps have #% chance to drop an additional Currency Item",
        "Scarabs dropped in your Maps have #% increased chance to be Abyss Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Anarchy Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Bestiary Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Betrayal Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Beyond Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Blight Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Cartography Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Delirium Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Divination Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Domination Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Essence Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Expedition Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Harbinger Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Harvest Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Incursion Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Kalguuran Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Legion Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Ritual Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Sulphite Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Titanic Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Torment Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Ultimatum Scarabs",
        "Scarabs found in your Maps have #% increased chance to be Ambush Scarabs",
        "Strongboxes in your Maps have #% chance to be guarded by an additional Pack of Monsters",
        "Tormented Spirits have a #% chance to be set free when Possessed Monsters are slain",
        "Ultimatum Altars in your Maps have #% increased Life",
        "Ultimatum Encounters in your Maps only requiring you to Survive\nhave #% increased duration",
        "Ultimatum Encounters in your Maps requiring you to Defeat waves of Enemies\nrequire killing #% increased number of Enemies",
        "Ultimatum Rewards in your Maps have #% increased chance to be Inscribed Ultimatums",
        "Ultimatum Stone Circles in your Maps have #% increased radius",
        "Voltaxic Sulphite Veins and Chests in your Maps contain #% increased Sulphite",
        "You gain #% increased Movement Speed per stack of Sulphite Intoxication",
        "Your Maps have #% chance to contain an additional Imprisoned Monster",
        "Your Maps have #% increased chance to contain Alva",
        "Your Maps have #% increased chance to contain Einhar",
        "Your Maps have #% increased chance to contain Jun",
        "Your Maps have #% increased chance to contain Niko",
        "Your Maps have #% increased chance to contain Ritual Altars",
        "Your Maps have #% increased chance to contain The Sacred Grove",
        "Your Maps have #% increased chance to contain a Blight Encounter",
        "Your Maps have #% increased chance to contain a Legion Encounter",
        "Your Maps have #% increased chance to contain a Mirror of Delirium",
        "Your Maps have #% increased chance to contain a Smuggler's Cache",
        "Your Maps have #% increased chance to contain an Abyss",
        "Your Maps have #% increased chance to contain an Expedition Encounter",
        "Your Maps have #% increased chance to contain an Ultimatum Encounter",
        "Your Maps have +#% chance to be haunted by a Tormented Spirit",
        "Your Maps have +#% chance to contain Alva",
        "Your Maps have +#% chance to contain Einhar",
        "Your Maps have +#% chance to contain Jun",
        "Your Maps have +#% chance to contain Niko",
        "Your Maps have +#% chance to contain Ore Deposits",
        "Your Maps have +#% chance to contain Ritual Altars",
        "Your Maps have +#% chance to contain The Sacred Grove",
        "Your Maps have +#% chance to contain a Blight Encounter",
        "Your Maps have +#% chance to contain a Legion Encounter",
        "Your Maps have +#% chance to contain a Mirror of Delirium",
        "Your Maps have +#% chance to contain a Rogue Exile",
        "Your Maps have +#% chance to contain a Shrine",
        "Your Maps have +#% chance to contain a Smuggler's Cache",
        "Your Maps have +#% chance to contain a Strongbox",
        "Your Maps have +#% chance to contain a Vaal Side Area",
        "Your Maps have +#% chance to contain an Abyss",
        "Your Maps have +#% chance to contain an Expedition Encounter",
        "Your Maps have +#% chance to contain an Imprisoned Monster",
        "Your Maps have +#% chance to contain an Ultimatum Encounter",
        "Your Maps have a #% chance to be haunted by an additional Tormented Spirit",
        "Your Maps have a #% chance to contain an additional Harbinger",
        "Your Maps have a #% chance to contain an additional Rogue Exile",
        "Your Maps have a #% chance to contain an additional Shrine",
        "Your Maps that contain Smuggler's Caches have a #% chance to contain an additional Smuggler's Cache",
        "Your Maps that contain capturable Beasts have #% chance to contain an additional Red Beast",
    ],
    "Totemic Idol": [
        "#% chance for your Maps to attract Beyond Demons",
        "#% chance to spawn a Searing Exarch Altar when the Influence of The Searing Exarch first appears in your Maps",
        "#% increased Pack Size of your Maps affected by Fortune Favours the Brave",
        "#% increased Quantity of Items found in your Maps affected by Fortune Favours the Brave",
        "#% increased Rarity of Items Dropped by Immortal Syndicate Members in your Maps",
        "#% increased Rarity of Items found in your Maps",
        "#% increased Rarity of Items found in your Maps affected by Fortune Favours the Brave",
        "#% increased Rarity of Maps found in your Maps",
        "#% increased chance for Equipment Items dropped in your Maps to have Memory Strands",
        "#% increased chance for Maps found in your Maps to have Memory Influence",
        "#% increased chance to find Eater of Worlds Altars in your Maps",
        "#% increased effect of Explicit Modifiers on your Maps",
        "#% more Basic Currency Items found from Beyond Demons in your Maps\nthat are followers of Beidat",
        "#% more Divination Cards found from Beyond Demons in your Maps\nthat are followers of K'Tash",
        "#% more Unique Items found from Beyond Demons in your Maps\nthat are followers of Ghorr",
        "Abyss Cracks in your Maps have #% chance to spawn all Monsters as at least Magic",
        "Abyss Pits in your Maps have #% chance to spawn all Monsters as at least Magic",
        "Abysses in your Maps have #% increased chance to lead to an Abyssal Depths",
        "Abysses in your Maps that do not lead to an Abyssal Depths have #% increased chance to lead to a Stygian Spire",
        "Beyond Demons in your Maps grant #% increased Experience",
        "Beyond Portals in your Maps have #% increased chance to spawn a Unique Boss",
        "Bismuth Ore Deposits in your Maps have #% chance to\nadd an additional Modifier to Monsters they affect",
        "Blight Encounters in your Maps spawn #% more Non-Unique Monsters",
        "Blight Monsters in your Maps take #% increased Damage",
        "Buffs granted by Orichalcum Ore Deposits in your Maps have #% increased Duration",
        "Completing the final Ritual Altar in your Maps has #% chance to drop a Blood-filled Vessel",
        "Crimson Iron Ore Deposits in your Maps are guarded by an additional Corrupted Growth",
        "Currency Items from Strongboxes in your Maps are Duplicated",
        "Delirium Fog in your Maps lasts # additional seconds before dissipating",
        "Delirium Rewards in your Maps have #% increased chance to give Delirium Orbs",
        "Delirium in your Maps increases #% faster with distance from the mirror",
        "Divination Cards from Strongboxes in your Maps are Duplicated",
        "Expedition Monsters in your Maps spawn with an additional #% of Life missing",
        "Expeditions in your Maps have #% increased chance to be led by Dannig",
        "Expeditions in your Maps have #% increased chance to be led by Gwennen",
        "Expeditions in your Maps have #% increased chance to be led by Rog",
        "Expeditions in your Maps have #% increased chance to be led by Tujen",
        "Final Map Boss in each Map has #% chance to drop an additional Scarab",
        "Final Map Boss in each Map has #% chance to drop an additional connected Map",
        "Gems contained in Strongboxes in your Maps are Duplicated",
        "Harbingers in your Maps have #% chance to be replaced by a powerful Harbinger boss",
        "Harvest Monsters in your Maps drop #% increased Quantity of Lifeforce",
        "Harvests in your Maps have #% chance for the unchosen Crop to not wilt",
        "Heist Contracts found in your Maps are #% more likely to target High Value Targets",
        "Heist Contracts found in your Maps are #% more likely to target Precious Targets",
        "Immortal Syndicate Members in your Maps have #% chance to drop an additional Veiled Item",
        "Immortal Syndicate Members in your Maps have #% increased chance to be accompanied by reinforcements",
        "Imprisoned Monsters in your Maps have #% chance to have 3 additional Essences",
        "Inscribed Ultimatums found in your Maps have #% increased chance to reward Currency Items",
        "Inscribed Ultimatums found in your Maps have #% increased chance to reward Divination Cards",
        "Inscribed Ultimatums found in your Maps have #% increased chance to reward Unique Items",
        "Items dropped by Unique Monsters have #% chance to be Corrupted",
        "Killing non-resident Architects in your Maps has #% chance to add\nan additional Upgrade Tier to the surviving Architect's Room",
        "Legion Encounters in your Maps have #% increased chance to include a Karui army",
        "Legion Encounters in your Maps have #% increased chance to include a Maraketh army",
        "Legion Encounters in your Maps have #% increased chance to include a Templar army",
        "Legion Encounters in your Maps have #% increased chance to include a Vaal army",
        "Legion Encounters in your Maps have #% increased chance to include an Eternal Empire army",
        "Legion Monsters in your Maps which have Rewards have #% chance to gain two additional Rewards, and if not have #% chance to gain one additional Reward",
        "Maps from Strongboxes in your Maps are Duplicated",
        "Monster Packs Influenced by The Elder in your Maps have #% increased Pack Size",
        "Monster Packs Influenced by The Shaper in your Maps have #% increased Pack Size",
        "Monsters Influenced by The Eater of Worlds in your Maps have #% chance to drop an item with an Eater of Worlds Implicit Modifier",
        "Monsters Sacrificed at Ritual Altars in your Maps grant #% increased Tribute",
        "Oils found in your Maps have #% chance to be 1 tier higher",
        "Petrified Amber Ore Deposits in your Maps take #% increased Damage",
        "Rare Monsters in your Maps have #% increased chance to drop Scarabs per Monster Modifier affecting them",
        "Red Beasts captured in your Maps have a #% chance to gain a Modifier that provides a chance to not to be consumed when sacrificed at the Blood Altar",
        "Red Beasts in your Maps have #% chance to appear in Pairs",
        "Remnants in your Maps have #% chance to have an additional Suffix Modifier",
        "Ritual Altars in your Maps spawn Monsters #% faster",
        "Shrines in your Maps have #% chance to be guarded by an additional Pack of Monsters",
        "Smuggler's Caches drop #% more Rogue Markers for each Smuggler's Cache opened in the Area",
        "Smuggler's Caches in your Maps have #% increased chance to drop Contracts",
        "Splinters contained in Legion Chests in your Maps have #% chance to be Duplicated",
        "Splinters dropped by Legion Monsters in your Maps have #% chance to be Duplicated",
        "Splinters dropped by Legion Monsters or contained in Legion Chests in your Maps have #% chance to be Duplicated",
        "The Sacred Grove in your Maps has #% chance to contain an additional Harvest",
        "Ultimatum Encounters in your Maps spawn #% increased number of Monsters",
        "Ultimatum Monsters in your Maps grant #% increased Experience",
        "Up to # Rare Monsters in each of your Maps are Possessed and their Minions are Touched",
        "Vaal Side Areas in your Maps have #% chance for Rewards from Vaal Vessels to be Duplicated",
        "Verisium Ore Deposits in your Maps can be channelled on for #% longer",
        "Voltaxic Sulphite Veins and Chests in your Maps have #% chance to contain double Sulphite",
        "Wild Rogue Exiles in your Maps have #% chance to be Possessed by a Tormented Spirit",
        "You gain #% increased Damage per stack of Sulphite Intoxication",
        "Your Maps are haunted by an additional Tormented Spirit",
        "Your Maps contain # additional Strongboxes",
        "Your Maps contain an additional Harbinger",
        "Your Maps contain an additional Imprisoned Monster",
        "Your Maps contain an additional Shrine",
        "Your Maps have #% chance to grant an additional Kirac Mission on Completion",
        "Your Maps have #% increased chance to contain Alva",
        "Your Maps have #% increased chance to contain Einhar",
        "Your Maps have #% increased chance to contain Jun",
        "Your Maps have #% increased chance to contain Niko",
        "Your Maps have #% increased chance to contain Ritual Altars",
        "Your Maps have #% increased chance to contain The Sacred Grove",
        "Your Maps have #% increased chance to contain a Blight Encounter",
        "Your Maps have #% increased chance to contain a Legion Encounter",
        "Your Maps have #% increased chance to contain a Mirror of Delirium",
        "Your Maps have #% increased chance to contain a Smuggler's Cache",
        "Your Maps have #% increased chance to contain an Abyss",
        "Your Maps have #% increased chance to contain an Expedition Encounter",
        "Your Maps have #% increased chance to contain an Ultimatum Encounter",
        "Your Maps have +#% chance to be haunted by a Tormented Spirit",
        "Your Maps have +#% chance to contain Alva",
        "Your Maps have +#% chance to contain Einhar",
        "Your Maps have +#% chance to contain Jun",
        "Your Maps have +#% chance to contain Niko",
        "Your Maps have +#% chance to contain Ore Deposits",
        "Your Maps have +#% chance to contain Ritual Altars",
        "Your Maps have +#% chance to contain The Sacred Grove",
        "Your Maps have +#% chance to contain a Blight Encounter",
        "Your Maps have +#% chance to contain a Legion Encounter",
        "Your Maps have +#% chance to contain a Mirror of Delirium",
        "Your Maps have +#% chance to contain a Rogue Exile",
        "Your Maps have +#% chance to contain a Shrine",
        "Your Maps have +#% chance to contain a Smuggler's Cache",
        "Your Maps have +#% chance to contain a Strongbox",
        "Your Maps have +#% chance to contain a Trial of Ascendancy",
        "Your Maps have +#% chance to contain an Abyss",
        "Your Maps have +#% chance to contain an Expedition Encounter",
        "Your Maps have +#% chance to contain an Imprisoned Monster",
        "Your Maps have +#% chance to contain an Ultimatum Encounter",
        "Your Maps have a #% chance to contain an additional Harbinger",
        "Your Maps have a #% chance to contain an additional Rogue Exile",
        "Your Maps that contain capturable Beasts contain # additional Yellow Beast",
        "Your Maps with Ore Deposits have #% increased chance\nto contain at least two Ore Deposits",
    ],
    "Noble Idol": [
        "#% chance for Blight Chests to contain an additional Reward",
        "#% chance for one Monster in each of your Maps to drop an additional connected Map",
        "#% chance for your Maps to attract Beyond Demons",
        "#% increased Blueprints found in your Maps",
        "#% increased Quantity of Items contained in Strongboxes in your Maps",
        "#% increased Quantity of Tainted Currency dropped by Beyond Demons in your Maps",
        "#% increased Quantity of Vendor Refresh Currencies dropped by Monsters in your Maps",
        "#% increased Rarity of Items Dropped by Legion Sergeants in your Maps",
        "#% increased Rarity of Items Dropped by Wild Rogue Exiles in your Maps",
        "#% increased Rarity of items from Defeated Syndicate Members in your Maps per Equipment Item they have",
        "#% increased chance for Memory Threads to lead towards the Incarnation of Dread",
        "#% increased chance for Memory Threads to lead towards the Incarnation of Fear",
        "#% increased chance for Memory Threads to lead towards the Incarnation of Neglect",
        "#% increased chance for your Maps to contain Memory Tears (Tier 16+)",
        "#% increased chance of Ritual Altars with Special Rewards",
        "#% increased effect of Shrine Buffs on players granted by Shrines in your Maps",
        "#% increased number of Explosives in your Maps",
        "#% increased quantity of Artifacts dropped by Monsters",
        "+#% chance for a Synthesis Map to drop from Final Map Boss in each Map (Tier 14+)",
        "Abyss Cracks in your Maps have #% chance to spawn 100% increased Monsters",
        "Abyss Cracks in your Maps have #% chance to spawn all Monsters as Magic for each prior Pit in that Abyss",
        "Abyss Monsters in your Maps grant #% increased Experience",
        "Abyss Pits in your Maps have #% chance to spawn 100% increased Monsters",
        "Abysses in your Maps spawn #% increased Monsters",
        "Beyond Portals in your Maps have #% increased Merging Radius",
        "Blight Bosses in your Maps have #% chance to add an additional Reward Chest to their Lane",
        "Blight Monsters in your Maps spawn #% faster",
        "Blighted Chests in your Maps have #% increased chance to contain an Oil",
        "Cluster Jewels from Delirium Rewards have a #% chance to be Rare and Corrupted",
        "Delirium Bosses in your Maps have #% increased chance to drop Unique Cluster Jewels",
        "Delirium Fog in your Maps dissipates #% faster",
        "Delirium Monsters in your Maps have #% increased chance to drop Cluster Jewels",
        "Einhar deals #% more Damage to Unique Monsters in your Maps",
        "Einhar has #% increased Cooldown Recovery Rate in your Maps",
        "Expedition Detonation Chains in your Maps travel #% slower",
        "Favours Rerolled at Ritual Altars in your Maps have #% chance to cost no Tribute",
        "Final Map Boss in each Map has +#% chance to drop a Shaper Guardian Map (Tier 14+)",
        "Final Map Boss in each Map has +#% chance to drop an Elder Guardian Map (Tier 14+)",
        "Harbingers in your Maps have #% chance to drop an additional Stack of Currency Shards",
        "Harvest Crops in your Maps have #% increased chance to contain Tier 3 Plants",
        "Harvest Crops in your Maps have #% increased chance to contain a Tier 4 Plant",
        "Heist Contracts found in your Maps are #% more likely to require level 3 Jobs",
        "Heist Contracts found in your Maps are #% more likely to require level 4 Jobs",
        "Heist Contracts found in your Maps are #% more likely to require level 5 Jobs",
        "Immortal Syndicate Members in your Maps are #% more\nlikely to offer to Bargain for Items",
        "Incursions in your Maps have #% chance for all Monsters to be at least Magic",
        "Lanes of Blight Encounters in your Maps have #% chance for an additional Reward Chest",
        "Legion Encounters in your Maps have #% increased Duration",
        "Legion Monsters in your Maps have #% increased Pack Size",
        "Legion Monsters in your Maps take #% increased Damage while in Stasis",
        "Map Bosses have #% chance to be surrounded by Tormented Spirits",
        "Monster Packs Influenced by Conquerors in your Maps have #% increased Pack Size",
        "Monsters Imprisoned by Essences have a #% chance to contain a Remnant of Corruption",
        "Monsters Influenced by The Searing Exarch in your Maps have #% chance to drop an Item with a Searing Exarch Implicit Modifier",
        "Ritual Altars in your Maps can have #% increased number of Spawned Monsters at once",
        "Ritual Splinters offered at Ritual Altars in your Maps have #% increased Stack Size",
        "Rogue Exiles in your Maps have #% chance to drop an additional Currency Item",
        "Scarabs dropped in your Maps have #% increased chance to be Abyss Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Anarchy Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Bestiary Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Betrayal Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Beyond Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Blight Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Cartography Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Delirium Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Divination Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Domination Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Essence Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Expedition Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Harbinger Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Harvest Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Incursion Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Kalguuran Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Legion Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Ritual Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Sulphite Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Titanic Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Torment Scarabs",
        "Scarabs dropped in your Maps have #% increased chance to be Ultimatum Scarabs",
        "Scarabs found in your Maps have #% increased chance to be Ambush Scarabs",
        "Strongboxes in your Maps have #% chance to be guarded by an additional Pack of Monsters",
        "Tormented Spirits have a #% chance to be set free when Possessed Monsters are slain",
        "Ultimatum Altars in your Maps have #% increased Life",
        "Ultimatum Encounters in your Maps only requiring you to Survive\nhave #% increased duration",
        "Ultimatum Encounters in your Maps requiring you to Defeat waves of Enemies\nrequire killing #% increased number of Enemies",
        "Ultimatum Rewards in your Maps have #% increased chance to be Inscribed Ultimatums",
        "Ultimatum Stone Circles in your Maps have #% increased radius",
        "Voltaxic Sulphite Veins and Chests in your Maps contain #% increased Sulphite",
        "You gain #% increased Movement Speed per stack of Sulphite Intoxication",
        "Your Maps have #% chance to contain an additional Imprisoned Monster",
        "Your Maps have #% increased chance to contain Alva",
        "Your Maps have #% increased chance to contain Einhar",
        "Your Maps have #% increased chance to contain Jun",
        "Your Maps have #% increased chance to contain Niko",
        "Your Maps have #% increased chance to contain Ritual Altars",
        "Your Maps have #% increased chance to contain The Sacred Grove",
        "Your Maps have #% increased chance to contain a Blight Encounter",
        "Your Maps have #% increased chance to contain a Legion Encounter",
        "Your Maps have #% increased chance to contain a Mirror of Delirium",
        "Your Maps have #% increased chance to contain a Smuggler's Cache",
        "Your Maps have #% increased chance to contain an Abyss",
        "Your Maps have #% increased chance to contain an Expedition Encounter",
        "Your Maps have #% increased chance to contain an Ultimatum Encounter",
        "Your Maps have +#% chance to be haunted by a Tormented Spirit",
        "Your Maps have +#% chance to contain Alva",
        "Your Maps have +#% chance to contain Einhar",
        "Your Maps have +#% chance to contain Jun",
        "Your Maps have +#% chance to contain Niko",
        "Your Maps have +#% chance to contain Ore Deposits",
        "Your Maps have +#% chance to contain Ritual Altars",
        "Your Maps have +#% chance to contain The Sacred Grove",
        "Your Maps have +#% chance to contain a Blight Encounter",
        "Your Maps have +#% chance to contain a Legion Encounter",
        "Your Maps have +#% chance to contain a Mirror of Delirium",
        "Your Maps have +#% chance to contain a Rogue Exile",
        "Your Maps have +#% chance to contain a Shrine",
        "Your Maps have +#% chance to contain a Smuggler's Cache",
        "Your Maps have +#% chance to contain a Strongbox",
        "Your Maps have +#% chance to contain a Vaal Side Area",
        "Your Maps have +#% chance to contain an Abyss",
        "Your Maps have +#% chance to contain an Expedition Encounter",
        "Your Maps have +#% chance to contain an Imprisoned Monster",
        "Your Maps have +#% chance to contain an Ultimatum Encounter",
        "Your Maps have a #% chance to be haunted by an additional Tormented Spirit",
        "Your Maps have a #% chance to contain an additional Harbinger",
        "Your Maps have a #% chance to contain an additional Rogue Exile",
        "Your Maps have a #% chance to contain an additional Shrine",
        "Your Maps that contain Smuggler's Caches have a #% chance to contain an additional Smuggler's Cache",
        "Your Maps that contain capturable Beasts have #% chance to contain an additional Red Beast",
    ],
    "Burial Idol": [
        "#% chance for your Maps to attract Beyond Demons",
        "#% chance to spawn a Searing Exarch Altar when the Influence of The Searing Exarch first appears in your Maps",
        "#% increased Pack Size of your Maps affected by Fortune Favours the Brave",
        "#% increased Quantity of Items found in your Maps affected by Fortune Favours the Brave",
        "#% increased Rarity of Items Dropped by Immortal Syndicate Members in your Maps",
        "#% increased Rarity of Items found in your Maps",
        "#% increased Rarity of Items found in your Maps affected by Fortune Favours the Brave",
        "#% increased Rarity of Maps found in your Maps",
        "#% increased chance for Equipment Items dropped in your Maps to have Memory Strands",
        "#% increased chance for Maps found in your Maps to have Memory Influence",
        "#% increased chance to find Eater of Worlds Altars in your Maps",
        "#% increased effect of Explicit Modifiers on your Maps",
        "#% more Basic Currency Items found from Beyond Demons in your Maps\nthat are followers of Beidat",
        "#% more Divination Cards found from Beyond Demons in your Maps\nthat are followers of K'Tash",
        "#% more Unique Items found from Beyond Demons in your Maps\nthat are followers of Ghorr",
        "Abyss Cracks in your Maps have #% chance to spawn all Monsters as at least Magic",
        "Abyss Pits in your Maps have #% chance to spawn all Monsters as at least Magic",
        "Abysses in your Maps have #% increased chance to lead to an Abyssal Depths",
        "Abysses in your Maps that do not lead to an Abyssal Depths have #% increased chance to lead to a Stygian Spire",
        "Beyond Demons in your Maps grant #% increased Experience",
        "Beyond Portals in your Maps have #% increased chance to spawn a Unique Boss",
        "Bismuth Ore Deposits in your Maps have #% chance to\nadd an additional Modifier to Monsters they affect",
        "Blight Encounters in your Maps spawn #% more Non-Unique Monsters",
        "Blight Monsters in your Maps take #% increased Damage",
        "Buffs granted by Orichalcum Ore Deposits in your Maps have #% increased Duration",
        "Completing the final Ritual Altar in your Maps has #% chance to drop a Blood-filled Vessel",
        "Crimson Iron Ore Deposits in your Maps are guarded by an additional Corrupted Growth",
        "Currency Items from Strongboxes in your Maps are Duplicated",
        "Delirium Fog in your Maps lasts # additional seconds before dissipating",
        "Delirium Rewards in your Maps have #% increased chance to give Delirium Orbs",
        "Delirium in your Maps increases #% faster with distance from the mirror",
        "Divination Cards from Strongboxes in your Maps are Duplicated",
        "Expedition Monsters in your Maps spawn with an additional #% of Life missing",
        "Expeditions in your Maps have #% increased chance to be led by Dannig",
        "Expeditions in your Maps have #% increased chance to be led by Gwennen",
        "Expeditions in your Maps have #% increased chance to be led by Rog",
        "Expeditions in your Maps have #% increased chance to be led by Tujen",
        "Final Map Boss in each Map has #% chance to drop an additional Scarab",
        "Final Map Boss in each Map has #% chance to drop an additional connected Map",
        "Gems contained in Strongboxes in your Maps are Duplicated",
        "Harbingers in your Maps have #% chance to be replaced by a powerful Harbinger boss",
        "Harvest Monsters in your Maps drop #% increased Quantity of Lifeforce",
        "Harvests in your Maps have #% chance for the unchosen Crop to not wilt",
        "Heist Contracts found in your Maps are #% more likely to target High Value Targets",
        "Heist Contracts found in your Maps are #% more likely to target Precious Targets",
        "Immortal Syndicate Members in your Maps have #% chance to drop an additional Veiled Item",
        "Immortal Syndicate Members in your Maps have #% increased chance to be accompanied by reinforcements",
        "Imprisoned Monsters in your Maps have #% chance to have 3 additional Essences",
        "Inscribed Ultimatums found in your Maps have #% increased chance to reward Currency Items",
        "Inscribed Ultimatums found in your Maps have #% increased chance to reward Divination Cards",
        "Inscribed Ultimatums found in your Maps have #% increased chance to reward Unique Items",
        "Items dropped by Unique Monsters have #% chance to be Corrupted",
        "Killing non-resident Architects in your Maps has #% chance to add\nan additional Upgrade Tier to the surviving Architect's Room",
        "Legion Encounters in your Maps have #% increased chance to include a Karui army",
        "Legion Encounters in your Maps have #% increased chance to include a Maraketh army",
        "Legion Encounters in your Maps have #% increased chance to include a Templar army",
        "Legion Encounters in your Maps have #% increased chance to include a Vaal army",
        "Legion Encounters in your Maps have #% increased chance to include an Eternal Empire army",
        "Legion Monsters in your Maps which have Rewards have #% chance to gain two additional Rewards, and if not have #% chance to gain one additional Reward",
        "Maps from Strongboxes in your Maps are Duplicated",
        "Monster Packs Influenced by The Elder in your Maps have #% increased Pack Size",
        "Monster Packs Influenced by The Shaper in your Maps have #% increased Pack Size",
        "Monsters Influenced by The Eater of Worlds in your Maps have #% chance to drop an item with an Eater of Worlds Implicit Modifier",
        "Monsters Sacrificed at Ritual Altars in your Maps grant #% increased Tribute",
        "Oils found in your Maps have #% chance to be 1 tier higher",
        "Petrified Amber Ore Deposits in your Maps take #% increased Damage",
        "Rare Monsters in your Maps have #% increased chance to drop Scarabs per Monster Modifier affecting them",
        "Red Beasts captured in your Maps have a #% chance to gain a Modifier that provides a chance to not to be consumed when sacrificed at the Blood Altar",
        "Red Beasts in your Maps have #% chance to appear in Pairs",
        "Remnants in your Maps have #% chance to have an additional Suffix Modifier",
        "Ritual Altars in your Maps spawn Monsters #% faster",
        "Shrines in your Maps have #% chance to be guarded by an additional Pack of Monsters",
        "Smuggler's Caches drop #% more Rogue Markers for each Smuggler's Cache opened in the Area",
        "Smuggler's Caches in your Maps have #% increased chance to drop Contracts",
        "Splinters contained in Legion Chests in your Maps have #% chance to be Duplicated",
        "Splinters dropped by Legion Monsters in your Maps have #% chance to be Duplicated",
        "Splinters dropped by Legion Monsters or contained in Legion Chests in your Maps have #% chance to be Duplicated",
        "The Sacred Grove in your Maps has #% chance to contain an additional Harvest",
        "Ultimatum Encounters in your Maps spawn #% increased number of Monsters",
        "Ultimatum Monsters in your Maps grant #% increased Experience",
        "Up to # Rare Monsters in each of your Maps are Possessed and their Minions are Touched",
        "Vaal Side Areas in your Maps have #% chance for Rewards from Vaal Vessels to be Duplicated",
        "Verisium Ore Deposits in your Maps can be channelled on for #% longer",
        "Voltaxic Sulphite Veins and Chests in your Maps have #% chance to contain double Sulphite",
        "Wild Rogue Exiles in your Maps have #% chance to be Possessed by a Tormented Spirit",
        "You gain #% increased Damage per stack of Sulphite Intoxication",
        "Your Maps are haunted by an additional Tormented Spirit",
        "Your Maps contain # additional Strongboxes",
        "Your Maps contain an additional Harbinger",
        "Your Maps contain an additional Imprisoned Monster",
        "Your Maps contain an additional Shrine",
        "Your Maps have #% chance to grant an additional Kirac Mission on Completion",
        "Your Maps have #% increased chance to contain Alva",
        "Your Maps have #% increased chance to contain Einhar",
        "Your Maps have #% increased chance to contain Jun",
        "Your Maps have #% increased chance to contain Niko",
        "Your Maps have #% increased chance to contain Ritual Altars",
        "Your Maps have #% increased chance to contain The Sacred Grove",
        "Your Maps have #% increased chance to contain a Blight Encounter",
        "Your Maps have #% increased chance to contain a Legion Encounter",
        "Your Maps have #% increased chance to contain a Mirror of Delirium",
        "Your Maps have #% increased chance to contain a Smuggler's Cache",
        "Your Maps have #% increased chance to contain an Abyss",
        "Your Maps have #% increased chance to contain an Expedition Encounter",
        "Your Maps have #% increased chance to contain an Ultimatum Encounter",
        "Your Maps have +#% chance to be haunted by a Tormented Spirit",
        "Your Maps have +#% chance to contain Alva",
        "Your Maps have +#% chance to contain Einhar",
        "Your Maps have +#% chance to contain Jun",
        "Your Maps have +#% chance to contain Niko",
        "Your Maps have +#% chance to contain Ore Deposits",
        "Your Maps have +#% chance to contain Ritual Altars",
        "Your Maps have +#% chance to contain The Sacred Grove",
        "Your Maps have +#% chance to contain a Blight Encounter",
        "Your Maps have +#% chance to contain a Legion Encounter",
        "Your Maps have +#% chance to contain a Mirror of Delirium",
        "Your Maps have +#% chance to contain a Rogue Exile",
        "Your Maps have +#% chance to contain a Shrine",
        "Your Maps have +#% chance to contain a Smuggler's Cache",
        "Your Maps have +#% chance to contain a Strongbox",
        "Your Maps have +#% chance to contain a Trial of Ascendancy",
        "Your Maps have +#% chance to contain an Abyss",
        "Your Maps have +#% chance to contain an Expedition Encounter",
        "Your Maps have +#% chance to contain an Imprisoned Monster",
        "Your Maps have +#% chance to contain an Ultimatum Encounter",
        "Your Maps have a #% chance to contain an additional Harbinger",
        "Your Maps have a #% chance to contain an additional Rogue Exile",
        "Your Maps that contain capturable Beasts contain # additional Yellow Beast",
        "Your Maps with Ore Deposits have #% increased chance\nto contain at least two Ore Deposits",
    ],
    "Conqueror Idol": [
        "#% chance for Timeless Splinters to drop as Timeless Emblems instead in your Maps",
        "#% chance for your Maps to attract Beyond Demons",
        "#% chance on Completing your Maps to gain a free use of a random Map Crafting option",
        "#% chance on Completing your Maps to gain a free use of a special Map Crafting option",
        "#% increased Explosive Placement Range in your Maps",
        "#% increased Pack Size in your Maps",
        "#% increased Quantity of Items found in your Maps",
        "#% increased Stack size of Simulacrum Splinters found in your Maps",
        "#% increased effect of Explicit Modifiers on your Maps per 5% Map Quality",
        "#% increased effect of Explicit Modifiers on your Maps per Explicit Modifier",
        "Abyss Jewels dropped by Abyssal Troves or Stygian Spires in your Maps have a #% Chance to be Rare and Corrupted",
        "Abyss Jewels found in Abyssal Troves or dropped by Stygian Spires in your Maps have #% chance to be Corrupted and have 5 or 6 random Modifiers",
        "Abyss Pits in your Maps have #% chance to spawn 5 additional Rare Monsters",
        "Abyssal Troves and Stygian Spires in your Maps have #% chance to drop an Abyss Scarab",
        "Abysses in your Maps spawn #% increased Monsters for each prior Pit in that Abyss",
        "Abysses in your Maps that do not lead to an Abyssal Depths lead to 4 Pits if able",
        "Abysses in your Maps that do not lead to an Abyssal Depths lead to at least 3 Pits if able",
        "Beasts in your Maps are more likely to be less common varieties",
        "Beasts in your Maps have a #% chance to break free\nBeasts which break free in your Maps gain Bestial Rage\nDefeating Beasts grants Hunters' Cunning per Bestial Rage on the defeated Beast",
        "Blight Towers in your Maps can be Salvaged after the Blight Encounter\nHigher Tier Towers grant better Salvaged Rewards\nSalvaged Rewards are improved for each different Tower Type built during Encounter",
        "Blight chests in your Maps have a #% chance to be openable again",
        "Blueprints that drop in your Maps have #% chance to be fully Revealed",
        "Completing a Blight Encounter in your Maps grants all Players Blightreach",
        "Completing your Maps grants # Intelligence for a random Immortal Syndicate Safehouse",
        "Currency Shards dropped by Harbingers in your Maps can drop as Currency Items instead",
        "Defeating a Map Boss while Witnessed by The Maven has #% chance to count as also Witnessing an additional random Map Boss",
        "Deferring Favours at Ritual Altars in your Maps costs #% increased Tribute",
        "Delirious Unique Monsters in your Maps have a #% chance to drop an additional Cluster Jewel",
        "Delirious Unique Monsters in your Maps have a #% chance to drop an additional Delirium Orb",
        "Delirium Encounters in your Maps have #% chance to generate three additional Reward types",
        "Einhar remains in your Maps after his Mission is Complete",
        "Eldritch Embers found in your Maps influenced by The Searing Exarch have #% chance to be Duplicated",
        "Essences found in your Maps are a tier higher",
        "Expeditions in your Maps have +# Remnants",
        "Gain Demonic Power on defeating a Beyond Boss in your Maps",
        "Harvested Plants in your Maps have #% chance to spawn an additional Monster",
        "Huck accompanies you on opening the first Smuggler's Cache in each of your Maps",
        "Immortal Syndicate Members in your Maps drop #% more\nItems when Bargained with for Items",
        "Imprisoned Monsters in your Maps have at least 1 Essence at the highest possible tier",
        "Incursions in your Maps contain Cursed Treasures",
        "Incursions in your Maps contain a Vaal Flesh Merchant",
        "Killing resident Architects in your Maps adds their Upgrade Tier to the surviving Architect's Room",
        "Labyrinth Trials in your Maps have #% chance to award an Improved Offering to the Goddess",
        "Legion Encounters in your Maps contain # additional Sergeant",
        "Legion Encounters with a General in your Maps have both Generals",
        "Lifeforce dropped by Harvest Monsters in your Maps has #% chance to be Duplicated",
        "Map Device has #% chance not to consume Scarabs",
        "Maps found in your Maps have #% chance to have layers of Delirium",
        "Monster Packs Influenced by The Eater of Worlds in your Maps have #% increased Pack Size",
        "Ore Deposits in your Maps are more likely to be rarer varieties",
        "Ore Deposits in your Maps are replaced by Lost Shipments",
        "Plants Harvested in your Maps have #% chance to spawn duplicated Monsters",
        "Ritual Altars in your Maps allow rerolling Favours an additional time",
        "Scarabs found in your Maps are more likely to be less common varieties",
        "Shrines in your Maps are guarded by at least one Magic Pack",
        "Shrines in your Maps grant a random additional Shrine Effect",
        "Shrines in your Maps have #% chance to be a Covetous Shrine",
        "Slaying Enemies in your Maps has a #% increased chance to spawn a Beyond Portal",
        "Smuggler's Caches in your Maps have #% increased chance to contain Blueprints for each Smuggler's Cache opened in the Map",
        "Strongboxes in your Maps are Corrupted",
        "Strongboxes in your Maps are at least Rare",
        "Strongboxes opened in your Maps have #% chance to be openable again",
        "Synthesised Monsters in Synthesis Maps have #% increased Pack Size",
        "The number of Memory Strands on Equipment Items found\nin your Maps has #% chance to be Lucky",
        "Time gained from Kills is Doubled for Incursions in your Maps",
        "Tormented Spirits in your Maps are more likely to be less common varieties",
        "Ultimatum Boss drops a full stack of a random Catalyst",
        "Ultimatum Encounters in your Maps grant rewards as though you completed an additional Round",
        "Ultimatum Rewards in your Maps have #% chance to be duplicated",
        "Using a Vaal Orb on Imprisoned Monsters in your Maps replaces all Essences with one of the Essences on the Imprisoned Monster",
        "Varieties of Items contained in # Blight Chests are Lucky",
        "Voltaxic Sulphite Veins and Chests found in your Maps have #% chance to contain Doomed Spirits",
        "Voltaxic Sulphite Veins and Chests in your Maps are guarded by Sulphite-hoarding Monsters",
        "Wild Rogue Exiles in your Maps have #% chance to have additional Rewards",
        "Yellow Beasts in your Maps have #% chance to be replaced with Red Beasts",
        "You gain +#% to all maximum Elemental Resistances per stack of Sulphite Intoxication",
        "Your Maps are haunted by an additional Tormented Spirit",
        "Your Maps contain # additional Strongboxes",
        "Your Maps contain #% increased number of Runic Monster Markers",
        "Your Maps contain an additional Harbinger",
        "Your Maps contain an additional Imprisoned Monster",
        "Your Maps contain an additional Shrine",
        "Your Maps have #% chance to award double progress towards encountering The Searing Exarch",
        "Your Maps have #% increased chance to contain Alva",
        "Your Maps have #% increased chance to contain Einhar",
        "Your Maps have #% increased chance to contain Jun",
        "Your Maps have #% increased chance to contain Niko",
        "Your Maps have #% increased chance to contain Ritual Altars",
        "Your Maps have #% increased chance to contain The Sacred Grove",
        "Your Maps have #% increased chance to contain a Blight Encounter",
        "Your Maps have #% increased chance to contain a Legion Encounter",
        "Your Maps have #% increased chance to contain a Mirror of Delirium",
        "Your Maps have #% increased chance to contain a Smuggler's Cache",
        "Your Maps have #% increased chance to contain an Abyss",
        "Your Maps have #% increased chance to contain an Expedition Encounter",
        "Your Maps have #% increased chance to contain an Ultimatum Encounter",
        "Your Maps have +#% chance to be haunted by a Tormented Spirit",
        "Your Maps have +#% chance to contain Alva",
        "Your Maps have +#% chance to contain Einhar",
        "Your Maps have +#% chance to contain Jun",
        "Your Maps have +#% chance to contain Niko",
        "Your Maps have +#% chance to contain Ore Deposits",
        "Your Maps have +#% chance to contain Ritual Altars",
        "Your Maps have +#% chance to contain The Sacred Grove",
        "Your Maps have +#% chance to contain a Blight Encounter",
        "Your Maps have +#% chance to contain a Legion Encounter",
        "Your Maps have +#% chance to contain a Mirror of Delirium",
        "Your Maps have +#% chance to contain a Rogue Exile",
        "Your Maps have +#% chance to contain a Shrine",
        "Your Maps have +#% chance to contain a Smuggler's Cache",
        "Your Maps have +#% chance to contain a Strongbox",
        "Your Maps have +#% chance to contain an Abyss",
        "Your Maps have +#% chance to contain an Abyss per 2% increased Pack Size",
        "Your Maps have +#% chance to contain an Expedition Encounter",
        "Your Maps have +#% chance to contain an Imprisoned Monster",
        "Your Maps have +#% chance to contain an Ultimatum Encounter",
        "Your Maps have a #% chance to contain 20 additional Rogue Exiles",
        "Your Maps have a #% chance to contain an additional Harbinger",
        "Your Maps have a #% chance to contain an additional Rogue Exile",
        "Your Maps that contain Smuggler's Caches have a #% chance to contain 6 additional Smuggler's Caches",
        "Your Maps with Incursions always have four Incursions",
        "Your Maps with Ritual Altars always have four Ritual Altars",
    ],
}
# When True, the script will crawl live listings to discover idol affixes
# and use those for price checks instead of AFFIX_NAMES.
USE_DISCOVERED_AFFIXES = False

# ==========================
# Trade API endpoints
# ==========================
BASE_URL = "https://www.pathofexile.com"
STATS_URL = f"{BASE_URL}/api/trade/data/stats"
ITEMS_URL = f"{BASE_URL}/api/trade/data/items"
LEAGUES_URL = f"{BASE_URL}/api/trade/data/leagues"
FETCH_URL = f"{BASE_URL}/api/trade/fetch"


def _sleep():
    time.sleep(1)


def _make_session() -> requests.Session:
    sess = requests.Session()
    sess.headers.update({"User-Agent": USER_AGENT})
    if POESESSID and POESESSID != "YOUR_POESESSID_HERE":
        sess.cookies.set("POESESSID", POESESSID, domain=".pathofexile.com")
    return sess


def fetch_stat_id_map(sess: requests.Session) -> Dict[str, List[str]]:
    """Return mapping of stat text -> list of stat ids."""
    resp = sess.get(STATS_URL, timeout=30)
    resp.raise_for_status()
    _sleep()

    data = resp.json()
    mapping: Dict[str, List[str]] = {}
    for group in data.get("result", []):
        for entry in group.get("entries", []):
            text = entry.get("text")
            stat_id = entry.get("id")
            if not text or not stat_id:
                continue
            mapping.setdefault(text, []).append(stat_id)
    return mapping


def build_search_payload(stat_id: str, base_type: Optional[str] = None) -> Dict:
    payload = {
        "query": {
            "status": {"option": "online"},
            "stats": [
                {
                    "type": "and",
                    "filters": [
                        {
                            "id": stat_id,
                            "value": {"min": 1},
                        }
                    ],
                }
            ],
            "filters": {
                "type_filters": {
                    "filters": {
                        "category": {"option": "idol"}
                    }
                },
                "misc_filters": {
                    "filters": {
                        "rarity": {"option": "magic"}
                    }
                }
            },
        },
        "sort": {"price": "asc"},
    }
    if base_type:
        payload["query"]["type"] = base_type
    return payload


def search_affix(
    sess: requests.Session,
    league: str,
    stat_id: str,
    base_type: Optional[str],
) -> Tuple[str, List[str]]:
    payload = build_search_payload(stat_id, base_type=base_type)
    search_url = f"{BASE_URL}/api/trade/search/{quote(league)}"
    resp = sess.post(search_url, json=payload, timeout=30)
    resp.raise_for_status()
    _sleep()

    data = resp.json()
    query_id = data.get("id")
    result_ids = data.get("result", [])
    return query_id, result_ids


def fetch_trade_leagues(sess: requests.Session) -> List[Dict]:
    resp = sess.get(LEAGUES_URL, timeout=30)
    resp.raise_for_status()
    _sleep()
    data = resp.json()
    return data.get("result", [])


def fetch_idol_base_types(sess: requests.Session) -> List[str]:
    """Return idol base types from trade data items."""
    resp = sess.get(ITEMS_URL, timeout=30)
    resp.raise_for_status()
    _sleep()
    data = resp.json()
    for group in data.get("result", []):
        if group.get("id") == "idol" or group.get("label") == "Idol":
            base_types = []
            for entry in group.get("entries", []):
                # Base types have only "type" without unique flags or text/name.
                if "type" in entry and "flags" not in entry and "text" not in entry and "name" not in entry:
                    base_types.append(entry["type"])
            return sorted(set(base_types))
    return []


def build_discovery_payload(base_type: str) -> Dict:
    return {
        "query": {
            "status": {"option": "online"},
            "type": base_type,
            "filters": {
                "type_filters": {
                    "filters": {
                        "category": {"option": "idol"}
                    }
                },
                "misc_filters": {
                    "filters": {
                        "rarity": {"option": "magic"}
                    }
                }
            },
        },
        "sort": {"price": "asc"},
    }


def search_idol_base(sess: requests.Session, league: str, base_type: str) -> Tuple[str, List[str]]:
    payload = build_discovery_payload(base_type)
    search_url = f"{BASE_URL}/api/trade/search/{quote(league)}"
    resp = sess.post(search_url, json=payload, timeout=30)
    resp.raise_for_status()
    _sleep()
    data = resp.json()
    return data.get("id"), data.get("result", [])


def fetch_prices(
    sess: requests.Session,
    query_id: str,
    result_ids: List[str],
) -> List[Tuple[float, str]]:
    if not result_ids:
        return []

    limited_ids = result_ids[:5]
    ids_csv = ",".join(limited_ids)
    url = f"{FETCH_URL}/{ids_csv}?query={query_id}"

    resp = sess.get(url, timeout=30)
    resp.raise_for_status()
    _sleep()

    data = resp.json()
    prices: List[Tuple[float, str]] = []
    for item in data.get("result", []):
        listing = item.get("listing", {})
        price = listing.get("price")
        if not price:
            continue
        amount = price.get("amount")
        currency = price.get("currency")
        if amount is None or not currency:
            continue
        prices.append((float(amount), currency))
    return prices


def fetch_items(
    sess: requests.Session,
    query_id: str,
    result_ids: List[str],
) -> List[Dict]:
    if not result_ids:
        return []
    ids_csv = ",".join(result_ids)
    url = f"{FETCH_URL}/{ids_csv}?query={query_id}"
    resp = sess.get(url, timeout=30)
    resp.raise_for_status()
    _sleep()
    data = resp.json()
    return data.get("result", [])


def min_chaos_price(prices: List[Tuple[float, str]]) -> Optional[float]:
    chaos_prices = [amount for amount, currency in prices if currency == "chaos"]
    if not chaos_prices:
        return None
    return min(chaos_prices)


def chunked(items: List[str], size: int) -> List[List[str]]:
    return [items[i:i + size] for i in range(0, len(items), size)]


def discover_affixes(
    sess: requests.Session,
    league: str,
    base_types: List[str],
    sample_per_base: int = 20,
) -> Dict[str, List[str]]:
    affixes_by_base: Dict[str, set] = {}
    for base in base_types:
        try:
            query_id, result_ids = search_idol_base(sess, league, base)
        except requests.RequestException:
            affixes_by_base[base] = set()
            continue

        sample_ids = result_ids[:sample_per_base]
        mods: set = set()
        for batch in chunked(sample_ids, 10):
            try:
                items = fetch_items(sess, query_id, batch)
            except requests.RequestException:
                continue
            for item in items:
                explicit = item.get("item", {}).get("explicitMods", []) or []
                for mod in explicit:
                    mods.add(mod)
        affixes_by_base[base] = mods
    return {k: sorted(v) for k, v in affixes_by_base.items()}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Price-check Magic Idols via the PoE trade API.")
    parser.add_argument("--league", default=LEAGUE_NAME, help="League name for the trade API.")
    parser.add_argument("--list-leagues", action="store_true", help="Print trade API league names and exit.")
    parser.add_argument("--discover-affixes", action="store_true", help="Discover idol affixes from live listings.")
    parser.add_argument("--affix-sample", type=int, default=20, help="Listings per idol base to sample for affixes.")
    parser.add_argument("--affix-output", default="", help="Write discovered affixes to this file.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    league = args.league
    if not AFFIX_NAMES and not USE_DISCOVERED_AFFIXES:
        if not (args.list_leagues or args.discover_affixes):
            print("No affixes provided.")
            return 1

    sess = _make_session()

    if args.list_leagues:
        try:
            leagues = fetch_trade_leagues(sess)
        except requests.RequestException as exc:
            print(f"Failed to fetch leagues: {exc}")
            return 1
        for entry in leagues:
            print(f"{entry.get('text')} (id={entry.get('id')}, realm={entry.get('realm')})")
        if not args.discover_affixes:
            return 0

    discovered_affixes_by_base: Dict[str, List[str]] = {}
    if args.discover_affixes or USE_DISCOVERED_AFFIXES:
        try:
            base_types = fetch_idol_base_types(sess)
        except requests.RequestException as exc:
            print(f"Failed to fetch idol base types: {exc}")
            return 1
        if not base_types:
            print("No idol base types found.")
            return 1
        affixes_by_base = discover_affixes(sess, league, base_types, args.affix_sample)
        all_affixes = sorted({mod for mods in affixes_by_base.values() for mod in mods})
        discovered_affixes_by_base = affixes_by_base

        if args.discover_affixes and args.affix_output:
            with open(args.affix_output, "w", encoding="utf-8") as f:
                f.write("# Affixes by idol base\n")
                for base, mods in affixes_by_base.items():
                    f.write(f"\n[{base}]\n")
                    for mod in mods:
                        f.write(f"- {mod}\n")
                f.write("\n# Combined affix list\n")
                for mod in all_affixes:
                    f.write(f"- {mod}\n")
        elif args.discover_affixes:
            print("AFFIX_NAMES = {")
            for base in sorted(affixes_by_base.keys()):
                print(f"    \"{base}\": [")
                for mod in affixes_by_base[base]:
                    print(f"        \"{mod}\",")
                print("    ],")
            print("}")
        if args.discover_affixes and not USE_DISCOVERED_AFFIXES and not AFFIX_NAMES:
            return 0

    affixes_by_base = discovered_affixes_by_base if USE_DISCOVERED_AFFIXES else AFFIX_NAMES
    if not affixes_by_base:
        print("No affixes available to check.")
        return 1

    try:
        stat_map = fetch_stat_id_map(sess)
    except requests.RequestException as exc:
        print(f"Failed to fetch stats: {exc}")
        return 1

    for base_type in sorted(affixes_by_base.keys()):
        for affix in affixes_by_base[base_type]:
            stat_ids = stat_map.get(affix, [])
            if not stat_ids:
                print(f"{base_type} | {affix}: STAT ID NOT FOUND (check exact text)")
                continue
            if len(stat_ids) > 1:
                # If multiple IDs match the same text, pick the first and warn.
                print(f"{base_type} | {affix}: multiple stat IDs found {stat_ids}; using {stat_ids[0]}")
            stat_id = stat_ids[0]

            try:
                query_id, result_ids = search_affix(sess, league, stat_id, base_type)
            except requests.RequestException as exc:
                print(f"{base_type} | {affix}: search failed: {exc}")
                continue

            if not result_ids:
                print(f"{base_type} | {affix}: no results")
                continue

            try:
                prices = fetch_prices(sess, query_id, result_ids)
            except requests.RequestException as exc:
                print(f"{base_type} | {affix}: fetch failed: {exc}")
                continue

            min_price = min_chaos_price(prices)
            if min_price is None:
                print(f"{base_type} | {affix}: no chaos listings in first 5 results")
            else:
                print(f"{base_type} | {affix}: minimum price = {min_price} chaos")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
