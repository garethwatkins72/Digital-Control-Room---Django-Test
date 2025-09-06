import json
import os
import requests

from django.conf import settings
from django.core.management.base import BaseCommand

from countries.models import Country, Region


class Command(BaseCommand):
    help = "Loads country data from https://storage.googleapis.com/dcr-django-test/countries.json."

    COUNTRIES_DATA_URL = "https://storage.googleapis.com/dcr-django-test/countries.json"

    def get_data(self):
        try:
            response = requests.get(self.COUNTRIES_DATA_URL, timeout=10)
            response.raise_for_status()
            data = response.json()
            return data
        except requests.exceptions.RequestException as e:
            # Handle network errors, timeouts, bad responses
            print(f"Error fetching data: {e}")
            return None

    def handle(self, *args, **options):
        data = self.get_data()

        # create any new regions
        existing_regions = Region.objects.all().values_list("name", flat=True)
        new_region_names = set(
            row["region"] for row in data if row["region"] not in existing_regions
        )

        Region.objects.bulk_create([Region(name=name) for name in new_region_names])

        for region in new_region_names:
            self.stdout.write(self.style.SUCCESS(f"Region: {region} - Created"))

        # create a map of existing regions and countries to minimize queries
        all_regions = Region.objects.all()
        region_map = {r.name: r for r in all_regions}

        # get existing countries
        existing_countries = Country.objects.filter(
            name__in=[row["name"] for row in data]
        )
        existing_map = {c.name: c for c in existing_countries}

        new_countries = []
        countries_to_update = []

        # prepare lists of new countries and countries to update
        for row in data:
            if row["name"] in existing_map:
                country = existing_map[row["name"]]
                country.alpha2Code = row["alpha2Code"]
                country.alpha3Code = row["alpha3Code"]
                country.population = row["population"]
                country.region = region_map[row["region"]]
                country.top_level_domain = row["topLevelDomain"]
                country.capital = row["capital"]
                countries_to_update.append(country)

            else:
                new_countries.append(
                    Country(
                        name=row["name"],
                        alpha2Code=row["alpha2Code"],
                        alpha3Code=row["alpha3Code"],
                        population=row["population"],
                        region=region_map[row["region"]],
                        top_level_domain=row["topLevelDomain"],
                        capital=row["capital"],
                    )
                )

        # perform bulk update/create and print results
        Country.objects.bulk_update(
            countries_to_update,
            [
                "alpha2Code",
                "alpha3Code",
                "population",
                "region",
                "top_level_domain",
                "capital",
            ],
        )
        for country in countries_to_update:
            self.stdout.write(self.style.SUCCESS(f"Country: {country} - Updated"))

        Country.objects.bulk_create(new_countries)
        for country in new_countries:
            self.stdout.write(self.style.SUCCESS(f"Country: {country} - Created"))

