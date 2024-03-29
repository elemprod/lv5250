import pygame

import lv5250
from lv5250 import *
from lv5250.axis import *
from lv5250.arm_manager import *
from lv5250.axises import *
from lv5250.arm import *

import joy_config
from joy_config import *

pygame.init()
# This is a simple class that will help us print to the screen.
# It has nothing to do with the joysticks, just outputting the
# information.


class TextPrint:
    def __init__(self):
        self.reset()
        self.font = pygame.font.Font(None, 25)

    def tprint(self, screen, text):
        text_bitmap = self.font.render(text, True, (0, 0, 0))
        screen.blit(text_bitmap, (self.x, self.y))
        self.y += self.line_height

    def reset(self):
        self.x = 10
        self.y = 10
        self.line_height = 15

    def indent(self):
        self.x += 10

    def unindent(self):
        self.x -= 10


def move_to_complete(arm):
    print("Move Complete")


def button_down(arm, button_num):
    config = JoyConfig()

    if button_num < len(config.buttons):
        print(button_num)
        if config.buttons[button_num] != None:
            print(config.buttons[button_num].axis)
            current_arm = arm.arm_get(block=False)
            if current_arm != None:
                current_axises = current_arm.position
                if config.buttons[button_num].axis == AxisType.BASE:
                    current_axises.base.counts += config.buttons[button_num].counts
                elif config.buttons[button_num].axis == AxisType.WRIST_ROLL:
                    current_axises.wrist_roll.counts += config.buttons[button_num].counts
                elif config.buttons[button_num].axis == AxisType.WRIST_PITCH:
                    current_axises.wrist_pitch.counts += config.buttons[button_num].counts
                elif config.buttons[button_num].axis == AxisType.SHOULDER:
                    current_axises.shoulder.counts += config.buttons[button_num].counts
                arm.move_to_axises_cmd(
                    10, axises=current_axises, cb=move_to_complete)

            # arm.move_inc_cmd(
            #     config.buttons[button_num].axis, 50, config.buttons[button_num].counts)

        else:
            print("Button Not Defined")


def main():

    PORT = '/dev/cu.usbserial-FT5ZVFRV'
    arm = ArmManager(PORT)

    arm.remote_cmd()
    arm.clear_estop_cmd()
    arm.stop_cmd()
    #arm.hard_home_cmd()
    arm.torque_cmd()
    arm.get_pos_cmd()
    #arm.move_inc_cmd(AxisType.BASE, 50, 50000)

    # Set the width and height of the screen (width, height), and name the window.
    screen = pygame.display.set_mode((500, 700))
    pygame.display.set_caption("Joystick example")

    # Used to manage how fast the screen updates.
    clock = pygame.time.Clock()

    # Get ready to print.
    text_print = TextPrint()

    # This dict can be left as-is, since pygame will generate a
    # pygame.JOYDEVICEADDED event for every joystick connected
    # at the start of the program.
    joysticks = {}

    done = False
    while not done:
        # Event processing step.
        # Possible joystick events: JOYAXISMOTION, JOYBALLMOTION, JOYBUTTONDOWN,
        # JOYBUTTONUP, JOYHATMOTION, JOYDEVICEADDED, JOYDEVICEREMOVED
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True  # Flag that we are done so we exit this loop.

            if event.type == pygame.JOYBUTTONDOWN:
                print("Press")
                button_down(arm, event.button)

            if event.type == pygame.JOYBUTTONUP:
                print("Release")
                arm.stop_cmd()

            # Handle hotplugging
            if event.type == pygame.JOYDEVICEADDED:
                # This event will be generated when the program starts for every
                # joystick, filling up the list without needing to create them manually.
                joy = pygame.joystick.Joystick(event.device_index)
                joysticks[joy.get_instance_id()] = joy
                print(f"Joystick {joy.get_instance_id()} connencted")

            if event.type == pygame.JOYDEVICEREMOVED:
                del joysticks[event.instance_id]
                print(f"Joystick {event.instance_id} disconnected")

        # Drawing step
        # First, clear the screen to white. Don't put other drawing commands
        # above this, or they will be erased with this command.
        screen.fill((255, 255, 255))
        text_print.reset()

        # Get count of joysticks.
        joystick_count = pygame.joystick.get_count()

        text_print.tprint(screen, f"Number of joysticks: {joystick_count}")
        text_print.indent()

        # For each joystick:
        for joystick in joysticks.values():
            jid = joystick.get_instance_id()

            text_print.tprint(screen, f"Joystick {jid}")
            text_print.indent()

            # Get the name from the OS for the controller/joystick.
            name = joystick.get_name()
            text_print.tprint(screen, f"Joystick name: {name}")

            guid = joystick.get_guid()
            text_print.tprint(screen, f"GUID: {guid}")

            power_level = joystick.get_power_level()
            text_print.tprint(screen, f"Joystick's power level: {power_level}")

            # Usually axis run in pairs, up/down for one, and left/right for
            # the other. Triggers count as axes.
            axes = joystick.get_numaxes()
            text_print.tprint(screen, f"Number of axes: {axes}")
            text_print.indent()

            for i in range(axes):
                axis = joystick.get_axis(i)
                text_print.tprint(screen, f"Axis {i} value: {axis:>6.3f}")
            text_print.unindent()

            buttons = joystick.get_numbuttons()
            text_print.tprint(screen, f"Number of buttons: {buttons}")
            text_print.indent()

            for i in range(buttons):
                button = joystick.get_button(i)
                text_print.tprint(screen, f"Button {i:>2} value: {button}")
            text_print.unindent()

            hats = joystick.get_numhats()
            text_print.tprint(screen, f"Number of hats: {hats}")
            text_print.indent()

            # Hat position. All or nothing for direction, not a float like
            # get_axis(). Position is a tuple of int values (x, y).
            for i in range(hats):
                hat = joystick.get_hat(i)
                text_print.tprint(screen, f"Hat {i} value: {str(hat)}")
            text_print.unindent()

            text_print.unindent()

        # Go ahead and update the screen with what we've drawn.
        pygame.display.flip()

        # Limit to 30 frames per second.
        clock.tick(30)


if __name__ == "__main__":

    main()
    # If you forget this line, the program will 'hang'
    # on exit if running from IDLE.
    pygame.quit()
