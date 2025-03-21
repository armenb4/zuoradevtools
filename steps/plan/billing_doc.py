from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR
from common.util.billing_doc.build_util import BillingDocumentTemplateBuilder


def generate_all_html_template_payloads(environment: str):
    logger.info(
        f"Generating all HTML template payloads to upload to Zuora {environment.upper()}"
    )
    output_dir = ZUORA_VCS_DIR.joinpath("temp/billing_documents")
    output_dir.mkdir(exist_ok=True, parents=True)

    billing_documents_dir = ZUORA_VCS_DIR.joinpath("billing_documents")
    request_form_files = list(billing_documents_dir.glob("**/*_form.json"))
    template_names = []
    for file in request_form_files:
        template_names.append(file.stem.replace("_form", ""))

    for template_name in template_names:
        try:
            logger.info(f"Generating HTML template payload for {template_name}")
            BillingDocumentTemplateBuilder.build_request_payload(
                template_name, output_dir
            )
            logger.info(
                f"✅ Successfully generated HTML template payload for {template_name}"
            )
        except Exception as e:
            logger.error(
                f"❌ FAILED to generate HTML template payload for {template_name}"
            )
            logger.error(f"❌ {e}")
