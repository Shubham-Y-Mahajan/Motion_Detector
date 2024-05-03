import sys
from datetime import datetime
import cv2
import time
import os
import glob
import re
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QImage, QPixmap, QAction, QIcon, QColor
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget, QMainWindow, QPushButton, QComboBox, QToolBar, \
    QGridLayout, QSlider, QDialog, QLineEdit, QMessageBox


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Motion Detector by Shubham Yogesh Mahajan")
        self.setMinimumSize(1200, 800)  # min window size

        settings_menu_item = self.menuBar().addMenu("&Settings")

        change_input = QAction("[Change Source (input) of video stream]", self)
        change_input.triggered.connect(self.input_settings)
        settings_menu_item.addAction(change_input)

        image_save_settings_action = QAction("[Change Image Save Settings]", self)
        image_save_settings_action.triggered.connect(self.image_save_settings)
        settings_menu_item.addAction(image_save_settings_action)

        threshold_settings_action = QAction("[Change Frame Processing Parameters]", self)
        threshold_settings_action.triggered.connect(self.threshold_settings)
        settings_menu_item.addAction(threshold_settings_action)

        about_menu_item = self.menuBar().addMenu("&About")
        """about_software_action = QAction("[Software]", self)
        about_menu_item.addAction(about_software_action)
        about_software_action.triggered.connect(self.about_software)"""

        about_developer_action = QAction("[Developer]", self)
        about_menu_item.addAction(about_developer_action)
        about_developer_action.triggered.connect(self.about_developer)


        """initializing variables"""
        self.all_images=None
        self.save_index=0 # the images with entity will not be saved by default
        self.save_rate=30 # by default every 30th frame will be saved

        self.Dual_Tone=50
        self.source_index=0
        self.source=0 # Default source is first camera on system
        self.runtime=0 # flag to check if video stream has started

        # Create a layout to arrange the tables
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        layout = QGridLayout(central_widget)

        """Creating the widgets"""
        start_button = QPushButton("Start")
        start_button.clicked.connect(self.start_vid_stream)
        start_button.setStyleSheet("QPushButton {"
                                     "background-color: blue;"
                                     "color: white;"
                                     "border-style: outset;"
                                     "border-width: 2px;"
                                     "border-radius: 10px;"
                                     "border-color: beige;"
                                     "font: bold 14px;"
                                     "padding: 6px;"
                                     "}"
                                     "QPushButton:hover {"
                                     "background-color: darkblue;"
                                     "}")

        stop_button = QPushButton("Stop")
        stop_button.clicked.connect(self.stop_vid_stream)
        stop_button.setStyleSheet("QPushButton {"
                                   "background-color: red;"
                                   "color: white;"
                                   "border-style: outset;"
                                   "border-width: 2px;"
                                   "border-radius: 10px;"
                                   "border-color: beige;"
                                   "font: bold 14px;"
                                   "padding: 6px;"
                                   "}"
                                   "QPushButton:hover {"
                                   "background-color: darkred;"
                                   "}")

        self.video_label = QLabel(self)
        self.video_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_settings_label=QLabel()
        self.current_settings_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.current_settings_label_text = f"<h2><u>CURRENT SETTINGS:</u></h2><br><br><br>" \
                                           f"<ul>" \
                                           "<li><h3>Video Stream Input = First Camera</h3></li><br>" \
                                           "<li><h3>Object images are not being saved</h3></li><br>" \
                                           f"<li><h3>Dual Tone Threshold = {self.Dual_Tone}</h3></li><br>" \
                                           f"</ul>"
        self.current_settings_label.setText(self.current_settings_label_text)
        self.current_settings_label.setStyleSheet("border: 1.5px solid black; padding: 3px; background-color: lightyellow;")
        




        """Adding The widgets to the layout"""
        layout.addWidget(start_button, 1, 3)
        layout.addWidget(stop_button, 1, 4)  # 1 =row , 2= column
        layout.addWidget(self.video_label, 2 , 3 , 5 , 2 )
        layout.addWidget(self.current_settings_label,3,1,3,1)


        self.default()

    def start_vid_stream(self):
        cap=cv2.VideoCapture(self.source)
        if not cap.isOpened(): # selected input not valid
            message_widget = QMessageBox()
            message_widget.setWindowTitle("Invalid Camera:")
            message_widget.setText("Try Switching The Camera Input")
            message_widget.exec()

        else:
            self.video = cv2.VideoCapture(self.source) # 0 => First Camera 1=> Second Camera, else its a filepath to video
            self.runtime = 1
            time.sleep(2) # giving some time for camera to load
            self.first_frame = None
            self.status_list = []
            self.count = 1
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(10)  # Update frame every 10 milliseconds

    def update_frame(self):
        status = 0

        check, frame = self.video.read()

        try:

            gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            # converting color to gray frame as that would reduce the amount of data to process
            gray_frame_gau = cv2.GaussianBlur(gray_frame, (15, 15), 0)
            # blurring the frame a little so that data to be processed is less, we don't need that sharpness
            # the numbers are the amount of blurriness we need

            if self.first_frame is None: # first_frame wil act as the base frame for comparison
                self.first_frame = gray_frame_gau

            delta_frame = cv2.absdiff(self.first_frame, gray_frame_gau) # comparison
            thresh_frame = cv2.threshold(delta_frame, self.Dual_Tone, 255, cv2.THRESH_BINARY)[1]

            '''if a pixel in delta_frame has a value equal to or higher than the Dual Tone Threshold
                then we assign that pixel the value 255 (absolute white)
                
                Thresh binary is the special algorithm being used
                the output is a list and thus we want the 2nd item of it thus we use [1]
                
                this is being done to make the delta_frame completely dual tone (black and white)
                this reduces the amount of data we process'''

            dil_frame = cv2.dilate(thresh_frame, None, iterations=2)
            # removing the noise from frames
            # None is the configuration array (no need here)
            # the more iterations the more the processing

            '''At this point in dil_frame=> new object is white and rest of it is black'''

            '''Now we will proceed to detect the contours around the white areas
            (rectangles / outline)'''

            contours, check = cv2.findContours(dil_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            for contour in contours:
                if cv2.contourArea(contour) < 5000:
                    continue
                    # Contour on an insignificant/tiny area

                x, y, w, h = cv2.boundingRect(contour)
                # x,y = co-ordinate of top left corner of rectangle
                # w, h are width and height of rectangle

                rectangle = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                # this will draw the rectangle over the original colored frame 'frame'
                # coordinates of top left and bottom right corner given
                # (0,255,0) is the color of rectangle (green)
                # 2 is the thickness of frame

                if rectangle.any(): # if any rectangle exists i.e an object is present in the frame
                    status = 1 # object present

                    if not os.path.exists("Motion_Detector_Temp"):
                        os.makedirs("Motion_Detector_Temp")
                    cv2.imwrite(f"Motion_Detector_Temp/{self.count}.png", frame)

                    self.count += 1

            # when status=0 -> object not in frame
            # when status=1 -> object in frame
            # if value of status goes from 0 to 1 it means object entered the frame
            # if value of status goes from 1 to 0 it means object left the frame

            self.status_list.append(status)
            self.status_list = self.status_list[-2:] # [-2:] are the latest/ last two items of the list

            # Converting the OpenCV image to QImage

            height, width, channel = frame.shape
            bytes_per_line = 3 * width
            qimage = QImage(frame.data, width, height, bytes_per_line, QImage.Format.Format_RGB888)
            pixmap = QPixmap.fromImage(qimage.rgbSwapped())
            self.video_label.setPixmap(pixmap)

        except cv2.error:
            pass
            # when the user closes the window self.closeEvent will be called
            # there may be extra iterations of self.update frame method and the frame cv2 would read would be 'None'
            # a 'None' frame would raise cv2.error

    def stop_vid_stream(self):
        try:
            self.video.release()
            self.default()
            time.sleep(2)
            self.runtime=0
            if self.save_index:
                all_images = glob.glob("Motion_Detector_Temp/*.png")
                if all_images:

                    # Sort the file paths based on the numeric part
                    sorted_images = sorted(all_images, key=get_numeric_part)

                    for i in range (0,int(len(sorted_images)),self.save_rate):
                        image_with_object = sorted_images[i]
                        print(image_with_object)
                        object_image = cv2.imread(image_with_object)
                        folder_path = "Motion_Detector_Saved_Images"
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                        now = datetime.now()
                        text = now.strftime("%H_%M_%S")
                        cv2.imwrite(f"{folder_path}/{text}-{i}.png", object_image) # to ensure uniqueness of naming and prevent overwrites

            all_images = glob.glob("Motion_Detector_Temp/*.png")
            if all_images:
                delete_images(all_images)
        except AttributeError: # raised when stop is clicked without ever clicking start
            pass

    def input_settings(self):
        if self.runtime != 1:
            self.input_dialog_box = QDialog()
            self.input_dialog_box.setMinimumSize(500, 400)
            self.input_dialog_box.setWindowTitle("Choose Input:")
            layout = QGridLayout()

            self.choose_label=QLabel("Select Video Stream Source:")
            layout.addWidget(self.choose_label, 1, 1)

            self.source_option = QComboBox()
            lst = ["First Camera (Inbuilt Webcam By Default )","Second Camera", "Video File"]
            self.source_option.addItems(lst)
            self.source_option.setCurrentIndex(self.source_index)
            layout.addWidget(self.source_option, 1, 2)

            self.filepath_label = QLabel("Filepath :")
            layout.addWidget(self.filepath_label, 2, 1)

            if type(self.source) == int:
                self.vid_filepath=QLineEdit("<Enter Video Filepath Here (if source is Video File) >")
            else:
                self.vid_filepath = QLineEdit(f"{self.source}")
            layout.addWidget(self.vid_filepath, 2, 2)


            apply_button = QPushButton("Apply Changes")
            apply_button.clicked.connect(self.update_source)
            layout.addWidget(apply_button, 3, 1)

            button = QPushButton("Cancel")
            button.clicked.connect(self.input_dialog_box.close)
            layout.addWidget(button, 3, 2)

            self.input_dialog_box.setLayout(layout)

            self.input_dialog_box.exec()
        else:
            message_widget = QMessageBox()
            message_widget.setWindowTitle("Invalid Operation")
            message_widget.setText("Video stream source cannot be changed during runtime")
            message_widget.exec()

    def update_source(self):
        index=self.source_option.currentIndex()
        if index == 0: # First Camera
            self.source_index=index
            self.source = 0
            self.update_current_settings_label()
            self.input_dialog_box.close()

        elif index == 1: # Second Camera
            self.source_index = index
            self.source = 1
            self.update_current_settings_label()
            self.input_dialog_box.close()

        else: # Video File Input
            filepath=self.vid_filepath.text()
            if os.path.exists(filepath):  # source is video file but filepath is incorrect
                self.source_index = index
                self.source=filepath
                self.update_current_settings_label()
                self.input_dialog_box.close()
            else:
                message_widget = QMessageBox()
                message_widget.setWindowTitle("Incorrect FILEPATH:")
                message_widget.setText("Specified video file does not exist")
                message_widget.exec()

    def image_save_settings(self):
        self.dialog_box = QDialog()
        self.dialog_box.setMinimumSize(500, 400)
        self.dialog_box.setWindowTitle("Change settings:")
        layout = QGridLayout()

        self.save_option = QComboBox()
        lst = [ "Do Not Save Images of Detected Entities","Save Images of Detected Entities"]
        self.save_option.addItems(lst)
        self.save_option.setCurrentIndex(self.save_index)
        self.save_option.activated.connect(self.sl_value_change)

        self.sl = QSlider(Qt.Orientation.Horizontal)
        self.sl.setMinimum(10)
        self.sl.setMaximum(60)
        self.sl.setValue(self.save_rate)
        self.sl.setSingleStep(10)
        self.sl.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.sl.setTickInterval(10)
        self.sl.setFixedWidth(200)

        if self.save_index:
            self.sl_label = QLabel(f"Every {self.save_rate}th object image will be saved")
        else:
            self.sl_label = QLabel(f"Object images are not being saved")

        self.sl_label.setFixedWidth(250)
        self.sl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sl.valueChanged.connect(self.sl_value_change)

        layout.addWidget(self.save_option,1,1,2,1)
        layout.addWidget(self.sl,2,1,1,1)

        layout.addWidget(self.sl_label,2,2,1,1)

        apply_button = QPushButton("Apply Changes")
        apply_button.clicked.connect(self.write_save_settings)
        layout.addWidget(apply_button,4,1,2,1)

        button = QPushButton("Cancel")
        button.clicked.connect(self.dialog_box.close)
        layout.addWidget(button,5,1,2,1)

        self.dialog_box.setLayout(layout)

        self.dialog_box.exec()

    def sl_value_change(self):
        try:
            save_rate=self.sl.value()
            save_status = self.save_option.currentIndex()  # reading the save option combobox

            if save_status:
                self.sl_label.setText(f"Every {save_rate}th object image will be saved")
            else:
                self.sl_label.setText(f"Object images are not being saved")
        except AttributeError: # attribute error might be raised in the first iteration of main window
            pass

    def write_save_settings(self):
        save_status=self.save_option.currentIndex() # index 1 = save image

        if save_status:
            self.save_index=1
        else:
            self.save_index=0

        self.save_rate=self.sl.value()

        self.update_current_settings_label()

        self.dialog_box.close()

    def threshold_settings(self):
        self.threshold_dialog_box = QDialog()
        self.threshold_dialog_box.setMinimumSize(600, 400)
        self.threshold_dialog_box.setWindowTitle("Change settings:                         "
                                                 "( Hover over [ ? ] icon to see ToolTip )")
        layout = QGridLayout()

        self.dualtone_sl = QSlider(Qt.Orientation.Horizontal)
        self.dualtone_sl.setMinimum(10)
        self.dualtone_sl.setMaximum(80)
        self.dualtone_sl.setValue(self.Dual_Tone)
        self.dualtone_sl.setSingleStep(10)
        self.dualtone_sl.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.dualtone_sl.setTickInterval(10)
        self.dualtone_sl.setFixedWidth(200)

        self.dualtone_sl_label = QLabel(f"Dual Tone Threshold = {self.dualtone_sl.value()}\n [ ? ]")
        self.dualtone_sl_label.setFixedWidth(250)
        self.dualtone_sl_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.dualtone_sl_label.setToolTip("The lower the Dual Tone Threshold number \n"
                                          "the higher the sensitivity for motion detection\n"
                                          "Recommended Value = 50")
        self.dualtone_sl.valueChanged.connect(self.dual_tone_sl_value_change)


        apply_button = QPushButton("Apply Changes")
        apply_button.clicked.connect(self.write_threshold_settings)

        button = QPushButton("Cancel")
        button.clicked.connect(self.threshold_dialog_box.close)



        """Adding the Widgets"""


        layout.addWidget(self.dualtone_sl, 1, 2)
        layout.addWidget(self.dualtone_sl_label, 1, 1)

        layout.addWidget(apply_button, 3, 1, 1, 1)
        layout.addWidget(button, 3, 2, 1, 1)




        self.threshold_dialog_box.setLayout(layout)

        self.threshold_dialog_box.exec()

    def dual_tone_sl_value_change(self):
        try:
            dt = self.dualtone_sl.value()
            self.dualtone_sl_label.setText(f"Dual Tone Threshold = {dt}\n [ ? ]")

        except AttributeError:  # attribute error might be raised in the first iteration of main window
            pass

    def write_threshold_settings(self):
        self.Dual_Tone=self.dualtone_sl.value()

        self.update_current_settings_label()

        self.threshold_dialog_box.close()

    def update_current_settings_label(self):
        text=f"<h2><u>CURRENT SETTINGS:</u></h2><br><br><br><ul>"
        if self.source == 0:
            text += "<li><h3>Video Stream Input = First Camera</h3></li><br>"
        elif self.source == 1:
            text += "<li><h3>Video Stream Input = Second Camera</h3></li><br>"
        else:
            text += f"<li><h3>Video Stream Input = Video File <br> Filepath = {self.source} </h3></li><br>"

        if self.save_index == 1:
            text += f"<li><h3>Object images are being saved every {self.save_rate}th frame</h3></li><br>"
        else:
            text +=  "<li><h3>Object images are not being saved</h3></li><br>"

        text += f"<li><h3>Dual Tone Threshold = {self.Dual_Tone}</h3></li><br></ul>"
        self.current_settings_label_text = text
        self.current_settings_label.setText(self.current_settings_label_text)

    def closeEvent(self, event):
        try:
            self.video.release()
            self.default()
            time.sleep(1)
            self.runtime=0
            if self.save_index:
                all_images = glob.glob("Motion_Detector_Temp/*.png")
                if all_images:

                    # Sort the file paths based on the numeric part
                    sorted_images = sorted(all_images, key=get_numeric_part)

                    for i in range (0,int(len(sorted_images)),self.save_rate):
                        image_with_object = sorted_images[i]
                        print(image_with_object)
                        object_image = cv2.imread(image_with_object)
                        folder_path = "Motion_Detector_Saved_Images"
                        if not os.path.exists(folder_path):
                            os.makedirs(folder_path)
                        now = datetime.now()
                        text = now.strftime("%H_%M_%S")
                        cv2.imwrite(f"{folder_path}/{text}-{i}.png", object_image) # to ensure uniqueness of naming and prevent overwrites

            all_images = glob.glob("Motion_Detector_Temp/*.png")
            if all_images:
                delete_images(all_images)
        except AttributeError: # raised when stop is clicked without ever clicking start
            pass
        super().closeEvent(event)

    def default(self):
        width = 600  # Adjust width as needed
        height = 500  # Adjust height as needed
        color = QColor(180, 220, 255)  # Red color, adjust RGB values as needed
        pixmap = QPixmap(width, height)
        pixmap.fill(color)

        # Set the pixmap to your QLabel
        self.video_label.setPixmap(pixmap)

    def about_software(self):
        message_widget = QMessageBox()
        message_widget.setWindowTitle("About Software:")
        text="This Motion Detector has been developed as an assessment for Python Developer " \
             "Intern at Vyorius Drones Private Limited.\n" \
             "Any feedback is highly appreciated.\n" \
             "I look forward to hearing from you soon!"
        message_widget.setText(text)
        message_widget.exec()

    def about_developer(self):
        message_widget = QMessageBox()
        message_widget.setWindowTitle("About Developer:")
        text="This software has been developed by Shubham Yogesh Mahajan from Thane West, Maharashtra.\n" \
             "I am currently pursuing BTech in Computer Science and Engineering at IIT Bhilai.\n\n" \
             "My Contact Details:\n" \
             "Email: shubhamy@iitbhilai.ac.in\n" \
             "Contact Number: 8879466601"
        message_widget.setText(text)
        message_widget.exec()
def delete_images(filepaths):
    if filepaths:
        for filepath in filepaths:
            if os.path.exists(filepath):
                os.remove(filepath)
            else:
                pass
    else:
        return 0 # Case occurs when you close the window without ever clicking the Start Button


# Custom sorting key to extract the numeric part of the filename
def get_numeric_part(filepath):
    match = re.search(r'(\d+)\.png$', filepath)
    return int(match.group(1)) if match else 0  # Assuming a default value of 0 if no numeric part is found




if __name__ == '__main__':

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()

    sys.exit(app.exec())