import json
import re
from typing import Self

from django.core.management.base import BaseCommand

from core.config.base import BASE_DIR
from pharmacy.models import Inventory, OpeningHour, Pharmacy


class Command(BaseCommand):

    def create_inventory(self: Self, pharmacy: Pharmacy, raw_inventory: list) -> None:
        to_create_inventory = []
        for item in raw_inventory:
            name, color, count_per_pack = re.findall(
                r'^(.*?)\s+\((.*?)\)\s+\((\d+)\s+per\s+pack\)$',
                item['name'],
            )[0]

            inventory = Inventory(
                pharmacy=pharmacy,
                name=name,
                color=color,
                count_per_pack=int(count_per_pack),
                price=item['price'],
                stock_quantity=item['stockQuantity'],
            )
            to_create_inventory.append(inventory)

        Inventory.objects.bulk_create(to_create_inventory)

    def create_opening_hours(
        self: Self,
        pharmacy: Pharmacy,
        raw_opening_hours: str,
    ) -> None:
        opening_hour_list = re.findall(
            r'(\w+) (\d{2}:\d{2}) - (\d{2}:\d{2})',
            raw_opening_hours,
        )

        to_create_opening_hours = []
        for item in opening_hour_list:
            weekday, start_time, end_time = item

            # Convert "24:00" to "00:00" if present
            # p.s. Django DateTimeField 不支援 24:00
            if start_time == '24:00':
                start_time = '00:00'
            if end_time == '24:00':
                end_time = '00:00'

            opening_hour = OpeningHour(
                pharmacy=pharmacy,
                weekday=weekday,
                start_time=start_time,
                end_time=end_time,
            )
            to_create_opening_hours.append(opening_hour)

        OpeningHour.objects.bulk_create(to_create_opening_hours)

    def handle(self: Self, *args: tuple, **options: dict) -> None:
        # load the data from json file
        pharmacies_file_path = BASE_DIR.parent.parent / 'data' / 'pharmacies.json'
        with pharmacies_file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            # create pharmacy
            pharmacy = Pharmacy(name=item['name'], cash_balance=item['cashBalance'])
            pharmacy.save()

            # create opening hours
            self.create_opening_hours(pharmacy, item['openingHours'])

            # create inventory
            self.create_inventory(pharmacy, item['masks'])
