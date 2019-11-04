import matplotlib.pyplot as plt
import os
import pandas as pd
import numpy as np
import statistics as st

testHyper = "drop_out"
testHyperValue = ["0.1","0.2","0.4","0.6","0.8"]
label = ""

print('Plotting graph for various '+testHyper+' values')

datalosses = []
dataaccs = []

for i in testHyperValue:
    dataset = pd.read_csv(testHyper+'/'+str(i)+'/dataframe.csv')
    dataset.columns = ['epoch',label+"  "+str(i),label+" "+str(i)]
    #dataset[testHyper+" "+i] = dataset.pop('acc')
    datalosses.append(dataset[label+"  "+str(i)])
    dataaccs.append(dataset[label+" "+str(i)])

dfa = pd.DataFrame(dataaccs)
dfa = dfa.T
dfa.plot(subplots=False, grid=True, figsize=(5, 5))
plt.xlabel("epochs")
plt.ylabel("accuracy")
plt.savefig(testHyper+'_accuracy_combine_graph.png')

dfl = pd.DataFrame(datalosses)
dfl = dfl.T
dfl.plot(subplots=False, grid=True, figsize=(5,5))
plt.xlabel("epochs")
plt.ylabel("loss")
plt.savefig(testHyper+'_loss_combine_graph.png')