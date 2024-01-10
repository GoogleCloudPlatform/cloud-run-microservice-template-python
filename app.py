import signal
import sys
from types import FrameType

from flask import Flask, request

from utils.logging import logger
from models.data_processing_models import get_data_from_db_func, create_rsmp_and_mavg_for_the_data_func, store_proc_data_in_db_func
from prefect import Flow, task, flow

app = Flask(__name__)

# Prefect Tasks

@task
def get_data_from_db(request_data):
    return get_data_from_db_func(request_data)

@task
def create_rsmp_and_mavg_for_the_data(df, mav_period):
    return create_rsmp_and_mavg_for_the_data_func(df, mav_period)

@task
def store_proc_data_in_db(df, target_table_name):
    store_proc_data_in_db_func(df, target_table_name)

# Prefect Flows

@flow
def create_mavg_for_day_flow(request_data):
    # Task 1
    data_to_process = get_data_from_db(request_data)
    # Task 2
    df = create_rsmp_and_mavg_for_the_data(data_to_process, request_data['mavg_period'])
    # Task 3
    store_proc_data_in_db(df, "PROC_DATA")

# Flask Routes

@app.route("/create-mavg", methods=['POST'])
def create_mavg_for_day_endpoint():
    data = request.json
    data = request.get_json()
    create_mavg_for_day_flow(data)
    
    return "Data resampled and mavg created", 202

# Flask ...

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
