from oca_util import get_oca_response
from model import *
from logger import get_logger
import json
import time

logger=get_logger()

def get_llm_response(prompt, model, user):
    # logger.debug(f"Prompt: {prompt}")
    if model in model_map and model_map[model].get("service") == "oca":
        response = get_oca_response(prompt, model_map[model]["model_id"], user)
    # else:
    #     response =get_openai_response(prompt)
    # logger.debug(f"Response: {response}")
    return response