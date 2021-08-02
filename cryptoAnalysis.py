import sys
import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import statistics
import csv
import datetime

from dataHandler import *
from dataVisualization import *
from sentimentAnalysis import *


def main():
    eth_data, btc_data, tweet_data = loadRawData()
    visualizeRawData(eth_data, btc_data, tweet_data)
    preprocessData()
    #sentimentAnalysis(elon_data)

if __name__ == '__main__':
    main()