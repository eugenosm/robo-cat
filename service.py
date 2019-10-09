#!/usr/bin/env python
import ServoPi


class ServoUtils:
    """
    Service and diagnostic utils
    """
    __servo:ServoPi.Servo = None

    def __init__(self, servo=None, address=0x40, low_limit=1.0,
                 high_limit=2.0, reset=True):
        if servo is None:
            self.__servo = ServoPi.Servo(address, low_limit, high_limit, reset)
        else:
            self.__servo = servo

    def set_servo_to_zero_point(self, channel=0):
        """
        Moves servo to zero position. This would be needed for adjust actuator position while construction
        or after repair
        :param channel: 0 for all or channel number 1-15
        :return: None
        """
        self.__servo.move(channel, 0, ServoPi.SERVO_DEGREE_THRESHOLD)

    def set_servo_to_custom_position(self, channel=0, value=0, steps=ServoPi.SERVO_DEGREE_THRESHOLD):
        """
        Moves servo to zero position. This would be needed for adjust actuator position while construction
        or after repair
        :param channel: 0 for all or channel number 1-15
        :param value: position value (0..steps)
        :param steps: value threshold
        :return: None
        """
        self.__servo.move(channel, value, steps)
