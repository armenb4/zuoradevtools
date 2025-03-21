import json
import base64
from typing import List
from pathlib import Path

from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR

HTML_TEMPLATES_DIR = ZUORA_VCS_DIR.joinpath("billing_documents")


class BillingDocumentTemplateBuilder:
    @staticmethod
    def build_json_from_source_code(template_name: str, output_dir: Path = None):
        logger.info(f"Building JSON from source code for  {template_name}")
        billing_doc_dir = HTML_TEMPLATES_DIR.joinpath(template_name)
        billing_doc_json = billing_doc_dir.joinpath(f"{template_name}.json")

        with open(billing_doc_json) as fs:
            billing_doc_content: dict = json.load(fs)

        design: dict = billing_doc_content["design"]
        body: dict = design["body"]
        rows: List[dict] = body["rows"]

        main_html_content_file = billing_doc_dir.joinpath("main_content.html")
        main_html = main_html_content_file.read_text()

        for row in rows:
            columns = row["columns"]
            for column in columns:
                contents = column["contents"]

                for content in contents:
                    content_type = content["type"]
                    if content_type not in ("customx"):
                        continue

                    slug = content["slug"]
                    if slug not in ("reactHtml"):
                        continue

                    values = content["values"]
                    meta = values["_meta"]
                    html_id = meta["htmlID"]

                    source_file = billing_doc_dir.joinpath(f"{html_id}.html")
                    source_content = source_file.read_text()
                    values["html"] = source_content

                    main_html = main_html.replace(
                        f"placeholder-{html_id}", f"\n{source_content}\n"
                    )

        billing_doc_content["htmlContent"] = main_html

        if output_dir:
            new_billing_doc_json = output_dir.joinpath(f"{template_name}_new.json")
            with open(new_billing_doc_json, "w") as fs:
                json.dump(billing_doc_content, fs, indent=2)

        return billing_doc_content

    @staticmethod
    def build_request_payload(template_name: str, output_dir: Path) -> dict:
        template_json = BillingDocumentTemplateBuilder.build_json_from_source_code(
            template_name
        )
        template_json_str = json.dumps(template_json)
        base64_encoded_template_content = base64.b64encode(
            template_json_str.encode()
        ).decode()

        billing_doc_dir = HTML_TEMPLATES_DIR.joinpath(template_name)
        request_form_file = billing_doc_dir.joinpath(f"{template_name}_form.json")

        with open(request_form_file) as fs:
            request_form: dict = json.load(fs)

        request_form_file_new = output_dir.joinpath(f"{template_name}_form_new.json")

        request_form["base64EncodedTemplateFileContent"] = (
            base64_encoded_template_content
        )

        with open(request_form_file_new, "w") as fs:
            json.dump(request_form, fs, indent=2)

        return request_form
