

import csv
import logging
import io

def convert_to_csv_string(readings):
    """
    Convert a list of readings to a CSV file.
    
    :param readings: List of tuples containing sensor readings.
    :param filename: Name of the output CSV file.
    """
    if not readings:
        logging.warning("No readings provided to convert to CSV.")
        return ""
    dummy_output = io.StringIO()
    writer = csv.writer(dummy_output, dialect='excel', quoting=csv.QUOTE_MINIMAL)
    writer.writerow(['id', 'sensor_id', 'value', 'timestamp'])  # Write header
    for reading in readings:
        writer.writerow(reading)  # Write each reading as a row
    csv_string = dummy_output.getvalue()
    dummy_output.close()
    logging.info("CSV_WRITER::i::Converted readings to CSV string.")
    return csv_string
    
if __name__ == "__main__":
    # Example usage
    sample_readings = [
        (1, 'sensor_1', 23, '2023-10-01 12:00:00'),
        (2, 'sensor_2', 19, '2023-10-01 12:05:00'),
        (3, 'sensor_3', 22, '2023-10-01 12:10:00')
    ]
    print(convert_to_csv_string(sample_readings))