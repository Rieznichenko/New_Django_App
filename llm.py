import logging
import time
import os
import google.generativeai as genai


def check_thread_status(client, thread_id, run_id):
    """Check the status of the conversation thread"""
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
            time.sleep(3)


def chat_functionality_gemini(user_input, message, api_key, assistant_id):
    """Perform chat functionality using gemini API."""
    genai.configure(api_key=api_key)

    model = genai.GenerativeModel('gemini-pro')

    prompt = user_input
    response = model.generate_content(prompt)

    return response.text

def chat_functionality(OPENAI_CLIENT, message, user_input, thread_id, assitant_id):
    """Perform chat functionality using OpenAI API."""
    OPENAI_CLIENT.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=user_input
    )

    # Run the conversation thread with the assistant
    run = OPENAI_CLIENT.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assitant_id,
    )

    # Check the status of the conversation thread
    check_thread_status(OPENAI_CLIENT, thread_id, run.id)

    # Retrieve messages from the conversation thread
    messages = OPENAI_CLIENT.beta.threads.messages.list(thread_id=thread_id)

    # Extract user and assistant messages
    user_message = messages.data[1].content[0].text.value
    assistant_message = messages.data[0].content[0].text.value
    return assistant_message