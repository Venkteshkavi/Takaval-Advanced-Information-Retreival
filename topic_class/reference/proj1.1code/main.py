#!/usr/bin/env python
# coding: utf-8
import pandas as pd
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.callbacks import EarlyStopping, TensorBoard

import numpy as np
import matplotlib.pyplot as plt

print('UBID: egnanach')
print('Person Number: 50290792')

def fizzbuzz(n):
    
    # Logic Explanation
    if n % 3 == 0 and n % 5 == 0:
        #The number that is divisible by both 3 and 5 are labled as fizzbuzz
        return 'FizzBuzz'
    elif n % 3 == 0:
        #The number that is divisible by only 3 is labled as fizz
        return 'Fizz'
    elif n % 5 == 0:
        #The number that is divisible by only 5 is labled as buzz
        return 'Buzz'
    else:
        #The number that is neither divisible by 3 or 5 is labled as other
        return 'Other'


# Create Training and Testing Datasets in CSV Format

def createInputCSV(start,end,filename):
    
    # Why list in Python?
    # A list in python is an array like data structure. Here we store our input and output in a list.
    # We use list because the data is ordered and is changeable.Duplicate values are also allowed in list.
    inputData   = []
    outputData  = []
    
    # Why do we need training Data?
    # The model that we create at first is untaught and it will not be able to predict future outcomes.
    # In order to give our model some knowledge and make it more intelligent, we train our model with
    # a set of data known as training data. This data will help our model to identify the pattern and
    # learn from the given set of inputs. By doing this our model will be able to predict outcomes of
    # data outside the given training set using the trained pattern.
    for i in range(start,end):
        inputData.append(i)
        outputData.append(fizzbuzz(i))
    
    # Why Dataframe?
    # A dataframe is a series of objects and is a two dimensional tabular data structure.
    # Since we use csv files as input and output, dataframe has a similar structure which
    # helps in managing the input and output efficiently. It is also used to plot the graphs.
    # It is like a dictionary where all the inputs are under the key input and the output
    # is under the key label.
    dataset = {}
    dataset["input"] = inputData
    dataset["label"] = outputData
    
    # Writing to csv
    pd.DataFrame(dataset).to_csv(filename)
    
    print(filename, "Created!")


# Processing Input and Label Data

def processData(dataset):
    
    # Why do we have to process?
    # Processing data is a required step before we build a model. Since different algorithms or models
    # require different kind or format of data as its input, hence processing a data will help in better 
    # performance and delivers better results. Processing also helps in increasing the number of features
    # our input data set has, thus helps in increasing the accuracy of the model by providing more features.
    data   = dataset['input'].values
    labels = dataset['label'].values
    
    processedData  = encodeData(data)
    processedLabel = encodeLabel(labels)
    
    return processedData, processedLabel

def encodeData(data):
    
    processedData = []
    
    for dataInstance in data:
        
        # Why do we have number 10?
        # The input size of the data is 10. We actually convert the input integers into 10 bits binary data. 
        # It will also give our inputs more feature thus getting a more accurate predictions.
        processedData.append([dataInstance >> d & 1 for d in range(10)])
    
    return np.array(processedData)

def encodeLabel(labels):
    
    processedLabel = []
    
    for labelInstance in labels:
        if(labelInstance == "FizzBuzz"):
            # Fizzbuzz
            processedLabel.append([3])
        elif(labelInstance == "Fizz"):
            # Fizz
            processedLabel.append([1])
        elif(labelInstance == "Buzz"):
            # Buzz
            processedLabel.append([2])
        else:
            # Other
            processedLabel.append([0])

    return np_utils.to_categorical(np.array(processedLabel),4)


# Model Definition

input_size = 10
drop_out = 0.1
first_dense_layer_nodes  = 512
second_dense_layer_nodes = 4

def get_model():
    
    # Why do we need a model?
    # A machine learning model is used to predict an output for a given set of inputs.
    # There are various models, models are chosen depending on the kind of input, output and 
    # the nature of the problem, for example, a classification type of problem can be solved
    # using a sequential machine learning model. Each model is based on certain algorithm.
    
    # Why use Dense layer and then activation?
    # Dense Layer : 
    # Since we are carrying out a linear operation on the input layer, we use a dense layer.
    # A dense layer is formed when all the nodes in the network are connected with each other making it dense.
    # In a dense layer, a node calculates a weighted sum of inputs and adds a bias to it.
    #
    # Activation : 
    # An activation function is used to decide whether a node should be activated or not.
    # The acivation function is used to make the result of the matrix multiplication in a rational range.
    #
    #
    # Since the activation function is applied on the output of the dense layer, we use the dense layer
    # first and then the activation function. The activation function is used when the node finishes
    # calculating the weighted sum of inputs and is applied to the result of the calculation done by the node.
    
    # Why use sequential model with layers?
    # Since our model takes only one input and the layers are stacked on top of each other, we use sequential
    # model with layers. Moreover the problem we try to solve is a classification problem. For classification
    # type of problems, a sequential model is better.
    model = Sequential()
    
    # Here we add our first dense layer for our model
    model.add(Dense(first_dense_layer_nodes, input_dim=input_size))
    model.add(Activation('relu'))
    
    # Why dropout?
    # Drop out is used to drop units from hidden and visible layers (except the output layer) of the neural network.
    # It is used to prevent overfitting from occuring in the neural network and tries to reduce it.
    # In our model we've set the drop out as 0.2 which means there's a 0.2 or 20% probability that a hidden
    # layer will be set to zero. It helps in regularizing our neural network model.
    model.add(Dropout(drop_out))
    
    # This is the second dense layer of our model, which is also the output layer
    model.add(Dense(second_dense_layer_nodes))
    model.add(Activation('softmax'))
    
    # Why Softmax?
    # In the second layer of our neural network we use softmax function. Since the output we receive
    # is more discrete, we need a method to find its true probability. This will help to identify which 
    # class does the object belongs to. This is done using the softmax function.
    # The result of softmax function is a probability of which the node belongs to a particular class.
    
    model.summary()
    
    # Why use categorical_crossentropy?
    # Categorical cross entropy is a loss function that is used to minimize the target values. 
    # It is used to optimize our model. It is alse used for probability estimation.
    model.compile(optimizer='adadelta',
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

# Create datafiles
createInputCSV(101,1001,'training.csv')
createInputCSV(1,101,'testing.csv')


model = get_model()


validation_data_split = 0.2
num_epochs = 10000
model_batch_size = 128
tb_batch_size = 32
early_patience = 100

tensorboard_cb   = TensorBoard(log_dir='logs', batch_size= tb_batch_size, write_graph= True)
earlystopping_cb = EarlyStopping(monitor='val_loss', verbose=1, patience=early_patience, mode='min')

# Read Dataset
dataset = pd.read_csv('training.csv')

# Process Dataset
processedData, processedLabel = processData(dataset)
history = model.fit(processedData
                    , processedLabel
                    , validation_split=validation_data_split
                    , epochs=num_epochs
                    , batch_size=model_batch_size
                    , callbacks = [tensorboard_cb,earlystopping_cb]
                   )

#get_ipython().run_line_magic('matplotlib', 'inline')
df = pd.DataFrame(history.history)
df.plot(subplots=True, grid=True, figsize=(10,15))
plt.savefig('output.png')
plt.show()

def decodeLabel(encodedLabel):
    if encodedLabel == 0:
        return "Other"
    elif encodedLabel == 1:
        return "Fizz"
    elif encodedLabel == 2:
        return "Buzz"
    elif encodedLabel == 3:
        return "FizzBuzz"

wrong   = 0
right   = 0

testData = pd.read_csv('testing.csv')

processedTestData  = encodeData(testData['input'].values)
processedTestLabel = encodeLabel(testData['label'].values)
predictedTestLabel = []

for i,j in zip(processedTestData,processedTestLabel):
    y = model.predict(np.array(i).reshape(-1,10))
    predictedTestLabel.append(decodeLabel(y.argmax()))
    
    if j.argmax() == y.argmax():
        right = right + 1
    else:
        wrong = wrong + 1

print("Errors: " + str(wrong), " Correct :" + str(right))

print("Testing Accuracy: " + str(right/(right+wrong)*100))

# Please input your UBID and personNumber 
testDataInput = testData['input'].tolist()
testDataLabel = testData['label'].tolist()

testDataInput.insert(0, "UBID")
testDataLabel.insert(0, "egnanach")

testDataInput.insert(1, "personNumber")
testDataLabel.insert(1, "50290792")

predictedTestLabel.insert(0, "")
predictedTestLabel.insert(1, "")

output = {}
output["input"] = testDataInput
output["label"] = testDataLabel

output["predicted_label"] = predictedTestLabel

opdf = pd.DataFrame(output)
opdf.to_csv('output.csv')




