from gym_interface import RobotEnv
import time
import cv2

env = RobotEnv(simulator="pybullet")
observation, info = env.reset()


for _ in range(1000):
    observation, reward, terminated, truncated, info = env.step([0,0,0,0,0,0])
    # print(observation)

    # save the image
    cv2.imwrite("output.jpg", observation[0])


    time.sleep(1)