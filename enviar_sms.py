import time, csv
from voximplant.apiclient import VoximplantAPI, VoximplantException

api = VoximplantAPI("1c1e49a7-2be1-........")
SOURCE = "57666"

with open("pruebaSMS7_15001-25000.csv", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        destination = row["numero"].strip()
        mensaje = f"¡Gracias por participar! Tu inscripcion {row['cedula']} para el sorteo de la Feria de las Flores 2026 fue recibida con exito."

        try:
            res = api.a2p_send_sms(SOURCE, destination, mensaje)
            print(destination, "OK", res)
        except VoximplantException as e:
            print(destination, "ERROR", e.message)

        time.sleep(0.2)
