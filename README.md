# robotframework-debugger
Debugger that can stop execution and shows a Gui to try out Robot Framework commands

## Installation

``pip install robotframework-debugger``

## Usage

use it as listener

``robot --listener Debugger myrobotsuite.robot``  

## RF 3.2 and HTML 

from Robot Framework Version 3.2a1 it is possible to have rendered Keyword Documentation in Debugger.
If you install robotframework-debugger after you installed robotframework >= 3.2a, it is automatically active.
If you installed it before, just do ``pip install tkinterhtml`` to enable rich text docs.
