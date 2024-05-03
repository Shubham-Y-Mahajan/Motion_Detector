# Motion Detector by Shubham Yogesh Mahajan

## Setup

### To Run Software using main.py python script:
In Terminal Execute:
1) pip install opencv-python
2) pip install pyqt6
3) python main.py (or python3 main.py)

## Working Process
This Motion Detector takes video stream input from either a camera or a given video file.\
It sets the first frame as the base frame and then compares the subsequent frames it reads with the first frame. \
If there are differences between the base frame and the current frame , the software will highlight these 
differences with green rectangles.( The software will superimpose green rectangles on the current frame and display
the processed frame to the user)\
### Image Processing Algorithms Applied :
To achieve this motion detection ,on each frame the following image processing algorithms are applied :
1) Gray Frame conversion (converting coloured frame to gray frame)
2) Gaussian Blur ( blurring the frames to reduce the amount of data to be processed)
3) Absolute Difference (getting difference between base frame and current frame)
4) Thresh Binary algorithm (conversion to dual tone (absolute black and white) to reduce the data to be processed)
5) Frame Dilation (To remove noise from the frame)
6) Contour Detection (To detect motion)
The green rectangles are placed on these contours

## Functionality
The user can perform the following actions :
1) Start/Stop Video stream 

2) Change the source(input) of the video stream \
The input can be -\
a) First Device Camera (webcam by default)
b) Second Device Camera
c) A Video File

3) Choose to save the images of frames in which motion has been detected 
(images will be saved in the directory - Motion_Detector_Saved_Images/)
4) Choose the intervals in which motion detected frames are to be saved
As saving every single frame would be illogical storage-wise , the user can specify the interval for frame save.\
Example - Choose every 30th frame (in which motion was detected)

5) Change the Threshold value for conversion to Dual Tone

## Additional Notes about the software
1) Start Button has a time.sleep(2) applied to allow proper loading of device camera
2) Stop Button has time.sleep(2) applied to ensure all the temporary image frames get written and then deleted subsequently.
3) Whenever motion is detected, the image frames get saved in the folder Motion_Detector_Temp 
for the purpose of temporary storage.
4) If the user chooses to save object images then the images from this temporary folder get saved in the directory
Motion_Detector_Saved_Images according to the interval of saving set by the user.
5) Whenever the video stream is stopped , all the images from the temporary storage folder will be deleted.
(Note Motion_Detector_Saved_Images will ke kept untouched)
6) Sometimes when the camera loads ,it changes its sensitivity to light during run time which causes the software
to think that the frame has a difference wrt base frame. In that case the entire window might get outlined by 
the green rectangle.To solve that issue simply stop and start the video stream again.


