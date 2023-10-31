import os
import pip
import PIL.Image as PIL
import matplotlib.pyplot as plt
import numpy as np
import cv2
import keyboard
import json
from time import strftime, gmtime

class VideoCaptureProcessor:
    """
    A class for capturing and processing video from a camera.
    """

    # Changes Text color
    red_text = "\033[91m"
    reset_color = "\033[0m"

    def __init__(self):
        # Initialize Video Capture
        self.cap = cv2.VideoCapture(0)
        self.frame = None
        self.frame_rgb = None
        self.means_rgb = None


    def capture_and_process_video(self):
        # Defines frame
        ret, self.frame = self.cap.read()
        self.cap = cv2.VideoCapture(0)

        # Sets the Style
        plt.style.use('dark_background')

        # Check if the video capture was opened successfully
        if not self.cap.isOpened():
            print("Error: Could not open video capture.")
            return

        # Create empty arrays to store the color channels and means_rgb
        red_values, green_values, blue_values = [], [], []
        means_rgb = []

        while True:
            ret, self.frame = self.cap.read()

            if not ret:
                break

            self.frame_rgb = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB

            # Calculate the mean, max, and min values for each color channel
            red_mean, green_mean, blue_mean = np.mean(self.frame_rgb, axis=(0, 1))
            #red_max, green_max, blue_max = np.max(self.frame_rgb, axis=(0, 1))
            #red_min, green_min, blue_min = np.min(self.frame_rgb, axis=(0, 1))

            # Append the mean values to the respective arrays
            red_values.append(red_mean)
            green_values.append(green_mean)
            blue_values.append(blue_mean)
            means_rgb.append([red_mean, green_mean, blue_mean])

            # Display the frame and the color channel plots
            plt.clf()

            plt.subplot(2, 1, 1)
            plt.imshow(self.frame_rgb)
            plt.axis('off')

            plt.subplot(2, 1, 2)
            plt.plot(red_values[-16:], color="red", label="Red")
            plt.plot(green_values[-16:], color="green", label="Green")
            plt.plot(blue_values[-16:], color="blue", label="Blue")

            # Display Numbers
            plt.text(15, red_values[-1], np.round(red_values[-1]))
            plt.text(15, green_values[-1], np.round(green_values[-1]))
            plt.text(15, blue_values[-1], np.round(blue_values[-1]))

            # Display the mean values
            plt.figtext(0.02, 0.96, f'Means: [{red_mean}, {green_mean}, {blue_mean}]')
            #plt.figtext(0.02, 0.92, f'Max: [{red_max}, {green_max}, {blue_max}]')
            #plt.figtext(0.02, 0.88, f'Min: [{red_min}, {green_min}, {blue_min}]')

            if keyboard.is_pressed('q'):
                self.stop()
            elif keyboard.is_pressed('w'):
                VideoCaptureProcessor.save_data(means_rgb, self.frame_rgb, self.frame)
            elif keyboard.is_pressed('c' or 'g'):
                self.release_capture()
                self.get_pixel_position()
                break

            # Pause briefly to display the frame
            plt.pause(0.0001)


    def save_data(means_rgb, frame_rgb, frame):
        # Define the JSON format
        data = {
            "frames": len(means_rgb),
            "means_rgb": f"{means_rgb}",
            "raw_image": f"{frame_rgb.tolist()}"
        }

        # Get the time
        time = strftime("%Y-%m-%d@%H-%M-%S", gmtime())

        # Saves Image
        cv2.imwrite(f'image-{time}.png', frame)

        # Write the dictionary to a JSON file
        with open(f'data-{time}.json', 'w') as f:
            json.dump(data, f, indent=4)

        print("Saved!")
        plt.figtext(0.02, 0.84, "Saved!")

    def get_pixel_position(self):
        # Closes Window
        plt.close()

        # Initializes the image
        cv2.imwrite('%TEMP%.png', self.frame)
        img = PIL.open('%TEMP%.png', mode='r')

        # Get the tuple from the console
        pixel_xy = input("Enter pixel x, y: ")

        # Convert the tuple to a list
        pixel_xy = pixel_xy.split(",")

        # Tries to get pixel color
        try:
            pos_x = np.subtract(int(pixel_xy[0]), 1)
            pos_y = np.subtract(int(pixel_xy[1]), 1)
            pixel_rgb = img.getpixel(xy=(pos_x, pos_y))
            print(pixel_rgb)
            img.close() # Closes Var Img

        # Checks for a Value ERROR
        except (ValueError, TypeError, IndexError, OverflowError, SystemError) as ERROR:
            img.close()
            print(VideoCaptureProcessor.red_text + str(ERROR) + VideoCaptureProcessor.reset_color)
            self.get_pixel_position()

        try:
            os.remove('%TEMP%.png')  # Deletes the image
        except FileNotFoundError as ERROR:
            print(VideoCaptureProcessor.red_text + str(ERROR) + VideoCaptureProcessor.reset_color)

        # Release the video capture here
        self.release_capture()

        # Reruns the Main Program
        self.capture_and_process_video()

    def release_capture(self):
        self.cap.release()

    def stop(self):
        if self.cap.isOpened():
            self.release_capture()
        plt.close()
        quit(0)


if __name__ == "__main__":
    main_instance = VideoCaptureProcessor()
    main_instance.capture_and_process_video()
