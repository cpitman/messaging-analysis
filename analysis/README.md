Analysis
========

Takes a data dump generated from a running messaging system and calculates metrics and distributions. For example, given an input we should generate something similar to the following:

    metrics: {
      "Message Size": {
        "Max": 102400,
        "Min": 256,
        "Avg": 5986,
        "StdDev": 1235,
        "Histogram": [
          10, 8, 4, 7, 6, 15, 20, ..., 1
        ]
      }
    }
