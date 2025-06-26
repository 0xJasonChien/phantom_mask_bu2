# Response
## Brief Explanation of each API
* [ ] List pharmacies, optionally filtered by specific time and/or day of the week.
  * Implemented at `/pharmacy/` API.
  * with using `startTime`, `startTime_Gte`, `weekday`, `endTime_Lte`, `endTime` you can construct the filter of time and weekday
   <br>
* [ ] List all masks sold by a given pharmacy with an option to sort by name or price.
  * Implemented at `/pharmacy/<uuid>/inventory/` API.
  * You can get the result with filling up the uuid of pharmacy and filter by field like `price`, `price_Gt`, `price_Gte`, `price_Lt`, `price_Lte`
   <br>
* [ ] List all pharmacies that offer a number of mask products within a given price range, where the count is above, below, or between given thresholds.
  * Implemented at `/pharmacy/inventory/count/` API.
   <br>
* [ ] Show the top N users who spent the most on masks during a specific date range.
  * Implemented at `/member/purchase-ranking/` API.
  * with filling up the `top` argument and `purchaseDate` related field
   <br>
* [ ] Process a purchase where a user buys masks from multiple pharmacies at once.
  *  Implemented at `/member/<uuid>/create-purchase-history/` API.
   <br>
* [ ] Update the stock quantity of an existing mask product by increasing or decreasing it.
  * Implemented at `/pharmacy/inventory/<uuid>/update-quantity/` API.
   <br>
* [ ] Create or update multiple mask products for a pharmacy at once, including name, price, and stock quantity.
  * Implemented at `/pharmacy/<uuid>/inventory/bulk-update/` API for update.
  * Implemented at  `/pharmacy/<uuid>/inventory/bulk-create/` API for create.
   <br>
* [ ] Search for pharmacies or masks by name and rank the results by relevance to the search term.
  * Implemented at `/pharmacy/inventory/` API.
  * by filling up the search term, you can get the result

<br>

## API Document
The Swagger documentation was in PDF format generated using the `drf_spectacular` library. <br>
 You can explore and test the API after deployment via Docker. <br>
[ View the Swagger Documentation (PDF) ](https://github.com/user-attachments/files/20922153/Phantom.Mask.API.pdf)

### Preprocess before testing the api on swagger after the docker container is started up
> Be sure you have start up the container before starting the follow steps

1. Register an account for the system first
   <img width="1170" alt="Screenshot 2025-06-26 at 6 55 12 PM" src="https://github.com/user-attachments/assets/d0d028b8-dd4a-43a1-ae0a-65f0207c1a07" />
2. it will reponse a access key & refresh key for you, and go to the page fill in the access key
   <img width="1146" alt="Screenshot 2025-06-26 at 6 56 09 PM" src="https://github.com/user-attachments/assets/e4f4b8b6-64a3-4aad-9928-fb715afc2dca" />

   <img width="939" alt="Screenshot 2025-06-26 at 6 57 13 PM" src="https://github.com/user-attachments/assets/0c9635c6-46ea-4fda-8877-a012df0f77d5" />
3. after registered, you are ready to test

<br>

## Import Data Commands
I have written two commands for loading the initial data:
```bash
uv run python manage.py load_pharmacies
uv run python manage.py load_members
```
> However, you don't need to run them manually when using Docker, the entrypoint script will handle this.

<br>

## Test Coverage Report
I have written the unit tests, and the current test coverage is:
<br><br>
[![codecov](https://codecov.io/gh/0xJasonChien/phantom_mask_bu2/graph/badge.svg?token=SYRLPCTURX)](https://codecov.io/gh/0xJasonChien/phantom_mask_bu2)
<br>
![coverage chart](https://codecov.io/gh/0xJasonChien/phantom_mask_bu2/graphs/sunburst.svg?token=SYRLPCTURX)

> p.s. you can also trigger the [CI workflow](https://github.com/0xJasonChien/phantom_mask_bu2/actions/workflows/ci.yaml) to refresh the coverage.

<br>

## Deployment
I use Docker for deployment. please follow the setp to start up on  local. <br>

1. move to working directory
   ``` bash
   cd phantom_mask_bu2/backend/
   ```
3. Copy the `.env.example` and rename to `.env`
   ``` bash
   mv .env.example .env
   ```
4. edit the `.env` file
   ``` .env
   # django settings
   # please generate SECRET_KEY from https://djecrety.ir/
   SECRET_KEY=
   DEBUG=True

   # DB settings
   DB_USERNAME=phantom_mask
   DB_PASSWORD=phantom_mask
   DB_NAME=phantom_mask_db
   DB_PORT=5432
   DB_HOST=db
   ```
   > Please get a sercret key from [https://djecrety.ir/](https://djecrety.ir/) for SECRET_KEY value
   >  set the DEBUG to True, so that the API Document page is accessible in [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
5. Build and start the container

    ```
    docker compose up --build
    ```
    > p.s. when starting the container, the initial data will be loaded into DB, you don't have to run any command

<br>

## Additional Data
### ERD
```mermaid
erDiagram

    User {
        UUID uuid PK
        string email
        string username
        datetime created_at
        datetime updated_at
    }

    Pharmacy {
        UUID uuid PK
        string name
        float cash_balance
        datetime created_at
        datetime updated_at
    }

    OpeningHour {
        UUID uuid PK
        UUID pharmacy FK
        string weekday
        time start_time
        time end_time
        datetime created_at
        datetime updated_at
    }

    Inventory {
        UUID uuid PK
        UUID pharmacy FK
        string name
        string color
        int count_per_pack
        float price
        int stock_quantity
        datetime created_at
        datetime updated_at
    }

    InventorySnapshot {
        UUID uuid PK
        UUID pharmacy FK
        UUID inventory FK
        string pharmacy_name
        string inventory_name
        string color
        int count_per_pack
        float price
        datetime created_at
        datetime updated_at
    }

    Member {
        UUID uuid PK
        string name
        float cash_balance
        datetime created_at
        datetime updated_at
    }

    PurchaseHistory {
        UUID uuid PK
        UUID member FK
        UUID inventory FK
        float amount
        int quantity
        datetime purchase_date
        datetime created_at
        datetime updated_at
    }

    OpeningHour }o--|| Pharmacy : belongs_to
    Inventory }o--|| Pharmacy : belongs_to
    InventorySnapshot ||--|| Pharmacy : nullable_fk
    InventorySnapshot ||--|| Inventory : nullable_fk

    PurchaseHistory }o--|| Member : belongs_to
    PurchaseHistory ||--|| InventorySnapshot : uses_snapshot_for_logging
```
