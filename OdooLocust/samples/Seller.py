from locust import task, between
from OdooLocust.OdooLocustUser import OdooLocustUser


class Seller(OdooLocustUser):
    wait_time = between(0.1, 10)
    database = "devel"
    login = "admin"
    password = "admin"
    port = 8069
    protocol = "jsonrpc"
    
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
