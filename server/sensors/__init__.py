import smbus3


class Sensor:
    def __init__(self, bus_number=1):
        self.bus = smbus3.SMBus(bus_number)

    def read_sensor(self, address: int) -> list[int]:
        try:
            data = []
            # Read a word from the sensor at the specified address
            for i in range(5):
                reading = self.bus.read_word_data(address, i)
                data.append(reading)
            return data
        except Exception as e:
            print(f"Error reading from sensor at address {address}: {e}")
            logging.error(f"Sensor::E::Error reading from sensor at address {address}: {e}")
            return None

    def close(self):    
        """Close the I2C bus."""
        self.bus.close()
        print("I2C bus closed.")

    def __del__(self):
        """Ensure the I2C bus is closed when the object is deleted."""
        self.close()
        print("Sensors object deleted and I2C bus closed.")

# Example usage:    
# sensors = Sensor()   
# sensor_data = sensors.read_sensor(0x1)  # Replace with actual sensor address 
