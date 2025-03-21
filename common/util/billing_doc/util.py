from typing import Dict, List

from common.lib.logger import logger
from common.app.zuora.api import ZuoraAPI
from common.app.zuora.validator import validate_environment


BILLING_DOCUMENT_TYPES = [
    "invoice",
    "credit-memo",
    "debit-memo",
]


class BillingDocumentTemplateUtil:
    @staticmethod
    def list_all_billing_document_templates(environment: str):
        logger.info("Input validation")
        validate_environment(environment)

        logger.info(f"Zuora environment: {environment}")
        zuora_api = ZuoraAPI(environment)

        billing_document_templates: Dict[str, List[dict]] = {}
        for billing_document_type in BILLING_DOCUMENT_TYPES:
            logger.info(
                f"Listing billing document templates for {billing_document_type}"
            )
            billing_document_templates[billing_document_type] = []

            url = f"settings/{billing_document_type}-templates"

            response = zuora_api.get(path=url)

            if response.status_code == 200:
                response_json: List[dict] = response.json()
                for item in response_json:
                    template_format = item.get("templateFormat")
                    associated_account = item.get("associatedToBillingAccount")

                    if template_format not in ("HTML"):
                        continue

                    if not associated_account:
                        continue

                    billing_document_templates[billing_document_type].append(item)

            else:
                logger.error("❌ Could not get billing document templates")
                logger.error(response.text)

        return billing_document_templates

    @staticmethod
    def get_id_by_template_name(template_name: str, environment: str) -> str:
        pass
