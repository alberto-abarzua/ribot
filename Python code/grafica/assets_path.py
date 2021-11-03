# coding=utf-8
"""Convenience functionality to access assets files"""

import os.path

__author__ = "Daniel Calderon"
__license__ = "MIT"


def getAssetPath(filename):
    """Convenience function to access assets files regardless from where you run the example script."""

    thisFilePath = os.path.abspath(__file__)
    thisFolderPath = os.path.dirname(thisFilePath)
    parentFolderPath = os.path.dirname(thisFolderPath)
    assetsDirectory = os.path.join(parentFolderPath, "assets")
    requestedPath = os.path.join(assetsDirectory, filename)
    return requestedPath
