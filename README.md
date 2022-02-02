# Description
<p>
Python Software for create XML configuration with SCPI commands. Has a console installed with it. Launch with "start_software"
</p>

### Console window
<p>Left side is the console with a input for send command. <br>
Right side, you can connect on the device which will send automatically a *idn?<br>
Below, you can modify the choice of the connection. Needed for take a another port or do a GPIB connection.<br>
The New and Edit Config button are for create/modify a XML file to put on the folder Luxondes/Config_SCPI/ of the scanphone for the compatibility with the device.
</p>
![SCPI-Command-configuration](/imgs/connect.png)

### Config window
<p>
Openable with the New & Edit Config button. Used for  made a XML file to put on the folder Luxondes/Config_SCPI/ of the scanphone for the compatibility with the device.

After have fill the command, you can test them. Some test like the Unit command will not turn green.
</p>
![SCPI-Command-configuration](/imgs/config.png)

![SCPI-Command-configuration](/imgs/test.png)

# PyInstaller

<p>
Install PyInstaller & Python then you can launch "build_executable" for have a executable without the needs of python.
</p>
