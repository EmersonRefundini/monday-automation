from flask import Flask, request, jsonify
import worker

app = Flask(__name__)

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    if "challenge" in data:
        return jsonify({"challenge": data["challenge"]})

    item_id = str(data["event"]["pulseId"])
    print("Novo item recebido:", item_id)

    worker.fila.put(item_id)
    print("Enviado para fila:", item_id)

    return "OK", 200