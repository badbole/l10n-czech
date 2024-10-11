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


import datetime
from collections import defaultdict

import requests
from odoo import fields, models


class ResCurrencyRateProviderKB(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("KB", "Komerční banka")],
        ondelete={"KB": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "KB":
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # https://www.csob.cz/portal/lide/kurzovni-listek-old/-/date/kurzy.txt
        return [
            "ATS",
            "AUD",
            "BEF",
            "BGN",
            "CAD",
            "CHF",
            "CNY",
            "DEM",
            "DKK",
            "ESP",
            "EUR",
            "FIM",
            "FRF",
            "GBP",
            "GRD",
            "HUF",
            "IEP",
            "ITL",
            "JPY",
            "LUF",
            "NLG",
            "NOK",
            "PLN",
            "PTE",
            "RON",
            "RUB",
            "SEK",
            "SKK",
            "TRY",
            "USD",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "KB":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover

        if (
            datetime.datetime.now().date() - datetime.timedelta(days=1095)
        ) > date_from:
            date_from = (
                datetime.datetime.now() - datetime.timedelta(days=1095)
            ).date()
        validity_date_time = datetime.datetime(
            date_from.year,
            date_from.month,
            date_from.day,
            12,
            0,
            0,
            0,
            tzinfo=datetime.timezone.utc,
        ).isoformat()
        content = defaultdict(dict)
        while (
            datetime.datetime.fromisoformat(validity_date_time).date()
            <= date_to
        ):
            url = "https://api.kb.cz/open/api/exchange-rates/v1/exchange-rates"
            headers = {
                "x-api-key": "Bearer 199fabd0-9fee-357f-be18-b7493414222a"
            }
            params = {"validityDateTime": validity_date_time}
            response = requests.get(url, headers=headers, params=params)
            data = response.json()
            for row in data:
                if row["currency"] in currencies:
                    content[
                        datetime.datetime.fromisoformat(
                            row["validityDateTime"]
                        ).date()
                    ][row["currency"]] = 1.0 / float(
                        row["nonCashSell"] / float(row["currencyUnit"])
                    )
            validity_date_time = (
                datetime.datetime.fromisoformat(validity_date_time)
                + datetime.timedelta(days=1)
            ).isoformat()
        return content
