import pytest

from member.models import Member
from pharmacy.models import Inventory, Pharmacy


@pytest.fixture
def member() -> Member:
    return Member.objects.create(name='Test User', cash_balance=1000.0)


@pytest.fixture
def pharmacy() -> Pharmacy:
    return Pharmacy.objects.create(
        name='Test Pharmacy',
        cash_balance=345.6,
    )


@pytest.fixture
def inventory(pharmacy: Pharmacy) -> Inventory:
    return Inventory.objects.create(
        pharmacy=pharmacy,
        name='Mask A',
        color='red',
        count_per_pack=4,
        price=10,
        stock_quantity=100,
    )


@pytest.fixture
def inventory_snapshot(inventory: Inventory) -> Inventory:
    # Simulate snapshot creation
    return inventory.create_snapshot()
