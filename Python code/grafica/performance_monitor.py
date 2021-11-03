# coding=utf-8
"""Simple class to monitor the frames per second of an application"""

__author__ = "Daniel Calderon"
__license__ = "MIT"

class PerformanceMonitor:
    """
    Convenience class to measure simple performance metrics
    """
    
    def __init__(self, currentTime, period):
        """
        Set the first reference time and the period of time over to compute the average frames per second
        """
        self.currentTime = currentTime
        self.timer = 0.0
        self.period = period
        self.framesCounter = 0
        self.framesPerSecond = 0.0
        self.milisecondsPerFrame = 0.0

    def update(self, currentTime):
        """
        It must be called once per frame to update the internal metrics
        """
        self.framesCounter += 1
        self.deltaTime = currentTime - self.currentTime
        self.timer += self.deltaTime
        self.currentTime = currentTime
        
        if self.timer > self.period:
            self.framesPerSecond = self.framesCounter / self.timer
            self.milisecondsPerFrame = 1000.0 * self.timer / self.framesCounter
            self.framesCounter = 0
            self.timer = 0.0

    def getDeltaTime(self):
        """
        Get the time spent since the latest update.
        """
        return self.deltaTime
        
    def getFPS(self):
        """
        Returns the latest fps measure
        """
        return self.framesPerSecond
    
    def getMS(self):
        """
        Returns the latest miliseconds per frame measure
        """
        return self.milisecondsPerFrame

    def __str__(self):
        return f" [{self.framesPerSecond:.2f} fps - {self.milisecondsPerFrame:.2f} ms]"