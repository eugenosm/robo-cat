import argparse
import keyboard
import sys

import service
import thecat


def main():
    actions=[
        'adjust', 'play'
    ]
    parser = argparse.ArgumentParser()
    parser.add_argument('action', nargs='?', choices=actions, metavar='action', help='')

    parser.add_argument('chan', nargs='?', metavar='chan', type=int, help='')
    parser.add_argument('position', nargs='?', metavar='position', type=int, help='')

    parser.add_argument('-c', '--calculated', action='store_true')
    parser.add_argument('-h0', '--h0', metavar='h0', default=9,
                        help='zero pointed leg height')
    parser.add_argument('-a', '--a', metavar='a', default=6,
                        help='step ellipse length')
    parser.add_argument('-b', '--b', metavar='b', default=2,
                        help='step ellipse height')
    parser.add_argument('-hip', '--hip', metavar='hip', default=6,
                        help='hip bone length')
    parser.add_argument('-shin', '--shin', metavar='shin', default=6,
                        help='shin bone length')
    parser.add_argument('-stages', '--stages', metavar='stages', default=12,
                        help='servo stages per step cycle(ellipse). must be multiply of 4')
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
        if args.calculated:
            shifts = [0, args.stages//4, args.stages//2, 3*args.stages//4]
            the_cat.set_calculated_moves(args.hip, args.shin, args.h0, args.b, args.a, args.stages, shifts)
        while True:
            if keyboard.is_pressed('`'):
                sys.exit(0)

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
