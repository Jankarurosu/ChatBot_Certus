from flask import Flask, render_template, request, jsonify
from kivy.clock import Clock
import json
from difflib import get_close_matches

app = Flask(__name__)


# Cargar las respuestas desde el json answers
def load_answers():
    try:
        with open("answers.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


# Guardar las respuestas en el json answers
def save_answers(answers):
    with open("answers.json", "w") as file:
        json.dump(answers, file, indent=2)


# Verificar si el mensaje es considerado "malo"
def is_bad_question(message):
    bad_keywords = ["muerte", "hackear"]
    for keyword in bad_keywords:
        if keyword in message.lower():
            return True
    return False


# Buscar una mejor coincidencia entre las preguntas para una respuesta más precisa
def get_best_match(message, responses):
    message = message.lower()
    if message == "quit":
        return "Adiós!"
    elif message in responses:
        return responses[message]
    else:
        best_match = get_close_matches(message, responses.keys(), n=1, cutoff=0.6)
        if best_match:
            return responses[best_match[0]]
        else:
            return None


# Si el chatbot no conoce la respuesta da la opción de enseñársela o saltarla
def get_response(message):
    response = get_best_match(message, responses)
    if response is not None:
        return f"{response}"
    else:
        messages += f"No conozco la respuesta. ¿Puedes enseñarme? o escribe 'skip' para saltar.\n"
        messages += f"Tú: {message}\n"
        answer_usuario = wait_for_user_response()
        if answer_usuario.lower() == "skip":
            return "Salteada."
        else:
            responses[message] = answer_usuario
            save_answers(responses)
            return "¡Gracias por enseñarme!"


# Indicar la respuesta a enseñar al bot por el terminal
def wait_for_user_response():
    while True:
        response = input("Usuario: ")
        if response.strip():
            return response


# Ruta principal de la aplicación
@app.route("/")
def index():
    return render_template("index.html")


# Ruta para manejar la interacción del chatbot
@app.route("/send_message", methods=["POST"])
def send_message():
    data = request.get_json()
    message = data["message"]
    if message:
        # Verificar si el mensaje es considerado "malo"
        if is_bad_question(message):
            response = "¡Esta pregunta o solicitud no está permitida!"
        else:
            response = get_response(message)

        return jsonify({"message": message, "response": response})


# Ruta para enseñar respuestas al bot
@app.route("/teach_bot", methods=["POST"])
def teach_bot():
    data = request.get_json()
    teach_message = data["teach_message"]
    teach_answer = data["teach_answer"]

    if teach_message and teach_answer:
        responses[teach_message] = teach_answer
        save_answers(responses)
        return jsonify(
            {
                "teach_message": teach_message,
                "teach_answer": teach_answer,
                "message": "¡Gracias por enseñarme!",
            }
        )
    else:
        return jsonify(
            {"message": "Error: La pregunta y la respuesta no pueden estar vacías."}
        )


if __name__ == "__main__":
    responses = load_answers()
    app.run(debug=True)
