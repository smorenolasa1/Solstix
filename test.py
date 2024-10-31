from langchain_community.llms import Replicate  
from flask import Flask, request
import os
import requests
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from pdfdesign import generate_pdf
from dotenv import load_dotenv

load_dotenv()

class WhatsAppClient:
    API_URL = "https://graph.facebook.com/v18.0/"
    WHATSAPP_API_TOKEN = os.getenv("WHATSAPP_API_TOKEN")
    WHATSAPP_CLOUD_NUMBER_ID = os.getenv("WHATSAPP_CLOUD_NUMBER_ID")  
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.WHATSAPP_API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.API_URL = f"{self.API_URL}{self.WHATSAPP_CLOUD_NUMBER_ID}/messages"

    def send_text_message(self, message, phone_number):
        payload = {
            "messaging_product": 'whatsapp',
            "to": phone_number,
            "type": "text",
            "text": {
                "preview_url": False,
                "body": message
            }
        }
        # Use self.API_URL directly since it already includes /messages
        response = requests.post(self.API_URL, json=payload, headers=self.headers)
        if response.status_code != 200:
            print("Failed to send message:", response.text)
            return response.status_code
        return response.status_code

os.environ["REPLICATE_API_TOKEN"] = os.getenv("REPLICATE_API_TOKEN")
llama2_13b_chat = "meta/llama-2-13b-chat:f4e2de70d66816a838a89eeeb621910adffb0dd0baba3976c96980970978018d"

llm = Replicate(
    model=llama2_13b_chat,
    model_kwargs={"temperature": 0.01, "top_p": 1, "max_new_tokens":500}
)
client = WhatsAppClient()
app = Flask(__name__)

# Global dictionaries to keep track of user interactions, states, and responses
user_interactions = {}
user_states = {}
user_responses = {}
conversation_history = {}
# Sample question dictionary
questions_dict = {
    'start': "¡Bienvenido! Vamos a empezar con tu historial médico. ¿Cuál es tu nombre completo?",
    'dni': "¿Cuál es tu DNI?",
    'edad': "¿Cuál es tu edad?",
    'operaciones': "¿Te han operado alguna vez? Si es así, ¿qué tipo de operación fue y cuándo la realizaste?",
    'alergias': "¿Tienes alguna alergia? Si es así, ¿a qué eres alérgico?",
    'enfermedades_cronicas': "¿Padeces alguna enfermedad crónica? Si es así, ¿cuál o cuáles?",
    'medicamentos_actuales': "¿Estás tomando algún medicamento actualmente? Si es así, ¿cuáles?",
    'finish': "Thank you for your responses! Your review is complete."
}

def get_next_question(current_state):
    state_order = ['start', 'dni', 'edad', 'operaciones', 'alergias', 'enfermedades_cronicas', 
                   'medicamentos_actuales', 'finish']
    try:
        return state_order[state_order.index(current_state) + 1]
    except (ValueError, IndexError):
        return None

@app.route('/msgrcvd', methods=['POST', 'GET'])
def msgrcvd():
    message = request.args.get('message')
    if not message:
        return "Message is required.", 400

    destination_number = request.args.get('destination_number', "") #add number
    return handle_interaction(message, destination_number)

def handle_interaction(user_message, destination_number):
    if destination_number not in user_states or user_states[destination_number] != 'finish':
        return process_questionnaire(user_message, destination_number)
    return handle_llama_interaction(user_message, destination_number)

def process_questionnaire(user_message, destination_number):
    if user_message.endswith("?"):
        user_interactions[destination_number] = 'question'
        return handle_llama_interaction(user_message, destination_number)
    elif user_message.lower() == 'solved' and user_interactions.get(destination_number) == 'question':
        user_interactions.pop(destination_number)
        if destination_number in user_states:
            current_state = user_states[destination_number]
            if current_state:
                question = questions_dict.get(current_state, "Could not find the previous question.")
                return ask_question((current_state, question), destination_number)
            else:
                return "There seems to be an error. Please start your report by typing 'start report'."

    if user_message.lower() == 'start report':
        user_states[destination_number] = 'start'
        next_question_key = get_next_question(user_states[destination_number])
        return ask_question((next_question_key, questions_dict[next_question_key]), destination_number)

    if destination_number in user_states:
        current_state = user_states[destination_number]
        next_state = get_next_question(current_state)
        if next_state:
            return process_answer(user_message, current_state, destination_number)
        else:
            user_states.pop(destination_number)
            return "Report completed."

    return "Please start your report by typing 'start report'."

def handle_llama_interaction(user_message, destination_number):
    script = ("You are a helpful assistant, "
              "designed to assist users with questions about their report. "
              "Ensure you use the context of the report to provide accurate answers."
              "Output the answer in an organized list format.")
    
    # Retrieve the existing conversation history
    history = conversation_history.get(destination_number, [])

    # Add the system message and the user's latest message to the history
    if not history:
        formatted_responses = format_responses(user_responses.get(destination_number, {}))
        history.append({"role": "system", "content": script})
        history.append({"role": "system", "content": formatted_responses})
    history.append({"role": "user", "content": user_message})
    
    try:
        # Invoke the LLaMA model to get a response, passing 'input' as expected
        response = llm.invoke(input=history)
        # Assuming 'response' contains the response text directly
        assistant_message = response if isinstance(response, str) else "Sorry, I couldn't generate a response."

        # Update the conversation history with the assistant's response
        history.append({"role": "assistant", "content": assistant_message})
        conversation_history[destination_number] = history

        # Send the LLaMA's reply back to the user
        response_status = client.send_text_message(assistant_message, destination_number)
        if response_status != 200:
            print(f"Failed to send WhatsApp message: HTTP {response_status}")
            return f"Failed to send WhatsApp message: HTTP {response_status}", 500
    except Exception as e:
        print(f"Error processing message with LLaMA: {str(e)}")
        return f"Error processing message with LLaMA: {str(e)}", 500

    return assistant_message

def format_responses(responses):
    formatted_responses = (
        f"start: {responses.get('start', 'Not provided')}\n"
        f"dni: {responses.get('dni', 'Not provided')}\n"
        f"edad: {responses.get('edad', 'Not provided')}\n"
        f"operaciones: {responses.get('operaciones', 'Not provided')}\n"
        f"alergias: {responses.get('alergias', 'Not provided')}\n"
        f"enfermedades_cronicas: {responses.get('enfermedades_cronicas', 'Not provided')}\n"
        f"medicamentos_actuales: {responses.get('medicamentos_actuales', 'Not provided')}\n"
        f"finish: {responses.get('finish', 'Not provided')}\n"
    )
    return formatted_responses

def ask_question(question, destination_number):
    response_status = client.send_text_message(question[1], destination_number)
    if response_status != 200:
        print(f"Failed to send WhatsApp message: HTTP {response_status}")
        return f"Failed to send WhatsApp message: HTTP {response_status}", 500

    user_states[destination_number] = question[0]
    return "Asking question: " + question[1]

def prepare_summary(destination_number):
    responses = user_responses.get(destination_number, {})
    formatted_responses = {
        'start': responses.get('start', 'Not provided'),
        'dni': responses.get('dni', 'Not provided'),
        'edad': responses.get('edad', 'Not provided'),
        'operaciones': responses.get('operaciones', 'Not provided'),
        'alergias': responses.get('alergias', 'Not provided'),
        'enfermedades_cronicas': responses.get('enfermedades_cronicas', 'Not provided'),
        'medicamentos_actuales': responses.get('medicamentos_actuales', 'Not provided'),
        'finish': responses.get('finish', 'Not provided'),
    }

    fileName = f"Medical_Report_{destination_number}.pdf"
    documentTitle = "Medical Report Summary"
    generate_pdf(formatted_responses, fileName, documentTitle)

    notification_message = "Your report summary has been created."
    client.send_text_message(notification_message, destination_number)

    return "Summary PDF generated."

def process_answer(answer, current_state, destination_number):
    if destination_number not in user_responses:
        user_responses[destination_number] = {}
    user_responses[destination_number][current_state] = answer

    next_question = get_next_question(current_state)
    if next_question:
        user_states[destination_number] = next_question
        if next_question == 'finish':
            final_message = questions_dict[next_question]
            client.send_text_message(final_message, destination_number)
            summary = prepare_summary(destination_number)
            user_states[destination_number] = 'finish'
            return summary
        else:
            return ask_question((next_question, questions_dict[next_question]), destination_number)
    else:
        user_states.pop(destination_number, None)
        return "Unexpected end of conversation."

if __name__ == '__main__':
    app.run(debug=True)
