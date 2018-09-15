from datetime import timedelta

DEFAULT_PROFILE_IMAGE = 'img/default/profile_image.jpg'
DEFAULT_CARD_IMAGE = 'img/default/card_image.png'
EXPIRY_TOKEN_DELTA = timedelta(days=7)

GET = 'GET'
POST = 'POST'

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

class Difficulties:
    NORMAL = 'Normal'
    NIGHTMARE = 'Nightmare'
    HELL = 'Hell'


RARITIES = [Rarities.NEWBIE, Rarities.COMMON, Rarities.RARE, Rarities.EPIC, Rarities.LEGEND]
RACES = [Races.EMPIRE, Races.ROCK, Races.INFERNO, Races.DEUS, Races.ZEN, Races.RECLUSE, Races.PARADISE]
CARD_TYPES = [CardTypes.UNIT, CardTypes.SPELL]
DIFFICULTIES = [Difficulties.NORMAL, Difficulties.NIGHTMARE, Difficulties.HELL]
