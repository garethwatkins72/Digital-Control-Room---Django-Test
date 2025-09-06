from django.http import JsonResponse
from django.db.models import Count, Sum
from countries.models import Country, Region


def stats(request):
    regions = Region.objects.annotate(
        number_countries=Count("countries"),
        total_population=Sum("countries__population"),
    )

    regions_data = [
        {
            "name": region.name,
            "number_countries": region.number_countries,
            "total_population": region.total_population or 0,
        }
        for region in regions
    ]

    response = {"regions": regions_data}
    return JsonResponse(response)
