from flask import Flask, jsonify, request, Response
from dotenv import load_dotenv
from logger import get_logger
from llm_util import get_llm_response

import os
import re
import json
from collections import OrderedDict
load_dotenv()


app = Flask(__name__)

def read_file_block(path, block_name):
    try:
        with open(path, "r") as f:
            content = f.read()
        return f"--- {block_name}: {path} ---\n{content}\n"
    except Exception as e:
        return f"--- {block_name}: {path} [ERROR: {e}] ---\n"

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Flask API service!"})

@app.route('/api-test')
def api_test():
    """Serve the API testing interface."""
    from flask import render_template
    return render_template('api-test.html')

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

@app.route("/json-to-xml", methods=["POST"])
def json_to_xml():
    import json, re
    input_file = "constants/INPUT_CHANGE_PO_OUT.JSON"
    output_file = "constants/OUTPUT_CHANGE_PO_OUT.xml"
    xsl_file = "constants/XSL_CHANGE_PO_OUT.xml"
    prompt_jsontoxml = "constants/Prompt_JSONtoXML.txt"
    prompt_content = read_file_block(prompt_jsontoxml, "Prompt Content")
    generated_prompt = (
        prompt_content + "\n\n\n" +
        read_file_block(input_file, "Input File") + "\n" +
        read_file_block(output_file, "Output File") + "\n" +
        read_file_block(xsl_file, "XSL Stylesheet")
    )
    oca_response = get_llm_response(generated_prompt, "gpt", "yash.s.sahu@oracle.com")

    mapping_json = None
    mapping_javascript = None

    # Extract JSON code block
    json_match = re.search(r"```json\s*\n(.*?})\s*```", oca_response, re.DOTALL)
    mapping_json = None
    mapping_json_ordered = None
    mapping_json_raw = None
    if json_match:
        json_str = json_match.group(1)
        mapping_json_raw = json_str
        try:
            mapping_json_ordered = json.loads(json_str, object_pairs_hook=OrderedDict)
            mapping_json = mapping_json_ordered
        except Exception:
            mapping_json = None

    # Extract JS code block
    js_match = re.search(r"```javascript\s*\n([\s\S]*?)```", oca_response, re.DOTALL|re.IGNORECASE)
    if js_match:
        mapping_javascript = js_match.group(1).strip()

    # Write to files in results/ if mappings were found
    import os
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    if mapping_json_ordered is not None:
        with open(os.path.join(results_dir, "mapping.json"), "w", encoding="utf-8") as f_json:
            json.dump(mapping_json_ordered, f_json, ensure_ascii=False, indent=2)
    if mapping_javascript is not None:
        with open(os.path.join(results_dir, "mapping_functions.js"), "w", encoding="utf-8") as f_js:
            f_js.write(mapping_javascript)

    # Compose response ordering preserved for mapping_json
    result_ordered = OrderedDict()
    result_ordered["mapping_json"] = mapping_json_ordered
    result_ordered["mapping_javascript"] = mapping_javascript
    result_ordered["raw_mapping_json"] = mapping_json_raw
    result_ordered["raw_response"] = oca_response
    if mapping_json is None:
        result_ordered["error"] = "Could not extract or parse mapping JSON block."
    if mapping_javascript is None:
        result_ordered["error"] = result_ordered.get("error", "") + " Could not extract mapping JavaScript block."

    return Response(
        json.dumps(result_ordered, ensure_ascii=False, indent=2, sort_keys=False),
        mimetype="application/json"
    )

@app.route("/xml-to-json", methods=["POST"])
def xml_to_json():
    input_file = "constants/input.xml"
    output_file = "constants/output.json"
    xsl_file = "constants/xsl.xml"
    prompt_xmltojson = "constants/Prompt_XMLtoJSON.txt"
    prompt_content = read_file_block(prompt_xmltojson, "Prompt Content")
    generated_prompt = (
        prompt_content + "\n\n\n" +
        read_file_block(input_file, "Input File") + "\n" +
        read_file_block(output_file, "Output File") + "\n" +
        read_file_block(xsl_file, "XSL Stylesheet")
    )
    oca_response = get_llm_response(generated_prompt, "gpt", "yash.s.sahu@oracle.com")

    mapping_json = None
    mapping_javascript = None

    # Extract JSON code block
    json_match = re.search(r"```json\s*\n(.*?})\s*```", oca_response, re.DOTALL)
    mapping_json = None
    mapping_json_ordered = None
    mapping_json_raw = None
    if json_match:
        json_str = json_match.group(1)
        mapping_json_raw = json_str
        try:
            mapping_json_ordered = json.loads(json_str, object_pairs_hook=OrderedDict)
            mapping_json = mapping_json_ordered
        except Exception:
            mapping_json = None

    # Extract JS code block
    js_match = re.search(r"```javascript\s*\n([\s\S]*?)```", oca_response, re.DOTALL|re.IGNORECASE)
    if js_match:
        mapping_javascript = js_match.group(1).strip()

    # Write to files in results/ if mappings were found
    import os
    results_dir = "results"
    os.makedirs(results_dir, exist_ok=True)
    if mapping_json_ordered is not None:
        with open(os.path.join(results_dir, "mapping.json"), "w", encoding="utf-8") as f_json:
            json.dump(mapping_json_ordered, f_json, ensure_ascii=False, indent=2)
    if mapping_javascript is not None:
        with open(os.path.join(results_dir, "mapping_functions.js"), "w", encoding="utf-8") as f_js:
            f_js.write(mapping_javascript)

    # Compose response ordering preserved for mapping_json
    result_ordered = OrderedDict()
    result_ordered["mapping_json"] = mapping_json_ordered
    result_ordered["mapping_javascript"] = mapping_javascript
    result_ordered["raw_mapping_json"] = mapping_json_raw
    result_ordered["raw_response"] = oca_response
    if mapping_json is None:
        result_ordered["error"] = "Could not extract or parse mapping JSON block."
    if mapping_javascript is None:
        result_ordered["error"] = result_ordered.get("error", "") + " Could not extract mapping JavaScript block."

    return Response(
        json.dumps(result_ordered, ensure_ascii=False, indent=2, sort_keys=False),
        mimetype="application/json"
    )

if __name__ == "__main__":
    # For development purposes only; in production, use gunicorn or similar
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("PORT", "7003"))
    app.run(host="0.0.0.0", port=7003, debug=True)
