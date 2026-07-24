import time, csv, os
from voximplant.apiclient import VoximplantAPI, VoximplantException
import requests

api = VoximplantAPI("1c1e49a7-2be1-4dd.....n")
SOURCE = "57666"
CSV_PATH = "pruebaSMS9_3001-3480.csv"
SENT_LOG = "enviados.log"          # checkpoint: un numero por linea
MAX_RETRIES = 5

# 1. Cargar numeros ya enviados (si el archivo no existe, set vacio)
enviados = set()
if os.path.exists(SENT_LOG):
    with open(SENT_LOG, encoding="utf-8") as f:
        enviados = set(line.strip() for line in f)

print(f"Ya enviados previamente: {len(enviados)}")

with open(CSV_PATH, encoding="utf-8") as f, open(SENT_LOG, "a", encoding="utf-8") as logf:
    reader = csv.DictReader(f)
    for row in reader:
        destination = row["numero"].strip()

        if destination in enviados:
            continue  # ya se envio, saltar

        mensaje = f"¡Gracias por participar! Tu inscripcion {row['cedula']} para el sorteo de la Feria de las Flores 2026 fue recibida con exito."

        for intento in range(1, MAX_RETRIES + 1):
            try:
                res = api.a2p_send_sms(SOURCE, destination, mensaje)
                print(destination, "OK", res)
                logf.write(destination + "\n")
                logf.flush()  # escribe a disco YA, no esperar buffer
                break
            except (VoximplantException, requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
                print(destination, f"ERROR intento {intento}/{MAX_RETRIES}", repr(e))
                if intento == MAX_RETRIES:
                    print(destination, "FALLO DEFINITIVO, revisar manualmente")
                else:
                    time.sleep(2 ** intento)  # backoff: 2s, 4s, 8s, 16s...

        time.sleep(0.2)

print("Terminado.")
