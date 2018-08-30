from django.contrib import admin

from deckbuilder_app import models


class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'cost', 'get_race_display', 'get_rarity_display', 'get_card_type_display')

    list_filter = ('race', 'rarity', 'card_type')

    def get_race_display(self, obj):
        return obj.get_race_display()

    get_race_display.short_description = 'Race'

    def get_rarity_display(self, obj):
        return obj.get_rarity_display()

    get_rarity_display.short_description = 'Rarity'

    def get_card_type_display(self, obj):
        return obj.get_card_type_display()

    get_card_type_display.short_description = 'Card Type'


class CardInlineAdmin(admin.TabularInline):
    model = models.CardInDeck


class DeckAdmin(admin.ModelAdmin):
    inlines = [CardInlineAdmin]


admin.site.register(models.Card, CardAdmin)
admin.site.register(models.Deck, DeckAdmin)
