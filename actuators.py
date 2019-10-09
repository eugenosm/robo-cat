import ServoPi


class Actuator:
    """
    Base class for all servo actuators
    """
    _servo: ServoPi.Servo = None
    _drives = []

    def __init__(self, servo, drives=[]):
        self._servo = servo
        self._drives = drives


class CatLeg(Actuator):
    """
    Two bone leg class (is planned for robo-cat model)
    """
    _HIP = 0
    _SHIN = 1
    _drives = [0, 1]
    _step_stage = 0
    _stages = [
        [0, 0], [30, 30]
    ]

    def __init__(self, servo, drives=[0, 1]):
        super(CatLeg, self).__init__(servo, drives)

    def __set_servos_stage(self):
        """
        Set all actuator servos in current stage positions
        :return:
        """
        self._servo.move(channel=self._drives[self._HIP], position=self._stages[self._step_stage][self._HIP],
                         steps=ServoPi.SERVO_DEGREE_THRESHOLD)
        self._servo.move(channel=self._drives[self._SHIN], position=self._stages[self._step_stage][self._SHIN]
                         , steps=ServoPi.SERVO_DEGREE_THRESHOLD)

    def next_step_stage(self, till_stage=-1):
        """
        move servos to next preprogrammed stage to produce step
        :param till_stage: if used then change stages only untill given value
        :return: False if till_stage not reached, otherwise True
        """
        self.__set_servos_stage()
        next_stage = (self._step_stage + 1) % self.step_stage_count()
        if next_stage != till_stage:
            self._step_stage = next_stage
            return False
        return True

    def prev_step_stage(self, till_stage=-1):
        """
        move servos to previous preprogrammed stage to produce step
        :param till_stage: if used then change stages only until given value
        :return: False if till_stage not reached, otherwise True
        """
        self.__set_servos_stage()
        next_stage = (self._step_stage - 1)
        if next_stage < 0:
            next_stage = self.step_stage_count() - 1
        if next_stage != till_stage:
            self._step_stage = next_stage
            return False
        return True

    def step_stage_count(self):
        return len(self._stages)

    def current_step_stage(self):
        return self._step_stage

    def set_custom_stages(self, stages=[]):
        self._stages = stages

    def get_drives(self):
        return self._drives
