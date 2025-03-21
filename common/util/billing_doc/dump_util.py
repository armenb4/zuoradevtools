import json
import base64
import shutil
from pathlib import Path
from bs4 import BeautifulSoup
from requests import Response
from common.lib.logger import logger
from common.config.config import ZUORA_VCS_DIR

HTML_TEMPLATES_DIR = ZUORA_VCS_DIR.joinpath("billing_documents")


class BillingDocumentTemplateParser:
    @staticmethod
    def extract_json_from_api_response(response: Response) -> Path:
        response_json: list[dict] = response.json()
        name = response_json["name"]
        output_dir = HTML_TEMPLATES_DIR.joinpath(name)

        output_file = output_dir.joinpath(f"{name}.json")
        try:
            logger.info(f"Trying to clean up directory: {output_dir}")
            shutil.rmtree(output_dir)
        except Exception:
            pass

        output_dir.mkdir(exist_ok=True, parents=True)

        content = response_json["base64EncodedTemplateFileContent"]
        decoded = base64.b64decode(content).decode()
        template_json: dict = json.loads(decoded)

        with open(output_file, "w") as fs:
            json.dump(template_json, fs, indent=2)

        response_json.pop("id")
        response_json.pop("updatedOn")
        response_json.pop("templateNumber")
        response_json.pop("templateFormat")
        response_json.pop("associatedToBillingAccount")
        response_json["base64EncodedTemplateFileContent"] = "Placeholder"
        response_file = output_dir.joinpath(f"{name}_form.json")

        with open(response_file, "w") as fs:
            json.dump(response_json, fs, indent=2)

        return output_file

    @staticmethod
    def extract_source_code(template_name: str):
        billing_doc_dir = HTML_TEMPLATES_DIR.joinpath(template_name)
        billing_doc_json = billing_doc_dir.joinpath(f"{template_name}.json")
        logger.info(f"Extracting HTML source code from {billing_doc_json}")

        with open(billing_doc_json) as fs:
            billing_doc_content = json.load(fs)

        design: dict = billing_doc_content["design"]
        body: dict = design["body"]
        rows: list[dict] = body["rows"]

        html_ids = []
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

                    logger.debug(f"{content_type}       {slug}")
                    values = content["values"]
                    meta = values["_meta"]
                    html_id = meta["htmlID"]
                    html = values["html"]
                    html_ids.append(html_id)
                    values["html"] = "Placeholder"

                    output_file = billing_doc_dir.joinpath(f"{html_id}.html")
                    logger.info(f"Writing {output_file}")
                    output_file.write_text(html, encoding="utf-8")

        main_html_content_file = billing_doc_dir.joinpath("main_content.html")
        main_html = billing_doc_content["htmlContent"]

        soup = BeautifulSoup(main_html, "html.parser")
        for html_id in html_ids:
            element = soup.find(id=html_id)
            for content in element.contents:
                content.replace_with("")
            element.append(f"placeholder-{html_id}")

        billing_doc_content["htmlContent"] = "Placeholder"
        with open(billing_doc_json, "w") as fs:
            json.dump(billing_doc_content, fs, indent=2)

        logger.info(f"Writing {main_html_content_file}")
        main_html_content_file.write_text(
            soup.prettify(formatter="html"), encoding="utf-8"
        )
