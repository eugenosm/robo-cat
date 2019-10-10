from time import sleep
import math

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

    def __calc_ellips_coords(self, a, b, x):
        if x > a or x < -a or a < 0 or b < 0:
            return None
        bb = b * b
        return math.sqrt(bb - bb * x * x / (a * a))

    def __calc_y_l_and_gamma(self, a, b, h0, x, is_upper):
        """
        Returns leg effective y,l and gamma (see readme picture)
        :param a: step ellipse length (width)
        :param b: step ellipse height
        :param h0: leg effective height in zero position
        :param x: step (leg)  x coord
        :param is_upper: step phase (upper = True, lower = False)
        :return: y coord, effective leg length, effective leg angle against vertical h0
        """
        y = self.__calc_ellips_coords(a, b, x)
        y = h0 - b - y if is_upper else h0 - b + y
        l = math.sqrt(x*x + y*y)
        gamma = 90 - math.atan2(y, x) * 180 / math.pi
        return y, l, gamma

    def __calc_trg_c_angle(self, a, b, c):
        """
        calulate c angle in degree of abc triangle
        :param a: a side length
        :param b: b side length
        :param c: c side length
        :return: c angle value in degree
        """
        return math.acos((a*a + b*b - c*c)/(2*a*b)) * 180 / math.pi

    def __calc_trg_angles(self, a, b, c):
        """
        calculate all abc triangle angles.
        :param a: a side length
        :param b: b side length
        :param c: c side length
        :return: alpha, beta, gamma angles values in degree
        """
        alpha = self.__calc_trg_c_angle(b, c, a)
        betta = self.__calc_trg_c_angle(a, c, b)
        gamma = self.__calc_trg_c_angle(a, b, c)
        return alpha, betta, gamma

    def __calc_step_stages(self, a, b, h0, dx, hip, shin):
        """
        calculate all step stages for two bones leg
        :param a: step ellipse length (width)
        :param b: step ellipse height
        :param h0: leg effective height in zero position
        :param dx: x increase/decrease value for each stage
        :param hip: hip bone length
        :param shin: shin bone length
        :return: servo stages array for full step cycle
        """
        phases = [-1, 1, 1, -1]
        isupper = [False, True, True, False]
        steps = []
        x = 0
        for ph in range(4):
            i = 0
            while i < a:
                y, l, gamma = self.__calc_y_l_and_gamma(a, b, h0, x, isupper[ph])
                aa, ab, ac = self.__calc_trg_angles(hip, shin, l)
                steps.append([round(90 - gamma - ab),  round(180-ac)])
                i = i + dx
                x = x + phases[ph] * dx
        return steps

    def set_calculated_moves(self, hip, shin, stop_height, step_top, step_len, stages, shifts=[0, 0, 0, 0]):
        """
        set step stage values for all move modes by calculated ones
        :param hip: hip bone length
        :param shin: shin bone length
        :param stop_height: zero position leg height.
        :param step_top: max upper leg position
        :param step_len: longitude step threshold (actually this and prevoius is a sizes of ellipse)
        :param stages: the number of stages per step cycle. must be multiply of 4
        :param shifts: stage shift values for each leg
        :return: None
        """
        a = step_len / 2
        b = step_top / 2
        dx = step_len / (stages / 2)
        move = self.__calc_step_stages(a, b, stop_height, dx, hip, shin)
        bk_move = move.copy()
        bk_move.reverse()

        for i in range(4):
            self.__moves['forward']['move'][i] = move[shifts[i]:] + move[:shifts[i]]
            self.__moves['backward']['move'][i] = bk_move[shifts[i]:] + bk_move[:shifts[i]]

        slower = []
        for i in range(len(move)):
            slower.append(move[i])
            slower.append(move[i])
        shifts2 = [i * 2 for i in shifts]

        self.__moves['left']['move'][0] = move + move
        self.__moves['left']['move'][1] = slower[shifts2[1]:] + slower[:shifts2[1]]
        self.__moves['left']['move'][2] = move[shifts[2]:] + move[:shifts[2]] \
            + move[shifts[2]:] + move[:shifts[2]]
        self.__moves['left']['move'][3] = slower[shifts2[3]:] + slower[:shifts2[3]]

        self.__moves['right']['move'][0] = slower
        self.__moves['right']['move'][1] = move[shifts[1]:] + move[:shifts[1]] \
            + move[shifts[1]:] + move[:shifts[1]]
        self.__moves['right']['move'][2] = slower[shifts2[2]:] + slower[:shifts2[2]]
        self.__moves['right']['move'][3] = move[shifts[3]:] + move[:shifts[3]] \
            + move[shifts[3]:] + move[:shifts[3]]
