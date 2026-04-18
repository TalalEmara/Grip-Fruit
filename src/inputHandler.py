import pygame
import serial

class InputHandler:
    def __init__(self, serial_port='COM3', baudrate=9600):
        self.squeeze_triggered = False
        self.running = True
        self.ser = None
        
        try:
            self.ser = serial.Serial(serial_port, baudrate, timeout=0.1)
        except (serial.SerialException, ValueError) as e:
            print(f"Warning: Serial port not available: {e}")

    def update(self):
        self.squeeze_triggered = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                self.squeeze_triggered = True
        
        if self.ser and self.ser.in_waiting > 0:
            try:
                line = self.ser.readline().decode('utf-8').strip()
                if line == "PRESSED":
                    self.squeeze_triggered = True
            except Exception as e:
                print(f"Serial read error: {e}")

    def close(self):
        if self.ser:
            self.ser.close()