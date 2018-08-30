from datetime import timedelta

DEFAULT_PROFILE_IMAGE_USER = 'default/profile_image.jpg'
EXPIRY_TOKEN_DELTA = timedelta(days=7)


class Rarities:
    NEWBIE = 'Newbie\'s'
    COMMON = 'Common'
    RARE = 'Rare'
    EPIC = 'Epic'
    LEGEND = 'Legendary'


class Races:
    EMPIRE = 'Quadruple Radiance Empire'
    ROCK = 'Roughrock Weald'
    ZEN = 'Zen Valley'
    INFERNO = 'Inferno'
    DEUS = 'Deus of Winter\'s Apostle'
    RECLUSE = 'Recluse'
    PARADISE = 'Paradise Harbor'


class CardTypes:
    UNIT = 'Unit'
    SPELL = 'Spell'


RARITIES = [Rarities.NEWBIE, Rarities.COMMON, Rarities.RARE, Rarities.EPIC, Rarities.LEGEND]
RACES = [Races.EMPIRE, Races.ROCK, Races.INFERNO, Races.DEUS, Races.ZEN, Races.RECLUSE, Races.PARADISE]
CARD_TYPES = [CardTypes.UNIT, CardTypes.SPELL]
