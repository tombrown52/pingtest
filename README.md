# Introduction

This utility helps identify systemwide pauses. It continuously pings the loopback address (127.0.0.1) and logs the output to a file. If there is ever more than 1 second between pings, a warning is placed in the log file.

## Usage

Once installed, the service will automatically start when the machine starts. It can be manually controlled via upstart:

 start pingtest

 stop pingtest


## Building

Install python and run:

 python build/build.py

The resulting installable will be found in the dist/ folder.


## Installation

Install the package via dpkg:

 dpkg -i pingtest_1.0_all.deb
