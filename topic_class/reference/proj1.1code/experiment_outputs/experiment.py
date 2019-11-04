#!/usr/bin/env python
# coding: utf-8

import pandas as pd
from keras.utils import np_utils
from keras.models import Sequential
from keras.layers import Dense, Activation, Dropout
from keras.callbacks import EarlyStopping, TensorBoard
import numpy as np
import time
import matplotlib.pyplot as plt
import os

global testIteration
global testHyper
global testHyperValue

def fizzbuzz(n):
    
    # Logic Explanation
    if n % 3 == 0 and n % 5 == 0:
        return 'FizzBuzz'
    elif n % 3 == 0:
        return 'Fizz'
    elif n % 5 == 0:
        return 'Buzz'
    else:
        return 'Other'

def createInputCSV(start,end,filename):
    
    # Why list in Python?
    inputData   = []
    outputData  = []
    
    # Why do we need training Data?
    for i in range(start,end):
        inputData.append(i)
        outputData.append(fizzbuzz(i))
    
    # Why Dataframe?
    dataset = {}
    dataset["input"]  = inputData
    dataset["label"] = outputData
    
    # Writing to csv
    pd.DataFrame(dataset).to_csv(filename)
    
    print(filename, "Created!")

def processData(dataset):
    
    # Why do we have to process?
    data   = dataset['input'].values
    labels = dataset['label'].values
    
    processedData  = encodeData(data)
    processedLabel = encodeLabel(labels)
    
    return processedData, processedLabel

def encodeData(data):
    
    processedData = []
    
    for dataInstance in data:
        
        # Why do we have number 10?
        processedData.append([dataInstance >> d & 1 for d in range(10)])
    
    return np.array(processedData)

def decodeLabel(encodedLabel):
    if encodedLabel == 0:
        return "Other"
    elif encodedLabel == 1:
        return "Fizz"
    elif encodedLabel == 2:
        return "Buzz"
    elif encodedLabel == 3:
        return "FizzBuzz"

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

def get_model(inputs):
    input_size = inputs['input_size']
    drop_out = inputs['drop_out']
    first_dense_layer_nodes  = inputs['first_dense_layer_nodes']
    second_dense_layer_nodes = inputs['second_dense_layer_nodes']
    # Why do we need a model?
    # Why use Dense layer and then activation?
    # Why use sequential model with layers?
    model = Sequential()
    
    model.add(Dense(first_dense_layer_nodes, input_dim=input_size))
    model.add(Activation(inputs['first_activation']))
    
    # Why dropout?
    model.add(Dropout(drop_out))

    model.add(Dense(second_dense_layer_nodes))
    model.add(Activation(inputs['second_activation']))
    # Why Softmax?
    
    model.summary()
    
    # Why use categorical_crossentropy?
    model.compile(optimizer=inputs['optimizer'],
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])
    
    return model

def run_model(inputs):
    model = get_model(inputs)

    validation_data_split = inputs['validation_data_split']
    num_epochs = inputs['num_epochs']
    model_batch_size = inputs['model_batch_size']
    tb_batch_size = inputs['tb_batch_size']
    early_patience = inputs['tb_batch_size']

    tensorboard_cb   = TensorBoard(log_dir='logs', batch_size= tb_batch_size, write_graph= True)
    earlystopping_cb = EarlyStopping(monitor='val_loss', verbose=1, patience=early_patience, mode='min')

    dataset = pd.read_csv('training.csv')

    processedData, processedLabel = processData(dataset)
    start_time = time.time()
    history = model.fit(processedData
                        , processedLabel
                        , validation_split=validation_data_split
                        , epochs=num_epochs
                        , batch_size=model_batch_size
                        , callbacks = [tensorboard_cb,earlystopping_cb]
                    )
    timeTaken = time.time() - start_time

    df = pd.DataFrame(history.history)
    df.plot(subplots=True, grid=True, figsize=(5,10))
    plt.savefig(testHyper+'/'+str(testHyperValue)+'/'+str(testIteration)+'_graph.png')
    if testIteration == 5:
        df = df[df.columns[~df.columns.str.contains('_')]]
        df.to_csv(testHyper+'/'+str(testHyperValue)+'/dataframe.csv')
    return model, timeTaken

def compute(inputs,model,timeTaken):
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

    accuracy = right/(right+wrong)*100

    # Please input your UBID and personNumber 
    testDataInput = testData['input'].tolist()
    testDataLabel = testData['label'].tolist()

    testDataInput.insert(0, "UBID")
    testDataLabel.insert(0, "egnanach")

    testDataInput.insert(1, "personNumber")
    testDataLabel.insert(1, "50290792")

    testDataInput.insert(2, "Accuracy")
    testDataLabel.insert(2, accuracy)

    testDataInput.insert(3, "Time")
    testDataLabel.insert(3, timeTaken)

    predictedTestLabel.insert(0, "")
    predictedTestLabel.insert(1, "")
    predictedTestLabel.insert(2, "")
    predictedTestLabel.insert(3, "")

    output = {}
    output["input"] = testDataInput
    output["label"] = testDataLabel

    output["predicted_label"] = predictedTestLabel

    opdf = pd.DataFrame(output)
    opdf.to_csv(testHyper+'/'+str(testHyperValue)+'/'+str(testIteration)+'_output.csv')

createInputCSV(101,1001,'training.csv')
createInputCSV(1,101,'testing.csv')

testcases = [{
    'testHyper': "drop_out",
    'testHyperValue': 0.1,
    'type': 'drop_out'
},
{
    'testHyper': "drop_out",
    'testHyperValue': 0.2,
    'type': 'drop_out'
},
{
    'testHyper': "drop_out",
    'testHyperValue': 0.4,
    'type': 'drop_out'
},
{
    'testHyper': "drop_out",
    'testHyperValue': 0.6,
    'type': 'drop_out'
},
{
    'testHyper': "drop_out",
    'testHyperValue': 0.8,
    'type': 'drop_out'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 1,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 128,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 256,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 512,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 1024,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 2048,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_dense_layer_nodes",
    'testHyperValue': 4096,
    'type': 'first_dense_layer_nodes'
},
{
    'testHyper': "first_activation",
    'testHyperValue': 'sigmoid',
    'type': 'first_activation'
},
{
    'testHyper': "first_activation",
    'testHyperValue': 'tanh',
    'type': 'first_activation'
},
{
    'testHyper': "first_activation",
    'testHyperValue': 'relu',
    'type': 'first_activation'
},
{
    'testHyper': "optimizer",
    'testHyperValue': 'rmsprop',
    'type': 'optimizer'
},
{
    'testHyper': "optimizer",
    'testHyperValue': 'adadelta',
    'type': 'optimizer'
},
{
    'testHyper': "optimizer",
    'testHyperValue': 'adagrad',
    'type': 'optimizer'
},
{
    'testHyper': "optimizer",
    'testHyperValue': 'adam',
    'type': 'optimizer'
},
{
    'testHyper': "optimizer",
    'testHyperValue': 'sgd',
    'type': 'optimizer'
}]

testcases = [{
    'testHyper': "optimized",
    'testHyperValue': 0.1,
    'type': 'drop_out'
}]

inputs = {
    'input_size' : 10,
    'drop_out' : 0.1,
    'first_dense_layer_nodes'  : 512,
    'second_dense_layer_nodes' : 4,
    'validation_data_split' : 0.2,
    'num_epochs' : 10000,
    'model_batch_size' : 128,
    'tb_batch_size' : 32,
    'early_patience' : 100,
    'first_activation': 'relu',
    'second_activation': 'softmax',
    'optimizer': 'adadelta'
}

print('This program will run the model for various testcases')
print('Each testcase has 10 iterations to find mean accuracy')
print('Running this will take a lot of time and space')
print('\n\n\n')
decision = input('Do you wish to proceed? (y/n)')
if(decision == 'yes' or decision == 'y' or decision == 'Y'):
    for t in testcases:
        for i in range(10):
            testHyper = t['testHyper']
            testHyperValue = str(t['testHyperValue'])
            if not os.path.exists(testHyper):
                os.makedirs(testHyper)
            if not os.path.exists(testHyper+"/"+testHyperValue):
                os.makedirs(testHyper+"/"+testHyperValue)
            testIteration = i
            inputs[t['type']] = t['testHyperValue']
            model,timeTaken = run_model(inputs)
            compute(inputs,model,timeTaken)
else:
    print('Exiting the script!')
