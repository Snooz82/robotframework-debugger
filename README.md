# robotframework-debugger
Debugger that can stop execution and shows a Gui to try out Robot Framework commands

## Installation

``pip install robotframework-debugger``

## Usage

use it as listener

``robot --listener Debugger myrobotsuite.robot``  

## How it works:

Debugger pauses the execution on a failing keyword or on keywords named `Debug` or `Break`.
It opens a TKinter based GUI and let you see the error, try out other keywords in exact that situation.
It also gives access to Robot Frameworks variables and logs a history of passed keyword calles.

### Have Fun