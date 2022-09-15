# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (C) Stephane Wirtel
# Copyright (C) 2011 Nicolas Vanhoren
# Copyright (C) 2011 OpenERP s.a. (<http://openerp.com>).
# Copyright (C) 2017 Nicolas Seinlet
# Copyright (C) 2022 Michael Telahun Makonnen (<mtm@trevi.et>)
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation
# and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
##############################################################################
from odoorpc import ODOO, error
import time
import sys

from locust import HttpUser, events


def json(self, url, params):
    start_time = time.time()
    call_name = url
    if call_name == "/jsonrpc":
        call_name = f"{params['args'][3]}:{params['args'][4]}"

    try:
        data = self._connector.proxy_json(url, params)
        if data.get('error'):
            raise error.RPCError(
                data['error']['data']['message'], data['error']
            )
    except Exception as e:
        total_time = int((time.time() - start_time) * 1000)
        events.request_failure.fire(request_type="Odoo JsonRPC", name=call_name, response_time=total_time, response_length=0, exception=e)
        raise e
    total_time = int((time.time() - start_time) * 1000)
    events.request_success.fire(request_type="Odoo JsonRPC", name=call_name, response_time=total_time, response_length=sys.getsizeof(data))
    return data


ODOO.json = json


class OdooLocustUser(HttpUser):
    abstract = True
    port = 8069
    database = "demo"
    login = "admin"
    password = "admin"
    protocol = "jsonrpc"
    user_id = -1
    odoo_version = 0

    def on_start(self):
        # Prepare the connection to the server
        odoo = ODOO(self.host, port=self.port, protocol=self.protocol)

        # Login
        odoo.login(self.database, self.login, self.password)

        # Current user
        self.user_id = odoo.env.user.id

        self.client = odoo
        self.odoo_version = odoo.version
