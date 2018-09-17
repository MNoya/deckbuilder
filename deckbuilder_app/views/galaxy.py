import json

from django.shortcuts import render
from django.views.generic import DetailView

from deckbuilder_app.models import GalaxyMap


def galaxy_map_list(request):
    template_name = 'views/galaxy_list.html'

    map_list = []
    for galaxy_map in GalaxyMap.objects.all():
        map_list.append({
            'name': galaxy_map.name,
            'id': galaxy_map.id,
            'cards': [card.name for card in galaxy_map.cards.all()]
        })

    return render(request, template_name=template_name, context=({'maps': json.dumps(map_list)}))


class GalaxyDetailView(DetailView):
    model = GalaxyMap
    template_name = 'views/galaxy_detail.html'

    def get_context_data(self, **kwargs):
        context = super(GalaxyDetailView, self).get_context_data(**kwargs)
        return context
