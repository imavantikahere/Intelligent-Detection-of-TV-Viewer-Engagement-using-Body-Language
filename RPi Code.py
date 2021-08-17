#code that incorporates the learning model analysis, capturing the camera stream and the mob app code from the user

#final working code

import paho.mqtt.client as mqtt
import RPi.GPIO as GPIO
import time 
import os
import sys
import cv2
import os
from datetime import datetime
import keras
import matplotlib as plt
import pandas as pd
import numpy as np
import tensorflow.keras
from PIL import Image, ImageOps
import numpy as np
import couchdb
import tensorflow as tf
from PIL import Image
from datetime import datetime
from cloudant.client import Cloudant
from cloudant.error import CloudantException
from cloudant.result import Result, ResultByKey




def clouddb(showId,userId,EngagmentAverage,now, last):
    serviceUsername = "apikey-v2-16923uvpn7536bcm5rimsek7ziaxrendb3dgmeo1927m"
    servicePassword = "f3a0af32614ee446e0a24a9bca6e00ac"
    serviceURL = "https://apikey-v2-16923uvpn7536bcm5rimsek7ziaxrendb3dgmeo1927m:f3a0af32614ee446e0a24a9bca6e00ac@9292206b-ebd9-4fcc-8390-0a7ebc929d38-bluemix.cloudantnosqldb.appdomain.cloud/databasedemo"

    clientdb = Cloudant(serviceUsername, servicePassword, url=serviceURL)
    clientdb.connect()

    myDatabaseDemo = clientdb["databasedemo"]
            

    jsonDocument = {"showID": showId, "UserID": userId, "AverageEngagement" : EngagmentAverage, "StartTime" : str(now), "EndTime" : str(last)}
            
    newDocument = myDatabaseDemo.create_document(jsonDocument)
            
    print("sent to main db")


GPIO.setwarnings(False)

def on_connect(client, userdata, flags, rc):
    print("Connected with result code " + str(rc))
    client.subscribe("pi")
    print("subbed to pi")
    

def on_message(client, userdata, msg):
    print(msg.topic + " " + str(msg.payload))


    if msg.topic == "pi":
        if "on" in str(msg.payload):
            #os.system('./bashscript.sh')
            txt = str(msg.payload)
            print(txt)
            # setting the maxsplit parameter to 1, will return a list with 2 elements!
            x = txt.split("/", 2)

            showId= x[0]
            userId = x[1]
            
            print(x)
            #Below code will capture the video frames and will sve it a folder (in current working directory)
            
            dirname = '/home/pi/Desktop'
            in_stream = "rtsp://rtsp:12345678@192.168.1.196:554/av_stream/ch0"
            #video path
            video = cv2.VideoCapture(in_stream, cv2.CAP_FFMPEG)
            count = 0
            num_frames = 15
            # Start time
            start = time.time() #####################################################capture milliseconds
            #num_frames = 120;
            
            # datetime object containing current date and time
            now = datetime.now()
             
            print("now =", now)

            # dd/mm/YY H:M:S
            dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
            print("date and time =", dt_string)
            
            
            print("Capturing {0} frames".format(num_frames))

            vidcap = [] # all the results combined together
            n = 4
            while(n != 0): # will be linked with the mob app here - on message;  n != 0  ;    video.isOpened()
                for i in range(num_frames):
                    ret, frame = video.read()
                    if not ret:
                        break
                    else:
                    
                        name = "rec_frame"+str(count)+".jpg"
                        filename = dirname + "/image_" + str(datetime.now().strftime("%d-%m-%Y_%I-%M-%S_%p"))  + ".jpg"
                        cv2.imwrite(filename, frame)
                        
                        interpreter = tf.lite.Interpreter("/home/pi/Downloads/modelFinal.tflite")
                        interpreter.allocate_tensors()
                        
                        # Get input and output tensors.
                        input_details = interpreter.get_input_details()
                        output_details = interpreter.get_output_details()

                        # Test model on random input data.
                        input_shape = input_details[0]['shape']
                        input_data = np.array(np.random.random_sample(input_shape), dtype=np.float32)
                        interpreter.set_tensor(input_details[0]['index'], input_data)

                        interpreter.invoke()
                        output_data = interpreter.get_tensor(output_details[0]['index'])
                        #print(output_data)

                        
                        data = np.ndarray(shape=(1, 150, 150, 3), dtype=np.float32)
                        preprocessingTime1 = time.time()
                        
                        captureEnd = time.time()
                        
                        # Replace this with the path to your image
                        image = Image.open(filename)
                        
                        #resize the image to a 224x224 with the same strategy as in TM2:
                        #resizing the image to be at least 224x224 and then cropping from the center
                        size = (150, 150)
                        image = ImageOps.fit(image, size, Image.ANTIALIAS)

                        #turn the image into a numpy array
                        image_array = np.asarray(image)

                        # display the resized image
                        image.show()

                        # Normalize the image
                        normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1
                        preprocessingTime2 = time.time()
                        # Load the image into the array
                        data[0] = normalized_image_array
                        
                        # latancy test // time interfrance
                        modelTime1 = time.time()
                        
                        
                        input_shape = input_details[0]['shape']
                        input_tensor= np.array(np.expand_dims(data[0],0), dtype=np.float32)
                        input_index = interpreter.get_input_details()[0]["index"]
                        interpreter.set_tensor(input_index, input_tensor)
                        #Run the inference
                        interpreter.invoke()
                        
                        
                        
                        output_details = interpreter.get_output_details()

                        output_data = interpreter.get_tensor(output_details[0]['index'])
                        
                        results = np.squeeze(output_data)
                        
                        # latancy test // time interfrance
                        modelTime2 = time.time()
                        top_k = results.argsort()
                        vidcap.append(results)
                        n -= 1
                        print(results)
                                    
                        
                        count += 1
                    if cv2.waitKey(20) & 0xFF == ord('q'):
                        break
                    
                    time.sleep(5)
                #yield(4)
                    ####sleep here

            # End time
                end = time.time()
                # Time elapsed
                seconds = end - start
                print ("Time taken : {0} seconds".format(seconds))
                # Calculate frames per second
                fps  = num_frames / seconds
                print("Estimated frames per second : {0}".format(fps))
                
                print ("infrance time (both model timings)  ", modelTime2 - modelTime1)
                
                print ("preprocessing time   ", preprocessingTime2 - preprocessingTime1)
                
                print( "capture - start) ", captureEnd - start)
            video.release()
            last = datetime.now()
            print(vidcap)
            EngagmentAverage = 1- (sum(vidcap)/len(vidcap))
            print(EngagmentAverage)
            
            
            
            clouddb(showId,userId,EngagmentAverage,now, last)
            
            
            
            # Sending the results to the couchDB - the local db
            couch= couchdb.Server("http://192.168.1.49:5984/")
            user="admin"
            password="admin"

            couch= couchdb.Server("http://%s:%s@192.168.1.49:5984/" % (user,password))

            #for dbname in couch:
            #    print(dbname)
            # Sending the results to the couchDB - the local db
            db= couch["senior"]
            #print(type(showId))
            #print(type(userId))
            doc_id, doc_rev= db.save({'showID': showId, 'UserID': userId, 'AverageEngagement' : EngagmentAverage, 'StartTime' : str(now), 'EndTime' : str(last)})
            
            
            
            
            #html page for user and companies for the name and tv code
            #break
            
        elif "off" in str(msg.payload):
            print("off recived")
            exit()
            #break
            #time.sleep(1)
            #os.system('./bashscript.sh')



client = mqtt.Client()
#client = mqtt.Client(clean_session=CLEAN_SESSION)
#client.username_pw_set("htynlopx","Aj_2-C5AEXey")#replace with your user name and password
#client.connect("m10.cloudmqtt.com",11871,21871)
client.on_connect = on_connect
client.on_message = on_message
client.connect("broker.mqttdashboard.com")

client.loop_forever()

