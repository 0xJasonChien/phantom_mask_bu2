import json
import re
from datetime import datetime
from typing import Self

from django.core.management.base import BaseCommand
from django.utils import timezone

from core.config.base import BASE_DIR
from member.models import Member, PurchaseHistory
from pharmacy.models import Inventory, Pharmacy


class Command(BaseCommand):

    def prefetch_pharmacies(self: Self) -> dict[str, Pharmacy]:
        pharmacies = Pharmacy.objects.all()

        return {pharmacy.name: pharmacy for pharmacy in pharmacies}

    def create_purchase_history(
        self: Self,
        member: Member,
        raw_purchase_history: list,
    ) -> None:
        pharmacy_name_mapping = self.prefetch_pharmacies()

        to_create_purchase_history = []
        for item in raw_purchase_history:
            name, color, count_per_pack = re.findall(
                r'^(.*?)\s+\((.*?)\)\s+\((\d+)\s+per\s+pack\)$',
                item['maskName'],
            )[0]

            # convert native datetime to time zone aware
            naive_datetime = datetime.fromisoformat(item['transactionDatetime'])
            aware_datetime = timezone.make_aware(naive_datetime)

            inventory = Inventory.objects.get_or_create(
                pharmacy=pharmacy_name_mapping[item['pharmacyName']],
                name=name,
                color=color,
                count_per_pack=int(count_per_pack),
            )[0].create_snapshot()

            purchase_history = PurchaseHistory(
                member=member,
                inventory=inventory,
                amount=item['transactionAmount'],
                quantity=item['transactionQuantity'],
                purchase_date=aware_datetime,
            )
            to_create_purchase_history.append(purchase_history)

        PurchaseHistory.objects.bulk_create(to_create_purchase_history)

    def handle(self: Self, *args: tuple, **options: dict) -> None:
        # load the data from json file
        members_file_path = BASE_DIR / 'data' / 'users.json'
        with members_file_path.open('r', encoding='utf-8') as file:
            data = json.load(file)

        for item in data:
            # create member
            member = Member(name=item['name'], cash_balance=item['cashBalance'])
            member.save()

            # create purchase history
            self.create_purchase_history(member, item['purchaseHistories'])
