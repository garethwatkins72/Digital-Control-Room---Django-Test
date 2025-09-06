from django.test import TestCase
from django.urls import reverse
from countries.models import Country, Region


class StatsViewTests(TestCase):
    def setUp(self):
        africa = Region.objects.create(name="Africa")
        americas = Region.objects.create(name="Americas")

        Country.objects.create(
            name="Nigeria",
            alpha2Code="NG",
            alpha3Code="NGA",
            population=200000000,
            region=africa,
        )
        Country.objects.create(
            name="Egypt",
            alpha2Code="EG",
            alpha3Code="EGY",
            population=100000000,
            region=africa,
        )
        Country.objects.create(
            name="Brazil",
            alpha2Code="BR",
            alpha3Code="BRA",
            population=210000000,
            region=americas,
        )

    def test_stats_view_returns_correct_data(self):
        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertIn("regions", data)
        self.assertEqual(len(data["regions"]), 2)

        africa_data = next(r for r in data["regions"] if r["name"] == "Africa")
        americas_data = next(r for r in data["regions"] if r["name"] == "Americas")

        # Check counts
        self.assertEqual(africa_data["number_countries"], 2)
        self.assertEqual(africa_data["total_population"], 300_000_000)
        self.assertEqual(americas_data["number_countries"], 1)
        self.assertEqual(americas_data["total_population"], 210_000_000)

    def test_stats_view_empty(self):
        # Delete all regions and countries
        Country.objects.all().delete()
        Region.objects.all().delete()

        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        self.assertEqual(data["regions"], [])

    def test_stats_view_region_with_no_countries(self):
        # Create a region with no countries
        empty_region = Region.objects.create(name="Antarctica")

        response = self.client.get(reverse("stats"))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        ant_data = next(r for r in data["regions"] if r["name"] == "Antarctica")
        self.assertEqual(ant_data["number_countries"], 0)
        self.assertEqual(ant_data["total_population"], 0)
