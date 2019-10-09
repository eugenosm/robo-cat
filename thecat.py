from time import sleep

import ServoPi
import actuators


class TheCat:
    __leg_names = {'right front': 0, 'left front': 1, 'right rear': 2, 'left rear': 3}
    servo: ServoPi.Servo
    __legs = []
    __moves = {  # this values is just for test, and is needed to be adjusted.
        'forward': {'move': [  # servo position series for each leg, the pair is [hip, shin]
            [[30, 10], [38, 15], [45, 20], [52, 30], [60, 60], [52, 80], [45, 70], [38, 60]],  # FR
            [[45, 70], [38, 60], [30, 10], [38, 15], [45, 20], [52, 30], [60, 60], [52, 80]],  # FL
            [[60, 60], [52, 80], [45, 70], [38, 60], [30, 10], [38, 15], [45, 20], [52, 30]],  # RR
            [[45, 20], [52, 30], [60, 60], [52, 80], [45, 70], [38, 60], [30, 10], [38, 15]],  # RL
        ], 'start stage': 0},
        'backward': {'move': [
            [[30, 10], [38, 60], [45, 70], [52, 80], [60, 60], [52, 30], [45, 20], [38, 15]],
            [[45, 70], [52, 80], [60, 60], [52, 30], [45, 20], [38, 15], [30, 10], [38, 60]],
            [[60, 60], [52, 30], [45, 20], [38, 15], [30, 10], [38, 60], [45, 70], [52, 80]],
            [[45, 20], [38, 15], [30, 10], [38, 60], [45, 70], [52, 80], [60, 60], [52, 30]],
        ], 'start stage': 0},
        'left':  {'move': [
            [[30, 10], [38, 15], [45, 20], [52, 30], [60, 60], [52, 80], [45, 70], [38, 60],
             [30, 10], [38, 15], [45, 20], [52, 30], [60, 60], [52, 80], [45, 70], [38, 60]],
            [[45, 70], [45, 70], [38, 60], [38, 60], [30, 10], [30, 10], [38, 15], [38, 15],
             [45, 20], [45, 20], [52, 30], [52, 30], [60, 60], [60, 60], [52, 80], [52, 80]],
            [[60, 60], [52, 80], [45, 70], [38, 60], [30, 10], [38, 15], [45, 20], [52, 30],
             [60, 60], [52, 80], [45, 70], [38, 60], [30, 10], [38, 15], [45, 20], [52, 30]],
            [[45, 20], [45, 20], [52, 30], [52, 30], [60, 60], [60, 60], [52, 80], [52, 80],
             [45, 70], [45, 70], [38, 60], [38, 60], [30, 10], [30, 10], [38, 15], [38, 15]],
        ], 'start stage': 0},
        'right': {'move': [
            [[30, 10], [30, 10], [38, 15], [38, 15], [45, 20], [45, 20], [52, 30], [52, 30],
             [60, 60], [60, 60], [52, 80], [52, 80], [45, 70], [45, 70], [38, 60], [38, 60]],
            [[45, 70], [38, 60], [30, 10], [38, 15], [45, 20], [52, 30], [60, 60], [52, 80],
             [45, 70], [38, 60], [30, 10], [38, 15], [45, 20], [52, 30], [60, 60], [52, 80]],
            [[60, 60], [60, 60], [52, 80], [52, 80], [45, 70], [45, 70], [38, 60], [38, 60],
             [30, 10], [30, 10], [38, 15], [38, 15], [45, 20], [45, 20], [52, 30], [52, 30]],
            [[45, 20], [52, 30], [60, 60], [52, 80], [45, 70], [38, 60], [30, 10], [38, 15],
             [45, 20], [52, 30], [60, 60], [52, 80], [45, 70], [38, 60], [30, 10], [38, 15]],
        ], 'start stage': 0},
        'stop': {'move': [], 'start stage': 0},
    }
    __current_move = ''

    def __init__(self, servo=None, legs: dict = None):
        """
        Create TheCat Robot Model.
        :param servo: PCA9685 Servo Driver or None for create new one
        :param legs: legs servo channels dictionary. in form {'leg name': [hip, shin], ... }
               for example:
               {'right front': [1,2], 'left front': [3,4], 'right rear': [5,6], 'left rear': [7,8]}
               if None, then values from this example is used
        """
        if servo is None:
            self.servo = ServoPi.Servo()
        else:
            self.servo = servo

        if legs is None:
            for i in range(0, 7, 2):
                self.__legs.append(actuators.CatLeg(self.servo, [i+1, i+2]))
        else:
            for k, v in enumerate(legs):
                idx = self.__leg_names.get(k)
                if idx is None:
                    raise ValueError('Invalid leg name in constructor arguments')
                self.__legs[idx] = actuators.CatLeg(self.servo, v)
        self.__current_move = 'stop'

    def get_leg(self, idx) -> actuators.CatLeg:
        """
        Return Leg Actuator Object by name or index
        :param idx: integer index in __legs array or symbolic name like this 'right front'
        :return: Leg Actuator Object
        """
        if isinstance(idx, str):
            idx = self.__leg_names.get(idx)
            if idx is None:
                raise ValueError('Invalid leg name')
        if isinstance(idx, int):
            return self.__legs[idx]
        raise ValueError('Invalid leg identifier')

    def get_leg_servos(self, idx) -> [int, int]:
        """
        Return leg servo channel numbers
        :param idx:
        :return: [hip, shin]
        """
        return self.get_leg(idx).get_drives()

    def change_movement_mode(self, mode):
        """
        Change movement mode if right front leg in start position
        :param mode: movement mode string ('forward', 'backward', 'left', 'right', 'stop')
        :return: True if mode is set or already been set. Otherwise False
        """
        if mode == self.__current_move:
            return True
        move = self.__moves.get(mode)
        if mode is None:
            raise ValueError('Invalid move command')
        if self.get_leg(0).current_step_stage() != move['start stage']:
            return False  # let's try on next step/stage
        for i in range(len(self.__legs)):
            self.get_leg(i).set_custom_stages(move['move'][i])
        return True

    def next_stage(self, till_stage=-1):
        """
        Set next servo stages for all legs
        :param till_stage:
        :return:
        """
        for i in range(len(self.__legs)):
            self.get_leg(i).next_step_stage(till_stage=till_stage)

    def do_step(self, mode='forward'):
        """
        produce full step stages. if mode is not current move mode, then switch to it
        :param mode: movement mode string ('forward', 'backward', 'left', 'right', 'stop')
        :return:
        """
        stages = self.get_leg(0).step_stage_count()
        for stage in range(stages):
            self.next_stage()
            self.change_movement_mode(mode)
            sleep(0.2)

    def stop(self):
        """
        Finish current step stages and stop the servos of all legs
        :return:
        """
        if self.__current_move == 'stop':
            return
        move = self.__moves.get(self.__current_move)
        while self.get_leg(0).current_step_stage() != move['start stage']:
            self.next_stage()
            sleep(0.2)
        self.__current_move = 'stop'

