# Intelligent Detection of TV Viewer Engagement using Body Language
This system aims to analyse the varying levels of engagement a viewer maintains while watching any kind of television content, including movies, shows, or documentaries. Analyses are linked to television content using show codes and these are used to generate content specific reports. These reports can be sent on to television content providers to provide a more detailed representation of what viewers are actually interested in. This is in contrast to current analysis models which simply use viewer counts to conclude whether content is being watched or not. Such traditional methods can be inaccurate due to a multitude of reasons. For example, viewer counts do not explicitly state viewer engagement, as hundreds of people leave their entertainment sets on during the lengthy durations of the day while not necessarily being engaged at all times. Furthermore, some content providers, such as Netflix, consider their content as completely watched even if the viewer watches only two minutes of the content in question. This is regardless if the viewer decided to switch content soon after and, as a result, leads to flawed and inaccurate analysis of viewer engagement. This project uses Computer Vision and Deep Learning to derive levels of viewer engagement through their body language and analyses such results to help TV network providers assess their performance. 

The system proposed, as shown in Figure 1, consists of the following major components: a mobile application, web application, a machine learning model running in a Raspberry Pi connected to a camera stream mounted on a TV facing the viewer, and a central cloud database to store the engagement results from the learning model. 

![image](https://user-images.githubusercontent.com/61798267/129786146-d14d1db8-b343-478a-9cfa-b97306f6ea4e.png)

_Dataset Collection_

For our image dataset, we collected 2000 images of people displaying different body languages while watching TV (Refer to Description of Dataset file). We manually labelled these datasets as “Engaged” and “Not Engaged” and fed them to our CNN model for training.


_Camera Interface and Mobile Application_

An MQTT protocol is established between the mobile application (client) and the Raspberry Pi (broker), thus helping the user start the system using the application. The user may enter the ID of the content that they are watching. In case of any errors, the viewers will be notified via the application. The camera RTSP stream is hence started, which is fed to the learning model running on the Raspberry Pi.

_Learning Model_

We built a CNN model using Keras and trained it using the dataset on a PC. We then saved the trained model and converted it to a tensorflow lite version and loaded it on the Raspberry Pi. Images captured from the camera after a set time interval pass  through the trained model and the average of results (Percentage of engaged/disengaged) are sent to a central cloud database. 

![image](https://user-images.githubusercontent.com/61798267/129789193-36bdaca3-fe69-4ac8-a4be-ea5a0a8bd86f.png)


_Central Database and Application Server_

An application server at the network operating side connects to the central database where the results are sent and generates a report of statistics from the database including, but not limited to, most engaged times, most engaged users, and most engaging shows. 

# Implementation

_Hardware_

The main hardware components for this system are the Raspberry Pi microcontroller and IP camera. The Raspberry Pi captures images from the camera stream and feeds them to the tensorflow lite version of our CNN learning. A mobile application connects to the Raspberry Pi to start the RTSP IP camera stream via the MQTT protocol, and the results obtained from the learning model are sent to a central CouchDB database instance in the Cloud.  We used the Raspberry Pi 4B because of it’s easy set up and easily available documentation. For the IP camera, we used the SONOFF IP camera because of its reliable RTSP support and reasonable frame rate.

_Software_ 

The main software components for this system are the following:

Mobile Application

The mobile application allows TV Show viewers to login using their credentials and start recording their engagement with the camera. First, the viewer is required to scan a QR code to configure a network connection with their IP camera. The content or show watched is identified by its respective TV network name. To start the camera, the user is required to select the network and show relevant to the content being watched. The camera stream is then fed to the learning model running on the Raspberry Pi. We used the HiveMQ broker (browser client version), which provides a messaging platform to connect IoT devices to. We used the mobile application as a publisher client to the broker i.e. to publish MQTT messages to the broker. 

Learning Model

We implemented a 2D Convolutional Neural Network (2D-CNN) deep learning model, on which we trained our dataset (See Appendix A). Our architecture consists of 4 
Convolution layers, each with a filter size of 3 x 3; coupled with 4 -2 x 2 Max-Pooling layers. The convolutional layers  are then followed by fully connected layers, with an output layer consisting of 2 nodes corresponding to engaged and not engaged. We use the ReLu activation function at each layer, and compile the model using binary cross entropy loss as it is a binary classification model. For optimization, we use the Nadam optimizer and a learning rate of 0.0001.

We trained our dataset on this model and observed that the accuracy is about 81 percent. We also tried using pre-trained models for this purpose, but it did not give us good accuracy since our dataset was gathered by us, and is not compatible with the images in the datasets used in the pretrained models used for transfer learning. After training and compiling the model, we saved it in an hd5 format. Finally, we converted it to a tensorflow lite version to run it on the Raspberry Pi. A summary of the accuracies and F1 scores obtained and ROC curves can be found in a separate file with the summary of training and testing results.

Database Server

The central database receives the average of the engagement results as a percent from the learning model for each frame captured. It receives a result each time a user finishes watching TV content. The following table contains the fields in the database.
Table IV: central database fields

![image](https://user-images.githubusercontent.com/61798267/129786927-a1bc2d6b-f8f7-4f92-9576-0a9a4c0246e4.png)

We also have a user database to fill and check for user credentials during sign up and sign in. Note that this is for users to sign up/log in to the system and to the web application to check their results. A network database with the network ID and password also exists so network operators can login to the web application to check their statistics. A TV show database consisting of each network and it’s ID, along with the TV show IDs and names it broadcasts also exists so more networks and TV Shows can be added to the catalogue in a structured manner.
Web Application: Our central web application connects to the cloud database to retrieve results for each TV network operator upon successful login. For each TV network operator, we display the following:
1. Most Engaged timeslot
2. Most Engaging TV Show of the corresponding TV network operator
3. Most Engaged user for the network operator 
A sample of our web application screen can be viewed below.

Web application Screenshots

![image](https://user-images.githubusercontent.com/61798267/129788169-223d8c6e-6626-43c3-b10a-9b2405ce60f1.png)

![image](https://user-images.githubusercontent.com/61798267/129788251-2df9e548-9f09-47ab-b742-1936e57be8ec.png)

![image](https://user-images.githubusercontent.com/61798267/129788308-e1083ed3-8ce2-4331-bce2-079932d9dfae.png)

![image](https://user-images.githubusercontent.com/61798267/129787058-2be571b2-8794-476e-9baa-82a8150c2610.png)






