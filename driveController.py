from helpers import *

# just have a command line utility, ask to do basic movements.
# only going to do forward, down, left, right
# and need an option to set speed.


def main():
    print("[INFO] Main Driving Command Line Utility.")
    speed = 50
    current_action = 'x'
    while True:
        # get user input for driving
        print(f"Current Speed {speed}, current Action: {current_action}")
        val = str(input("What do you want to do? (WASD for movement. x to stop, f to change speed.)\n"))
        current_action = val
        if val == 'x':
            stopDriving()
        elif val == 'w':
            drive(speed=speed, time=-1)
        elif val == 's':
            drive(speed=-1*speed, time=-1)
        elif val == 'a':
            driveLocamotionTrack(-speed, speed)
        elif val == 'd':
            driveLocamotionTrack(speed, -speed)
        elif val == 'f':
            try:
                n_speed = int(input("Enter new speed: 0 - 100: "))
                if n_speed > 100 or n_speed < 0:
                    raise Exception("Invalid range entered. Speeds are from 0 to 100")
                speed = n_speed
            except Exception as e:
                print("Invalid entry.", e)
        elif val == 'q':
            print("Quitting!!")
            stopDriving()
            break


if __name__ == "__main__":
    main()
