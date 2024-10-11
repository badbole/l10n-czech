###################################################################################
#
#    Copyright (c) 2022 Data Dance s.r.o.
#
#    Data Dance Proprietary License v1.0
#
#    This software and associated files (the "Software") may only be used
#    (executed, modified, executed after modifications) if you have
#    purchased a valid license from Data Dance s.r.o.
#
#    The above permissions are granted for a single database per purchased
#    license. Furthermore, with a valid license it is permitted to use the
#    software on other databases as long as the usage is limited to a testing
#    or development environment.
#
#    You may develop modules based on the Software or that use the Software
#    as a library (typically by depending on it, importing it and using its
#    resources), but without copying any source code or material from the
#    Software. You may distribute those modules under the license of your
#    choice, provided that this license is compatible with the terms of the
#    Data Dance Proprietary License (For example: LGPL, MIT, or proprietary
#    licenses similar to this one).
#
#    It is forbidden to publish, distribute, sublicense, or sell copies of
#    the Software or modified copies of the Software.
#
#    The above copyright notice and this permission notice must be included
#    in all copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
#    OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL
#    THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#    FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#    DEALINGS IN THE SOFTWARE.
#
###################################################################################


import csv
from collections import defaultdict
from datetime import datetime
from urllib.request import urlopen

from odoo import fields, models


class ResCurrencyRateProviderCSOB(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("CSOB", "ČSOB CZ")],
        ondelete={"CSOB": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "CSOB":
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # https://www.csob.cz/portal/lide/kurzovni-listek-old/-/date/kurzy.txt
        return [
            "AUD",
            "CNY",
            "DKK",
            "EUR",
            "JPY",
            "CAD",
            "HUF",
            "NOK",
            "PLN",
            "RON",
            "SEK",
            "CHF",
            "TRY",
            "USD",
            "GBP",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "CSOB":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover
        url = "https://www.csob.cz/portal/lide/kurzovni-listek-old/-/date/kurzy.txt"
        content = defaultdict(dict)
        with urlopen(url) as response:
            response = response.read().decode("utf-8").splitlines()
            date = datetime.strptime(
                response[0].split(" ")[0], "%Y-%m-%d"
            ).date()
            reader = csv.DictReader(response[3:], delimiter=";")
            for row in reader:
                if row["Měna"] in currencies:
                    if row["Nákup"] != "0,000":
                        content[date][row["Měna"]] = str(
                            1.0
                            / float(row["Prodej"].replace(",", "."))
                            / float(row["Množství"])
                        )
        return content