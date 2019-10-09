import argparse
import keyboard
import os

import service
import thecat


def main():
    actions=[
        'adjust', 'play'
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=actions, metavar='action', help='')
    parser.add_argument('chan', nargs='?', metavar='chan', help='')
    parser.add_argument('position', nargs='?', metavar='position', help='')

    args = parser.parse_args()

    if args.action == 'adjust':
        servo_utils = service.ServoUtils()
        if args.chan is None:
            servo_utils.set_servo_to_zero_point()
        if args.position is None:
            servo_utils.set_servo_to_zero_point(int(args.chan))
        else:
            servo_utils.set_servo_to_custom_position(int(args.chan), int(args.position))

    if args.action == 'play':
        the_cat = thecat.TheCat()
        while True:
            if keyboard.is_pressed('`'):
                os.exit(0)

            elif keyboard.is_pressed('w'):
                the_cat.do_step('forward')
            elif keyboard.is_pressed('s'):
                the_cat.do_step('backward')
            elif keyboard.is_pressed('a'):
                the_cat.do_step('left')
            elif keyboard.is_pressed('d'):
                the_cat.do_step('right')
            else:
                the_cat.stop()


if __name__ == '__main__':
    main()
