*** Settings ***


*** Test Cases ***
test 123
    Log To Console    Hello
    Run Keyword And Ignore Error    A keyword That Fails
    Log   this is Skipped
    Log    This Too
    [Teardown]      Another Keyword that fails


*** Keywords ***
A Keyword That Fails
    Fail    expected

Another Keyword that fails
    Log To Console    This is Executed
    Fail    again
    Log To Console    This is also Executed
