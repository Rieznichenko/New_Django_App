from django.views.decorators.csrf import csrf_exempt
import json
from django.http import JsonResponse, HttpResponse
import os
import openai
import time
import logging
from llm_bot.models import LLMCOnfig, LLMAgent


logging.basicConfig(
    format="[%(asctime)s] [%(filename)s:%(lineno)d] %(message)s", level=logging.INFO
)

VALID_PROVIDERS = ["gemini", "openai"]


def check_thread_status(client, thread_id, run_id):
    """
    Check the status of the conversation thread.

    Parameters:
        client (openai.Client): The OpenAI client instance.
        thread_id (str): The ID of the conversation thread.
        run_id (str): The ID of the conversation run.

    Returns:
        None
    """

    while True:
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id
        )

        if run.status == "completed":
            logging.info(f"Run is completed")
            break
        elif run.status == "expired":
            logging.info(f"Run is expired")
            break
        else:
            logging.info(f"OpenAI: Run is not yet completed. Waiting...")
            time.sleep(1)


def ajax_get_config(request):
    llm_config_id = request.GET.get('id', '')

    llm_config_instance = LLMCOnfig.objects.get(id=llm_config_id)

    llm_agents = LLMAgent.objects.filter(llm_config = llm_config_instance)

    result = list(llm_agents.values('id', 'agent_name'))
    return HttpResponse(json.dumps(result), content_type="application/json")