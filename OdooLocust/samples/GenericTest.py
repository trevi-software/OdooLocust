from OdooLocust.OdooLocustUser import OdooLocustUser
from locust import task, between
from OdooLocust import OdooTaskSet


class GenericTest(OdooLocustUser):
    wait_time = between(0.1, 1)
    database = "devel"
    login = "admin"
    password = "admin"
    port = 8069
    protocol = "jsonrpc"

    @task(10)
    def read_partners(self):
        cust_model = self.client.env['res.partner']
        cust_ids = cust_model.search([], limit=80)
        prtns = cust_model.read(cust_ids, ['name'])

    tasks = [OdooTaskSet.OdooGenericTaskSet]
