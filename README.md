# OdooLocust

An Odoo load testing solution, using odooRPC and Locust. Locust API changed a bit, and OdooLocust follow this change.

## Links

* OdooRPC: <a href="https://github.com/OCA/odoorpc">OCA/odoorpc</a>
* Locust: <a href="http://locust.io">locust.io</a>
* Odoo: <a href="https://odoo.com">odoo.com</a>

# Quick Start

Assuming you have a local odoo instance already up and running you can see the result of the sample loads included in this project:

1. Clone this repo

```
git clone https://github.com/trevi-software/OdooLocust.git
```

2. Create a python virtual environment and install required packages
```
cd OdooLocust
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Modify the connection values for your local odoo instance
```
vi OdooLocust/samples/Seller.py
vi OdooLocust/samples/GenericTest.py
```

4. To Run though the sale order load
```
locust -f OdooLocust/samples/Seller.py --config OdooLocust/samples/locust.conf
```

OR

4. To run through a bunch of users clicking on menu items randomly
```
locust -f OdooLocust/samples/GenericTest.py --config OdooLocust/samples/locust.conf
```

OR

4. To run both loads at the same time
```
locust -f OdooLocust/samples --config OdooLocust/samples/locust.conf
```

5. Open your web browser, point it to the locust instance you started and fire up the workload
```
http://localost:8089/
```

# HowTo

To load test Odoo, you create tests like you'll have done it with Locust:

```
from locust import task, between
from OdooLocust.OdooLocustUser import OdooLocustUser


class Seller(OdooLocustUser):
    wait_time = between(0.1, 10)
    database = "test_db"
    login = "admin"
    password = "secret_password"
    port = 443
    protocol = "jsonrpc+ssl"

    @task(10)
    def read_partners(self):
        cust_model = self.client.env['res.partner']
        cust_ids = cust_model.search([])
        prtns = cust_model.read(cust_ids)

    @task(5)
    def read_products(self):
        prod_model = self.client.env['product.product']
        ids = prod_model.search([])
        prods = prod_model.read(ids)

    @task(20)
    def create_so(self):
        prod_model = self.client.env['product.product']
        cust_model = self.client.env['res.partner']
        so_model = self.client.env['sale.order']

        cust_id = cust_model.search([('name', 'ilike', 'azure')])[0]
        prod_ids = prod_model.search([('name', 'ilike', 'desk')])

        order_id = so_model.create({
            'partner_id': cust_id,
            'order_line': [(0, 0, {'product_id': prod_ids[0],
                                   'product_uom_qty': 1}),
                           (0, 0, {'product_id': prod_ids[1],
                                   'product_uom_qty': 2}),
                          ]
        })
        so_model.action_confirm([order_id])
```

The host on which run the load is defined in locust.conf file, either in your project folder or home folder, as explained in Locust doc:
https://docs.locust.io/en/stable/configuration.html#configuration-file

```
host=localhost
users = 100
spawn-rate = 10
```

then you run your locust tests the usual way:

```
locust -f my_file.py
```

# Generic test

This version is shipped with a generic TaskSet task, OdooTaskSet, and a TaskSet which randomly click on menu items,
OdooGenericTaskSet.  To use this version, create this simple test file:

```
from OdooLocust.OdooLocustUser import OdooLocustUser
from locust import task, between
from OdooLocust import OdooTaskSet


class GenericTest(OdooLocustUser):
    wait_time = between(0.1, 1)
    database = "my_db"
    login = "admin"
    password = "secure_password"
    port = 443
    protocol = "jsonrpc+ssl"

    @task(10)
    def read_partners(self):
        cust_model = self.client.env['res.partner']
        cust_ids = cust_model.search([], limit=80)
        prtns = cust_model.read(cust_ids, ['name'])

    tasks = [OdooTaskSet.OdooGenericTaskSet]
```

and you finally run your locust tests the usual way:

```
locust -f my_file.py
```
