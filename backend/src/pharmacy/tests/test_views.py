import pytest
from rest_framework import status
from rest_framework.test import APIClient

from pharmacy.models import Inventory, Pharmacy


@pytest.mark.django_db
def test_pharmacy_list(authenticated_client: APIClient) -> None:
    url = '/pharmacy/'
    response = authenticated_client.get(url)
    assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
def test_inventory_per_pharmacy_list(
    authenticated_client: APIClient,
    pharmacy: Pharmacy,
    inventory: Inventory,
) -> None:
    url = f'/pharmacy/{pharmacy.uuid}/inventory/'
    response = authenticated_client.get(url)

    # assert the status code and the first inventory item is equal or not
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['name'] == inventory.name


@pytest.mark.django_db
def test_inventory_list(authenticated_client: APIClient, inventory: Inventory) -> None:
    url = '/pharmacy/inventory/'
    response = authenticated_client.get(url)

    # assert the status code and the first item is equal or not
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['inventoryName'] == inventory.name


@pytest.mark.django_db
def test_inventory_count(authenticated_client: APIClient, inventory: Inventory) -> None:
    url = '/pharmacy/inventory/count/'
    response = authenticated_client.get(url)

    # assert the status code
    assert response.status_code == status.HTTP_200_OK
    assert response.json()[0]['inventoryCount'] == 100


@pytest.mark.django_db
def test_inventory_quantity_update(
    authenticated_client: APIClient,
    inventory: Inventory,
) -> None:
    url = f'/pharmacy/inventory/{inventory.uuid}/update-quantity/'
    data = {'delta': 10}

    response = authenticated_client.put(url, data, format='json')

    # assert the status code
    assert response.status_code == status.HTTP_200_OK

    # refresh from db to check
    inventory.refresh_from_db()
    assert inventory.stock_quantity == 110


@pytest.mark.django_db
def test_inventory_bulk_create(
    authenticated_client: APIClient,
    pharmacy: Pharmacy,
) -> None:
    url = f'/pharmacy/{pharmacy.uuid}/inventory/bulk-create/'
    data = [
        {
            'name': 'Mask B',
            'color': 'blue',
            'count_per_pack': 5,
            'price': 20,
            'stock_quantity': 50,
        },
        {
            'name': 'Mask C',
            'color': 'green',
            'count_per_pack': 6,
            'price': 30,
            'stock_quantity': 60,
        },
    ]

    # request to create
    response = authenticated_client.post(url, data, format='json')
    assert response.status_code == status.HTTP_201_CREATED

    # check if the inventories were created
    assert Inventory.objects.filter(pharmacy=pharmacy, name='Mask B').exists()
    assert Inventory.objects.filter(pharmacy=pharmacy, name='Mask C').exists()


@pytest.mark.django_db
def test_inventory_bulk_update(
    authenticated_client: APIClient,
    pharmacy: Pharmacy,
    inventory: Inventory,
) -> None:
    url = f'/pharmacy/{pharmacy.uuid}/inventory/bulk-update/'
    data = [
        {
            'uuid': str(inventory.uuid),
            'name': 'Mask A Updated',
            'color': 'red',
            'count_per_pack': 4,
            'price': 15,
            'stock_quantity': 120,
        },
    ]

    # request to update
    response = authenticated_client.put(url, data, format='json')

    # check status code
    assert response.status_code == status.HTTP_200_OK

    # assert to check the results
    inventory.refresh_from_db()
    assert inventory.name == 'Mask A Updated'
    assert inventory.price == 15
    assert inventory.stock_quantity == 120
