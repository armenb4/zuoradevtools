import json
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.app.zuora.api import ZuoraAPI
from common.util.billing_doc.util import BillingDocumentTemplateUtil


VALID_ENVIRONMENTS = ("dev", "qa", "uat", "prod")


def deploy_all_billing_document_templates(environment: str):
    logger.info(
        f"Deploying all billing document templates to Zuora {environment.upper()}"
    )
    billing_documents = BillingDocumentTemplateUtil.list_all_billing_document_templates(
        environment
    )

    logger.info(f"Zuora environment: {environment}")
    zuora_api = ZuoraAPI(environment)

    payloads_dir = ZUORA_VCS_DIR.joinpath("temp", "billing_documents")
    templates_deployed = []
    for document_type, documents in billing_documents.items():
        for document in documents:
            id = document["id"]
            template_name = document["name"]

            url = f"settings/{document_type}-templates/{id}"

            payload_file = payloads_dir.joinpath(f"{template_name}_form_new.json")
            if not payload_file.exists():
                logger.info(
                    f"No deployment file found for {template_name}. Skipping this deployment."
                )
                continue

            with open(payload_file) as fs:
                payload = json.load(fs)

            response = zuora_api.put(path=url, payload=payload)
            if response.status_code == 200:
                logger.info(f"Successfully deployed template {template_name}")
            else:
                logger.error(f"❌ Could not update billing document {url}")
                logger.error(response.text)

            templates_deployed.append(template_name)

    eligible_files = list(payloads_dir.glob("*.json"))
    eligible_template_names = [
        filepath.stem.replace("_form_new", "") for filepath in eligible_files
    ]
    not_deployed = [
        template_name
        for template_name in eligible_template_names
        if template_name not in templates_deployed
    ]

    if not_deployed:
        logger.info("❌ Some billing document templates have not been deployed")
        logger.info(not_deployed)
        # with open(payload_file) as fs:
        #     payload: dict = json.load(fs)

        # document_type = payload.pop("document_type")
        # url = f"settings/{document_type}-templates"
        # response = zuora_api.post(path=url, payload=payload)
        # if response.status_code == 200:
        #     logger.info(f"Successfully deployed template {template_name}")
        # else:
        #     logger.error(f"❌ Could not export billing document {url}")
        #     logger.error(response.text)
        # # TODO: add POST command
        # # POST https://rest.zuora.com/settings/invoice-templates
        # {
        #     "name": "My new invoice template",
        #     "defaultTemplate": false,
        #     # "suppressZeroValueLine": false,
        #     # "templateFileName": "Allbrighter - Invoice  Template - 2019 v1.1USD.doc",
        #     "base64EncodedTemplateFileContent": "0M8R4KGxGuEAAAAAAAAAAAAAAAAAAAAAPgADAP...",
        #     "templateFormat": "WORD",
        #     "templateCategory": "New"
        # }
    else:
        logger.info("✅ Successfully deployed all billing document templates")
