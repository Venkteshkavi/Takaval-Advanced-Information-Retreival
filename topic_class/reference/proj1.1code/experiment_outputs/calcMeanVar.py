import pandas as pd
import os
import statistics as st

testHyper = "drop_out"
testHyperValue = ["0.1","0.2","0.4","0.6","0.8"]

print('Calculating mean and variance for various '+testHyper+' values')

for t in testHyperValue:
    accuracy = []
    for i in range(10):
        dataset = pd.read_csv(testHyper+'/'+t+'/'+str(i)+'_output.csv',skiprows=2,nrows=1)
        accuracy.append(dataset.iat[0,2])

    m = st.mean(accuracy)
    print("############")
    print("For "+testHyper+" and value "+t)
    print("Mean :"+str(m))
    print("Variance :"+str(st.variance(accuracy,m)))
    print("############")