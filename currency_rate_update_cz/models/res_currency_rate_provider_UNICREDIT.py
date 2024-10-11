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


import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime

import requests
from odoo import fields, models


class ResCurrencyRateProviderUniCredit(models.Model):
    _inherit = "res.currency.rate.provider"

    service = fields.Selection(
        selection_add=[("UniCredit", "UniCredit CZ")],
        ondelete={"UniCredit": "set default"},
    )

    def _get_supported_currencies(self):
        self.ensure_one()
        if self.service != "UniCredit":
            return super()._get_supported_currencies()  # pragma: no cover

        # List of currencies obrained from:
        # https://www.unicreditbank.cz/cs/exchange_rates_xml.exportxml.html
        return [
            "AUD",
            "BAM",
            "BGN",
            "CAD",
            "CHF",
            "DKK",
            "EUR",
            "GBP",
            "HKD",
            "HUF",
            "JPY",
            "NOK",
            "NZD",
            "PLN",
            "RON",
            "SEK",
            "SGD",
            "TRY",
            "USD",
        ]

    def _obtain_rates(self, base_currency, currencies, date_from, date_to):
        self.ensure_one()
        if self.service != "UniCredit":
            return super()._obtain_rates(
                base_currency, currencies, date_from, date_to
            )  # pragma: no cover
        content = defaultdict(dict)
        url = (
            "https://www.unicreditbank.cz/cs/exchange_rates_xml.exportxml.html"
        )
        headers = {
            "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,/;q=0.8",
            "accept-language": "en-US,en;q=0.5",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "referer": "https://www.unicreditbank.cz/cs/obcane/kurzovni-listek.html",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36",
        }
        response = requests.get(url, headers=headers)
        root = ET.fromstring(response.content)
        exchange_rate = root.find(
            'exchange_rate[@type="XML_RATE_TYPE_UCB_SALE_DEVIZA"]'
        )
        date = datetime.strptime(
            exchange_rate.attrib["valid_from"], "%d.%m.%Y"
        ).date()
        for row in exchange_rate.findall("currency"):
            if row.attrib["name"] in currencies:
                content[date][row.attrib["name"]] = str(
                    1.0
                    / float(row.attrib["rate"])
                    / float(row.attrib["quota"])
                )
        return content
