import sqlite3
import logging

class Database:
    def __init__(self, db_path):
        """
        Initialize the database connection and create necessary tables.
        :param db_path: Path to the SQLite database file.
        """

        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()
        self._create_tables()
        logging.info(f"DB::i::Database initialized")

    def _create_tables(self) -> None:   
        """Create the necessary tables in the database."""
        logging.debug("DB::d::Creating tables if they do not exist.")
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS readings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sensor_id TEXT NOT NULL,
                value INTEGER NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                experiment_id INTEGER
                REFERENCES experiments(id) ON DELETE SET NULL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS experiments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                start_time DATETIME DEFAULT CURRENT_TIMESTAMP,
                end_time DATETIME
            )'''
        )   
        self.connection.commit()

    def start_experiment(self, name: str) -> int:
        """
        Start a new experiment and return its ID.
        :param name: Name of the experiment.
        :return: ID of the newly created experiment.
        """
        try:
            self.cursor.execute('''
                INSERT INTO experiments (name)
                VALUES (?)
            ''', (name,))
            self.connection.commit()
            experiment_id = self.cursor.lastrowid
            logging.info(f"DB::i::Experiment started: {name} with ID {experiment_id}")
            return experiment_id
        except sqlite3.Error as e:
            logging.error(f"DB::E::Error starting experiment: {e}")
            return -1   

    def insert_reading(self, sensor_id, values: list, experiment_id: int|None = None) -> None:
        """Insert a new reading into the database."""
        remade_values = [value + sensor_id*100 for value in values]
        
        try:
            # Get the current experiment ID if not provided
            if experiment_id is None:
                self.cursor.execute('''
                    SELECT id FROM experiments ORDER BY start_time DESC LIMIT 1
                ''')
                result = self.cursor.fetchone()
                if result:
                    experiment_id = result[0]
                else:
                    logging.warning("DB::W::No active experiment found, inserting reading without experiment ID.")
                    experiment_id = 0
                



            for value in remade_values:
                self.cursor.execute('''
                INSERT INTO readings (sensor_id, value, experiment_id)
                VALUES (?, ?, ?)
                ''', (sensor_id, value, experiment_id))
                self.connection.commit()
            logging.debug(f"DB::d::Inserted reading: {sensor_id} - {values} with experiment ID {experiment_id}")
        except sqlite3.Error as e:
            logging.error(f"DB::E::Error inserting reading: {e}")
    
    
    def fetch_readings(self, sensor_id: int|None=None, experiment_id: int|None=None)  -> list:
        """Fetch readings from the database, optionally filtered by sensor_id and experiment id."""
        print("DB::i::Fetching readings from the database.")
        try:
            data = None
            if sensor_id and experiment_id:
                self.cursor.execute('''
                    SELECT * FROM readings WHERE sensor_id = ? AND experiment_id = ?
                ''', (sensor_id, experiment_id))
                data = self.cursor.fetchall()
            elif sensor_id and not experiment_id:
                self.cursor.execute('''
                    SELECT * FROM readings WHERE sensor_id = ?
                ''', (sensor_id,))
                data = self.cursor.fetchall()
            elif not sensor_id and experiment_id:
                self.cursor.execute('''
                    SELECT * FROM readings WHERE experiment_id = ?
                ''', (experiment_id,))
                data = self.cursor.fetchall()
            else:
                self.cursor.execute('''
                    SELECT * FROM readings
                ''')
                data = self.cursor.fetchall()
                print(f"data: {data}")
            return data
        except sqlite3.Error as e:
            logging.error(f"DB::E::Error fetching readings: {e}")
            return []
    
    def close(self):
        """Close the database connection."""
        self.connection.close()
        logging.info("DB::i::Database connection closed.")

    def __enter__(self):
        """Enable the use of 'with' statement for automatic resource management."""
        return self 
    
    def __exit__(self, exc_type, exc_value, traceback):
        """Ensure the database connection is closed when exiting the 'with' block."""
        self.close()
        if exc_type:
            logging.error(f"DB::E::An error occurred: {exc_value}")
        return False
        # Return False to propagate exceptions, if any.

    def __del__(self):
        """Ensure the database connection is closed when the object is deleted."""
        self.close()
        print("Database object deleted and connection closed.")
        logging.debug("DB::d::Database object deleted and connection closed.")

# Example usage
if __name__ == "__main__":
    db = Database("/home/pi/Planterra/planterra.db")
    # db.insert_reading("sensor_1", 23.5)
    readings = db.fetch_readings()
    print(readings)
    db.close()