# LtSpice Simulations for Glitchifier9000
This folder contains the files used for simulating the analog frontend of the glitcher.
All simulation were done using LTspice XVII. Other spice software might work, but this is untested.
## Adding the IRF7807 spice model
For running the simulation LTspice must know how the IRF7807 behaves. This behaviour is described in the supplied model.
There are two options for importing the model: copying the `irf7808zpbf.asy`, or autogenerate it from `irf7807zpbf.cir`
### Copying the '.asy'
Locate the symbol folder on of LTspice. On windows "C:\Users\$(YourUserName)\Documents\LTspiceXVII\lib\sym\" and copy `irf7808zpbf.asy` to here.

### Autogenerate the symbol.
Open `irf7807zpbf.cir` in LTspice, and right click on the first line (it should read`.SUBCKT irf7807zpbf 1 2 3`).
Click the option "Create Symbol".

Now there will be a prompt that ask if you want LTSpice to create a footprint with 3 ports for you. Select yes. LTspice should now open a new window, showing the component.

The model uses the following pinout:
```
* External Node Designations
* Node 1 -> Drain
* Node 2 -> Gate
* Node 3 -> Source
```
For your convenience you can swap the location of port 1 and 2, so the layout matches the pins of a conventional FET.

[Suggested layout for the ports](./readme_fig1.PNG "Title")

The resistor connecting the voltage source to the gate is to limit the current. This is to roughly simulate the limited current output of the Raspberry Pico.