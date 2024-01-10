import signal
import sys
from types import FrameType
from multiprocessing import Process

from flask import Flask, request

from utils.logging import logger
from models.data_processing_models import create_mvg
from prefect import Flow, task, flow

app = Flask(__name__)

@task
def create_mavg_for_day_task(data):
    create_mvg(data)
    logger.info("Data processed and stored in PROC_DATA table")

@flow
def create_mavg_for_day_flow(data):
    create_mavg_for_day_task(data)

@app.route("/create-mavg", methods=['POST'])
def create_mavg_for_day_endpoint():
    data = request.json
    data = request.get_json()
    create_mavg_for_day_flow(data)
    # flow_state = flow.run(parameters={"data": data})
    
    return "Data processing task initiated", 202

def shutdown_handler(signal_int: int, frame: FrameType) -> None:
    logger.info(f"Caught Signal {signal.strsignal(signal_int)}")

    from utils.logging import flush

    flush()

    # Safely exit program
    sys.exit(0)


if __name__ == "__main__":
    # Running application locally, outside of a Google Cloud Environment

    # handles Ctrl-C termination
    signal.signal(signal.SIGINT, shutdown_handler)

    # create_mavg_for_day()

    app.run(host="localhost", port=8080, debug=True)
else:
    # handles Cloud Run container termination
    signal.signal(signal.SIGTERM, shutdown_handler)
