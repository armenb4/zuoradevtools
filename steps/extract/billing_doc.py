from common.lib.logger import logger
from common.app.zuora.validator import validate_environment
from common.app.zuora.api import ZuoraAPI
from common.util.billing_doc.util import BillingDocumentTemplateUtil
from common.util.billing_doc.dump_util import BillingDocumentTemplateParser

BILLING_DOCUMENT_TYPES = [
    "invoice",
    "credit-memo",
    "debit-memo",
]


def export_all_billing_document_templates(environment: str):
    logger.info("Exporting all billing document templates")
    logger.info("Input validation")
    validate_environment(environment)

    billing_documents = BillingDocumentTemplateUtil.list_all_billing_document_templates(
        environment
    )

    logger.info(f"Zuora environment: {environment}")
    zuora_api = ZuoraAPI(environment)

    for document_type, documents in billing_documents.items():
        for document in documents:
            id = document["id"]
            template_name = document["name"]

            url = f"settings/{document_type}-templates/{id}"
            response = zuora_api.get(path=url)

            if response.status_code == 200:
                BillingDocumentTemplateParser.extract_json_from_api_response(response)
                BillingDocumentTemplateParser.extract_source_code(template_name)

            else:
                logger.error(f"❌ Could not export billing document {url}")
                logger.error(response.text)
