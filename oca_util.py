import os
import json
import hashlib
import http.client
import requests
import sseclient
import urllib3
import io
from dotenv import load_dotenv, set_key
from authlib.integrations.requests_client import OAuth2Session
from logger import get_logger

# Load environment variables
load_dotenv()
logger = get_logger()

def get_access_token():
    # Load client credentials from environment variables
    CLIENT_ID = os.getenv('OCA_CLIENT_ID')
    CLIENT_SECRET = os.getenv('OCA_CLIENT_SECRET')
    TOKEN_URL = os.getenv('OCA_TOKEN_URL')
    SCOPE = os.getenv('OCA_SCOPE')

    # Initialize OAuth2 session
    client = OAuth2Session(CLIENT_ID, CLIENT_SECRET, scope=SCOPE)

    token = client.fetch_token(
        TOKEN_URL,
        grant_type='client_credentials',
        auth=(CLIENT_ID, CLIENT_SECRET)
    )
    return token

def get_oca_response(prompt: str, oca_model: str, user: str) -> str:
    bearer_token = os.getenv("OCA_BEARER_TOKEN")
    try:
        return make_request(prompt, oca_model, user, bearer_token)
    except Exception as e:
        error_message = str(e)
        # Check if the error is related to token expiration
        if "token expired" in error_message.lower() or "unauthorized" in error_message.lower() or "401" in error_message:
            logger.debug("Token expired. Refreshing token...")
            try:
                # Get a new token
                try:
                    token_data = get_access_token()
                    new_token = token_data.get('access_token')
                except Exception as refresh_error:
                    logger.error(f"Error refreshing token: {str(refresh_error)}", exc_info=True)
                    raise Exception(f"Failed to refresh token: {str(refresh_error)}")

                if new_token:
                    logger.debug("Token refreshed successfully: %s", new_token)
                    # Retry the request with the new token
                    return make_request(prompt, oca_model, user, new_token)
                else:
                    raise Exception("Failed to get a new token")
            except Exception as oca_error:
                logger.error(f"Error Get OCA response: {str(oca_error)}", exc_info=True)
                raise Exception(f"Failed to call OCA: {str(oca_error)}")
        else:
            # If the error is not related to token expiration, re-raise it
            raise

def handle_streaming_events(client, request_id=None):
    full_response = ""
    event_count = 0
    last_event_raw = None
    try:
        for event in client.events():
            try:
                logger.info(event.data)
                event_data = json.loads(event.data)
            except Exception as e:
                logger.warning(f"Skipping non-JSON event: {event.data}")
                continue
            event_count += 1
            last_event_raw = event.data
            choices = event_data.get("choices", [])
            if choices:
                delta = choices[0].get("delta", {})
                content = delta.get("content")
                if content:
                    full_response += str(content)
        logger.info(
            "Response received from OCA. request_id=%s chunks=%s",
            request_id or "unknown",
            event_count,
        )
        return full_response
    except (requests.exceptions.ChunkedEncodingError, 
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            http.client.IncompleteRead,
            urllib3.exceptions.ProtocolError,
            Exception) as err:
        logger.error(
            "Error from OCA streaming client. request_id=%s chunks=%s last_chunk=%s err=%s",
            request_id or "unknown",
            event_count,
            last_event_raw,
            err,
            exc_info=True,
        )
        return "Something went wrong while processing the response from OCA. Please try again later."


def make_request(prompt: str, oca_model: str, user: str, token: str = None) -> str:

    url = os.getenv('OCA_URL_V2')
    client_name = os.getenv('OCA_CLIENT_NAME')
    model = oca_model or os.getenv('OCA_DEFAULT_MODEL')
    bearer_token = token or os.getenv('OCA_BEARER_TOKEN')
    original_principal = hashlib.sha3_256(user.encode('utf-8')).hexdigest()

    headers = {
        'Content-Type': 'application/json',
        'Accept': 'text/event-stream',
        'client': client_name,
        'original-principal': original_principal,
        'Authorization': f'Bearer {bearer_token}'
    }

    data = {
        "model": "oca/gpt-4.1",
        "messages": [
            {
                "role": "user",
                "content": prompt
            }
        ]
    }

    logger.debug("Making streaming request to OCA API")
    logger.debug(url)
    with requests.Session() as session:
        response = session.post(
            url,
            stream=True,
            headers=headers,
            json=data,
            timeout=(
                int(os.getenv("OCA_CONNECT_TIMEOUT", "10")),
                int(os.getenv("OCA_READ_TIMEOUT", "300")),
            ),
        )
        request_id = (
            response.headers.get("x-request-id")
            or response.headers.get("request-id")
            or response.headers.get("x-trace-id")
        )
        logger.info(
            "OCA Response: %s request_id=%s",
            response.status_code,
            request_id or "unknown",
        )
        response.raw.decode_content = True
        client = sseclient.SSEClient(response.raw)
        # logger.info("client", client)

    if response.status_code in [401, 403]:
        logger.error("Error: Unauthorized, Token Expired")
        raise Exception("Unauthorized : Token expired")

    response_value = handle_streaming_events(client, request_id=request_id)
    logger.debug(
        "Completed streaming request. request_id=%s response_length=%s",
        request_id or "unknown",
        len(response_value),
    )
    return response_value


if __name__ == "__main__":
    token_data = get_access_token()
    logger.debug("Access Token: %s", token_data)
