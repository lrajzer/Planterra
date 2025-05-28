from fastapi import FastAPI
from fastapi.responses import FileResponse
from paths import *
from db import Database
if not USE_I2C_MOCK:
    from sensors import Sensor
import uvicorn
import logging
import os
import time
from contextlib import asynccontextmanager
from utils.csv_converter import *

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', filename=os.path.join(LOG_PATH, 'sensor_api.log'), filemode='a')
# Check if we are using mock sensors
if USE_I2C_MOCK:
    logging.info("main::i::Using mock I2C sensors")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Startup event handler to initialize the TaskRunner.
    This runs when the FastAPI application starts.
    """
    logging.info("main::i::Starting TaskRunner...")
    task_runner = TaskRunner(interval=1)
    task_runner.run()
    yield
    logging.info("main::i::Stopping TaskRunner...")
    task_runner.running = False

app = FastAPI(
    title="Sensor API",
    description="API for reading humidity sensor data.",
    version="1.0.0",
    # lifespan=lifespan
)

if USE_I2C_MOCK:
    print("Using mock I2C sensors")
else:
    sensors = Sensor(1)

@app.get("/")
def read_root():
    return {"message": "Welcome to the Sensor API"}
@app.get("/sensors/{sensor_id}")
def read_sensor(sensor_id: str):
    """
    Endpoint to read sensor data by sensor ID.
    
    :param sensor_id: ID of the sensor to read (in hex).
    :return: Current sensor data as a 16-bit integer value in the range 0-1023.
    """
    if USE_I2C_MOCK:
        return {"sensor_id": sensor_id, "values": 42}

    try:
        return sensors.read_sensor(int(sensor_id, 16))  # Assuming sensor_id is an integer address
    except Exception as e:
        print(f"Error reading sensor {sensor_id}: {e}")
        logging.error(f"main::E::Error reading sensor {sensor_id}: {e}")
        return {"error": str(e), "status": "inactive"}

@app.get("/sensors")
def read_all_sensors():
    """
    Endpoint to read all sensors data.
    Data is a 16-bit integer value in the range 0-1023.
    
    :return: List of all sensors data.
    """
    # Here you would typically fetch all sensor data from a database or hardware
    # For demonstration, we return a mock response
    
    if USE_I2C_MOCK:
        return [
        {"sensor_id": "1", "value": 23},
        {"sensor_id": "2", "value": 19},
        {"sensor_id": "3", "value": 22}]

    for sensor_id in range(1, 6):
        try:
            sensor_data = sensors.read_sensor(sensor_id)
            if sensor_data is not None:
                return [{"sensor_id": sensor_id, "value": sensor_data}]
        except Exception as e:
            print(f"Error reading sensor {sensor_id}: {e}")
            logging.error(f"main::E::Error reading sensor {sensor_id}: {e}")
    return [[]]

@app.get("/health")
def health_check():
    """
    Health check endpoint to verify the API is running.
    
    :return: Health status of the API.
    """
    return {"status": "healthy", "message": "Sensor API is running smoothly."}
@app.get("/version")
def get_version():
    """
    Endpoint to get the version of the API.
    
    :return: Version information of the API.
    """
    return {"version": "1.0.0", "description": "Sensor API for reading humidity sensor data."}

@app.get("/download")
def download_readings():
    """
    Endpoint to download sensor readings as a CSV file.
    
    :return: CSV file containing sensor readings.
    """
    # global db
    db = Database("/home/pi/Planterra/planterra.db")
    try:
        readings = db.fetch_readings()
        if not readings:
            return {"error": "No readings found."}
        
        csv_string = convert_to_csv_string(readings)
        # Make the return a CSV file download
        if not csv_string:
            return {"error": "No readings found."}
        csv_file_path = os.path.join(LOG_PATH, f'sensor_readings{time.strftime("Y_%m_%d_%H:%M:%S")}.csv')
        with open(csv_file_path, 'w') as csv_file:
            csv_file.write(csv_string)
        logging.info("main::i::Readings downloaded successfully.")
        return FileResponse(csv_file_path, media_type='text/csv', filename=f'sensor_readings{time.strftime("%Y_%m_%d_%H:%M:%S")}.csv')
    except FileNotFoundError:
        logging.error("main::E::File not found while downloading readings.")
        return {"error": "File not found."}
    except sqlite3.Error as e:
        logging.error(f"main::E::Database error while downloading readings: {e}")
        return {"error": "Database error occurred."}

    except Exception as e:
        logging.error(f"main::E::Error downloading readings: {e}")
        return {"error": str(e)}

@app.get("/start_experiment")
def start_experiment():
    """
    Endpoint to start an experiment.
    
    :return: Confirmation message that the experiment has started.
    """
    # Here you would typically start an experiment, e.g., by initializing sensors or logging
    logging.info("main::i::Experiment started.")
    return {"message": "Experiment started successfully."}  

class TaskRunner:
    def __init__(self, interval: int = 60):
        """
        Initialize the TaskRunner with a specified interval.
        
        :param interval: Interval in seconds for running the task.
        """
        self.interval = interval
        self.running = True
    
    def run(self):
        """
        Run the task at the specified interval.
        This method should be run in a separate thread or process.
        """
        while self.running:
            try:
                logging.info("TaskRunner::i::Getting sensor data...")
                if USE_I2C_MOCK:
                    # Simulate sensor data retrieval
                    for sensor_id in range(1, 6):
                        db.insert_reading(sensor_id, 42)  # Mock sensor data
                    
                else:
                    # Retrieve sensor data from the actual sensors
                    for sensor_id in range(1, 6):
                        sensor_data = sensors.read_sensor(sensor_id)
                        if sensor_data is not None:
                            logging.info(f"TaskRunner::i::Sensor {sensor_id} data: {sensor_data}")
                            # Here you would typically save the data to the database
                            db.insert_reading(sensor_id, sensor_data)
            except KeyboardInterrupt:
                logging.info("TaskRunner::i::Stopping task runner...")
                self.running = False
                break

            except Exception as e:
                logging.error(f"TaskRunner::E::Error in task: {e}")
            finally:
                # Sleep for the specified interval
                time.sleep(self.interval)

1

if __name__ == "__main__":
    # Ensure the log directory exists
    if not os.path.exists(LOG_PATH):
        os.makedirs(LOG_PATH)
    # Run the FastAPI application using uvicorn
    logging.info("main::i::Starting Sensor API on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
    