import os
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

    __version__ = "0.1.2"

    def __init__(self):
        # Camera index
        self.camera_index = []

        # Initialize Video Capture
        self.frame = None
        self.frame_rgb = None
        self.means_rgb = None
        self.is_running = 0

        # Gets the Available Cameras
        self.available_cameras = self.get_available_cameras()
        self.select_camera()

        # Figure
        self.fig = plt.figure()

        # Cameras Resolution
        self.width, self.height = cv2.VideoCapture(self.camera_index).get(3), cv2.VideoCapture(self.camera_index).get(4)

    def select_camera(self):
        print()

        i = 0
        for camera in self.available_cameras:
            i += 1
            print(f'{i}.    Camera {camera}')

        self.camera_index = int(input("What camera do you want to use? ")) - 1
        self.cap = cv2.VideoCapture(self.available_cameras[self.camera_index])

    def get_available_cameras(self):
        available_cameras = []
        for i in range(10):  # Try to access up to 10 cameras (adjust as needed)
            cap = cv2.VideoCapture(i)
            if cap.isOpened():
                available_cameras.append(i)
                cap.release()
        return available_cameras

    def capture_and_process_video(self):

        # Get the Capture
        self.cap = cv2.VideoCapture(self.available_cameras[self.camera_index])

        # Prints the Resolution
        print(f"Resolution: {self.width}, {self.height}")

        # Defines frame
        ret, self.frame = self.cap.read()

        # Sets the Style
        self.fig.set_facecolor('black')
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
            self.frame = cv2.rotate(self.frame, cv2.ROTATE_180)

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

            self.fig.clf() # Clears the frame

            # Display the frame and the color channel plots
            ax_img = self.fig.add_subplot(2, 1, 1)
            ax_img.set_xlim(0, self.width)
            ax_img.set_ylim(0, self.height)
            ax_img.imshow(self.frame_rgb)
            ax_img.axis('off')

            # Displays the Graph
            ax_rgb = self.fig.add_subplot(2, 1, 2)
            ax_rgb.plot(red_values[-16:], color="red", label="Red")
            ax_rgb.plot(green_values[-16:], color="green", label="Green")
            ax_rgb.plot(blue_values[-16:], color="blue", label="Blue")

            # Display Numbers
            ax_rgb.text(15, red_values[-1], np.round(red_values[-1]), color='white')
            ax_rgb.text(15, green_values[-1], np.round(green_values[-1]), color='white')
            ax_rgb.text(15, blue_values[-1], np.round(blue_values[-1]), color='white')

            # Display the mean values
            plt.figtext(0.02, 0.96, f'Means: [{red_mean}, {green_mean}, {blue_mean}]', color='white')
            #plt.figtext(0.02, 0.92, f'Max: [{red_max}, {green_max}, {blue_max}]')
            #plt.figtext(0.02, 0.88, f'Min: [{red_min}, {green_min}, {blue_min}]')

            if keyboard.is_pressed('q'):
                self.release_capture()
                self.stop()

            elif keyboard.is_pressed('w'):
                VideoCaptureProcessor.save_data(means_rgb, self.frame_rgb, self.frame)

            elif keyboard.is_pressed('c' or 'g'):
                self.release_capture()
                self.get_pixel_position()
                break

            # Pause briefly to display the frame
            plt.pause(0.00000001)


    def save_data(means_rgb, frame_rgb, frame):
        # Define the JSON format
        data = {
            "frames": len(means_rgb),
            "means_rgb": means_rgb,
            "raw_image": frame_rgb.tolist()
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

        # Open a new Matplotlib figure
        self.fig = plt.figure()

        # Rerun the main program
        self.capture_and_process_video()

    def release_capture(self):
        self.cap.release()

    def stop(self):
        if self.cap.isOpened():
            self.release_capture()
        plt.close(fig=self.fig)

if __name__ == "__main__":
    main_instance = VideoCaptureProcessor()
    main_instance.capture_and_process_video()
