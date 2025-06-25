import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from member.models import Member, PurchaseHistory
from pharmacy.models import Inventory


@pytest.mark.django_db
def test_create_purchase_history_success(
    authenticated_client: APIClient,
    member: Member,
    inventory: Inventory,
) -> None:
    url = f'/member/{member.uuid!s}/create-purchase-history/'
    data = [
        {
            'inventory_uuid': str(inventory.uuid),
            'quantity': 2,
        },
    ]

    response = authenticated_client.post(url, data, format='json')

    # calculate expected cash balance after purchase
    expected_cash_balance = member.cash_balance - inventory.price * 2
    member.refresh_from_db()
    assert response.status_code == status.HTTP_201_CREATED
    assert member.cash_balance == expected_cash_balance


@pytest.mark.django_db
def test_create_purchase_history_insufficient_balance(
    authenticated_client: APIClient,
    member: Member,
    inventory: Inventory,
) -> None:
    member.cash_balance = 10.0
    member.save()
    url = f'/member/{member.uuid!s}/create-purchase-history/'
    data = [
        {
            'inventory_uuid': str(inventory.uuid),
            'quantity': 2,
        },
    ]
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'not enough' in response.data['detail']


@pytest.mark.django_db
def test_create_purchase_history_out_of_stock(
    authenticated_client: APIClient,
    member: Member,
    inventory: Inventory,
) -> None:
    inventory.stock_quantity = 1
    inventory.save()

    url = f'/member/{member.uuid!s}/create-purchase-history/'
    data = [
        {
            'inventory_uuid': str(inventory.uuid),
            'quantity': 2,
        },
    ]

    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert 'out of stock' in response.data['detail']


@pytest.mark.django_db
def test_purchase_ranking_list(
    authenticated_client: APIClient,
    member: Member,
    inventory: Inventory,
) -> None:
    # Create some purchase history
    PurchaseHistory.objects.create(
        member=member,
        inventory=inventory.create_snapshot(),
        amount=200.0,
        quantity=2,
        purchase_date=timezone.now(),
    )
    url = '/member/purchase-ranking/'
    response = authenticated_client.get(url)

    assert response.status_code == status.HTTP_200_OK
    assert response.data[0]['member__uuid'] == str(member.uuid)
    assert response.data[0]['accumulated_amount'] == 200.0


@pytest.mark.django_db
def test_purchase_ranking_list_top_param(
    authenticated_client: APIClient,
    member: Member,
    inventory: Inventory,
) -> None:
    # Create two members and purchase histories
    member2 = Member.objects.create(name='User2', cash_balance=1000.0)
    PurchaseHistory.objects.create(
        member=member,
        inventory=inventory.create_snapshot(),
        amount=100.0,
        quantity=1,
        purchase_date=timezone.now(),
    )
    PurchaseHistory.objects.create(
        member=member2,
        inventory=inventory.create_snapshot(),
        amount=300.0,
        quantity=3,
        purchase_date=timezone.now(),
    )

    url = '/member/purchase-ranking/'
    response = authenticated_client.get(url, {'top': 1})

    assert response.status_code == status.HTTP_200_OK
    assert len(response.data) == 1
    assert response.data[0]['accumulated_amount'] == 300.0
