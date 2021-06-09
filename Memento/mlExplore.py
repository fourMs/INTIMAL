import socket
import select
import struct
import time

import numpy as np
import matplotlib.pyplot as plt

from collections import deque

# Function for connecting to socket
def socketUDP(): 
    # Three ways of connecting:
    
    #If gethostbyname throws an error, comment out that line and use the one belove instead
    #UDP_IP = "192.168.100.6" #"put your IP adress here"

    # can use gethostbyname, but this does not work on all platforms
    #UDP_IP = socket.gethostbyname(socket.gethostname())

    # This way of connecting seem to work the most consistently, but if that fails
    # try uncommenting the line above containing gethistbyname
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 1))
    UDP_IP = s.getsockname()[0]
    
    print("\nComputer name is :", socket.gethostname())
    print("Receiver IP: ", UDP_IP)
    UDP_PORT = 6000
    float(UDP_PORT)
    print("Port: ", UDP_PORT)   
    sock = socket.socket(socket.AF_INET, # Internet
                        socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))
    return sock 

#Remove data from the socketbuffer
def empty_socket(sock):
    input = [sock]
    while 1:
        inputready, o, e = select.select(input,[],[], 0.0)
        if len(inputready)==0: break
        for s in inputready: s.recv(1)

# Plots the datastream along with thresholds
# x is xcoordinates
# y, line, ymin and ymax must be iterables
def stream_plotter(x, y, line,
                   ymin, ymax,
                   labels,
                   title='', pause=0.01):
    if line[0]==[]:
        plt.ion()
        fig = plt.figure(figsize=(10,7))
        plt.title('Title: {}'.format(title))
        plt.axis('off')
        ax = deque()
        for i in range(len(y)):
            position = len(y) * 50 + 21 + i
            ax.append(fig.add_subplot(position))
            line[i] = ax[i].plot(x, y[i], 'r-', alpha=0.8)
            ax[i].hlines([ymin[i], ymax[i]], x[0], x[-1], 'r', 'dashed')
            plt.ylabel(labels[i])
            plt.ylim([-0.1, ymax[i] * 2])
            plt.tight_layout()
            plt.show()
    for i in range(len(y)):
        line[i][0].set_ydata(y[i])
    plt.pause(pause)
    return line

# Lowpass filter. It removes low frequencies from signal
# params:
# x: current signal
# py: previous signal after pass
# returns: 
# y: current signal after pass
def lowPassFilter(x, py, dt, f):#alpha = 0.5):
    alpha = (2 * np.pi * dt * f) / (2 * np.pi * dt * f + 1)
    y = py + alpha * (x - py) 
    return y

# Highpass filter. Removes high frequencies from signal
# params:
# x: current rawsignal
# px: previous rawsignal
# py: previous signal after pass
# returns: 
# y: current signal after pass
def highPassFilter(x, px, py, dt, f):#alpha = 0.5):
    alpha = 1 / (2 * np.pi * dt * f + 1)
    y = alpha * (py + x - px)
    return y    

# The class FeatureBox is responsible for interpreting movement information
# sent from the phone. The file mlExploreSettings.txt contains thresholds
# for what counts as steps and rotations, and FeattureBox decides what counts
# as steps and rotations.
class FeatureBox:
    # readLimits is a method for importing thresholds used for deciding
    # what is a step or rotation
    def readLimits(self, fileName = "./mlExploreSettings.txt"):
        try:
            f = open(fileName)
            stats = [[float(a) for a in line.split()[1:]] for line in f if not line[0] == '#']
        finally:
            f.close()
        return stats[0], stats[1], stats[2]

    # Constructor
    def __init__(self, size = 200):
        self.mins, self.maxs, rotLimits = self.readLimits()
        self.rotLimitLeft = rotLimits[0]
        self.rotLimitRight = rotLimits[1]
        
        # Labels for each data point
        self.labels = ['Accel', 'Jerk',
                       'Area', 'Rotation']

        self.size = size
        self.x = range(size) # data point number, 0 is observation number 0 and so on
        self.dPoints = len(self.labels)
                
        # For figuring update rate
        self.thisTime = time.time()
        self.prevTime = self.thisTime
        self.currMagAcc = 0
        
        # hist is the data history
        self.initiateHist()
    
        # Initialize variables
        self.setToZero()
        
        # graph is the evolving plot
        self.graphs = [[] for i in range(self.dPoints)]


    # method for initiating history. used several times to clear old data
    def initiateHist(self):
        self.hist = [deque([0] * self.size) for i in range(self.dPoints)]
        self.initiateRotHist()

    def initiateRotHist(self):
        self.rotYZHist = deque([0] * 30)
        
    def setToZero(self):
        self.a = np.zeros(3)
        self.v = self.a.copy()
        self.j = self.a.copy()
        self.smoothA = self.a.copy()
        self.pSmoothA = self.a.copy()
        self.smoothJ = self.a.copy()
        self.pSmoothJ = self.a.copy()
        self.rot = self.a.copy()
        self.smoothRot = self.a.copy()
        
    # Updates the data, the update is saved in hist"
    def update(self, data):
        # Timedelta dt, used to find the time difference between loop cycles
        # returns difference in time given in seconds
        self.prevTime = self.thisTime
        self.thisTime = time.time()
        dt = self.thisTime - self.prevTime
        
        # This is the raw data
        self.pa = self.a
        self.a = np.array([float('%3.6f' %struct.unpack_from('!f', data, 4 * i)) for i in range(3)])
        self.pRot = self.rot
        self.rot = np.array([float('%3.6f' %struct.unpack_from('!f', data, 4 * i + 24)) for i in range(3)])
        self.rot[0] = 0; self.rot[2] = 0 # Set X and Z rotation to zero
        
        # Extract new features
        # Acceleration magnitude
        self.aMag = np.array([np.sqrt(np.sum([ai**2 for ai in self.a]))])
        
        # rotation magnitude
        self.rotMag = np.array([np.sqrt(np.sum([roti**2 for roti in self.rot]))])
        
        # Jerk
        self.j = (self.a - self.pa) / dt
        # Jerk magnitude
        self.jMag = np.array([np.sqrt(np.sum([ji**2 for ji in self.j]))])
        
        # Acceleration area:
        self.aArea = np.array([np.sum(self.a)])

        # Frequency of data sampling
        freq = 1 / dt
        
        #Smoothed Acceleration
        self.ppSmoothA = self.pSmoothA
        self.pSmoothA = self.smoothA

        # Highpass filter. Lets higher frequencies pass
        self.smoothA = highPassFilter(self.a, self.pa, self.smoothA, dt, f = 10**5 * freq )
        # Lowpass filter. Lets lower frequencies pass
        self.smoothA = lowPassFilter(self.a, self.smoothA, dt, f = 10**6 * freq )
        self.smoothA = (self.smoothA + 2 * self.pSmoothA + 3 * self.ppSmoothA) / 6
        
        self.smoothAMag = np.array([np.sqrt(np.sum(self.smoothA**2))])
        
        
        # smooth Jerk
        self.ppSmoothJ = self.pSmoothJ
        self.pSmoothJ = self.smoothJ
        self.smoothJ = (self.smoothA - self.pSmoothA) / dt
        self.smoothJ = (self.smoothJ + 2 * self.pSmoothJ + 3 * self.ppSmoothJ) / 6
        # smooth Jerk magnitude
        self.smoothJMag = np.array([np.sqrt(np.sum([ji**2 for ji in self.j]))])
        
        # smooth Acceleration area:
        self.pSmoothAArea = np.array([np.sum(self.pSmoothA)])
        self.smoothAArea = np.array([np.sum(self.smoothA)])
        self.smoothAArea = (self.smoothAArea - self.pSmoothAArea)**2
        
        # smooth rotation
        self.smoothRot = highPassFilter(self.rot, self.pRot, self.smoothRot, dt, f = 1 * freq )
        self.smoothRot = lowPassFilter(self.rot, self.smoothRot, dt, f = 1 * freq )
        
        self.smoothRotMag = np.array([np.sqrt(np.sum(self.smoothRot**2))])
        
        # Update history
        now = np.concatenate([self.smoothAMag, self.smoothJMag,
                              self.smoothAArea, self.smoothRotMag])
        for h, ai in zip(self.hist, now):
            h.popleft()
            h.append(ai)
        self.rotYZHist.popleft()
        self.rotYZHist.append(self.rot[1])# + self.rot[2])

    # Method to plot the data
    def plot(self, title = 'Graph'):
        self.graphs = stream_plotter(self.x, self.hist, self.graphs, self.mins, self.maxs,
                                     self.labels, title=title)

    # Boolean Method to check for steps, returns true if step is detected
    def detectStep(self):
        # get the last three datapoints
        data = np.array([[point[-1], point[-2], point[-3]] for point in self.hist])
        # Check to see if there is a maximum in acceleration
        top = data[0][1] > data[0][0] and data[0][1] > data[0][2]
        # Check to see if there are any maximums:
        # If there are a maximum check the limits
        limit = 0
        if top:
            limit = sum([stat[1] >= mini and stat[1] <= maxi for stat, mini, maxi in zip(data, self.mins, self.maxs)])

        step = limit == len(data)
        #if step:
            #self.initiateHist()
            #self.setToZero()
        return step

    # Boolean method to detect left rotation
    def detectRotLeft(self):
        rotLeft = np.sum(self.rot) >= self.rotLimitLeft
        if rotLeft:
            self.initiateRotHist()
        #    self.setToZero()
        return rotLeft

    # Boolean method to detect right rotation
    def detectRotRight(self):
        rotRight = np.sum(self.rot) <= self.rotLimitRight
        if rotRight:
            self.initiateRotHist()
        #    self.setToZero()
        return rotRight

    # Returns the acceleration data history
    def getFeatures(self):
        return self.hist

    # Returns the number of different features in the model
    def getNumFeatures(self):
        return self.dPoints

def main():
    try:
        # Set up UDP
        sock = socketUDP()
        dataStream = FeatureBox()
        
        # pData is previous data initialized.
        # Used to determine if new data is different to previous data
        pData = ''

        # count steps taken:
        steps = 0
        left = 0
        right = 0
        while True:
            # collect data:
            data = sock.recv(2048)

            # Check to see if collected data is different to previous data
            # And will restart loop to collect new data without
            # executing the rest of the loop
            if data == pData:
                continue
            # If the new data is novel continue with operations
            pData = data

            dataStream.update(data)
            dataStream.plot()
            
            steps += dataStream.detectStep()
            left += dataStream.detectRotLeft()
            right += dataStream.detectRotRight()
            print("Steps: ", steps, " Left: ", left, " Right: ", right, end = '\r')
    finally:
        empty_socket(sock)

if __name__ == "__main__":
    main()
    
