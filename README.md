# Cortical Excitability During Motor Imagery - Barr 2022

This repository contains the experiment code for a study looking at whether cortical excitability during motor imagery depends on the motoric complexity of the imagined movement.

This study uses two different tasks: 1) a modified version of the TraceLab task from [Ingram et al. (2018)](https://doi.org/10.1016/j.bbr.2018.10.030), and 2) a modified version of the Motor Imagery Implicit Sequence Learning (MIISL) task from [Kraeutner et al. ](https://dx.doi.org/10.1037/xhp0000148), both of which have been modified to deliver TMS pulses at 120% of participants' resting motor threshold on a random subset of trials. EMG data is recorded during each task to collect the motor-evoked potentials (MEPs) resulting from each pulse, giving a measure of cortical excitability for each task.

More information on the TraceLab task and how it works can be found in the [main TraceLab repository](https://github.com/LBRF/TraceLab).


## Requirements

This study requires the following hardware to work as intended:

* A computer with Python 3.7 or later installed
* A touchscreen monitor (we used a 24" Planar PCT2485)
* A Magstim TMS stimulator connected to the experiment computer via serial port (we used a BiStim, but a 200 should also work)
* A LabJack U3 wired to the firing trigger on the MagStim (code can be modified to use a parallel port or similar TTL device instead).

The experiment programs configure, arm, and disarm the TMS hardware remotely throughout the tasks via the serial port, while the LabJack triggers the TMS to fire at specific points during motor imagery trials (and also sends marker codes to an external EMG device).

If you do not have access to any this equipment, both tasks are programmed so that they can be tested for demo purposes without any special hardware.


## Getting Started

The TraceLab task is written in Python 3 (3.7+ compatible) using the [KLibs framework](https://github.com/a-hurst/klibs). The MIISL task is written in Python 3 using PySDL2. Both should install and run on any recent version of macOS, Linux, or Windows.

If using a LabJack U3 for TMS firing and EMG markup, you will also need to install the correct LabJack hardware driver for your OS in order to use it (the [Exodriver](https://labjack.com/pages/support?doc=/software-driver/installer-downloads/exodriver/) for macOS and Linux, or the [UD Library](https://labjack.com/pages/support?doc=/software-driver/ud-library/) for Windows).


### Installing Dependencies

#### Option 1: Pipenv Installation

To install all of the tasks' Python dependencies in a self-contained virtual environment, run the following commands in a terminal window inside the same folder as this README:

```bash
pip install pipenv
pipenv install
```
These commands should create a fresh environment for both tasks with all their dependencies installed inside it. Note that to run commands using this environment, you will need to prefix them with `pipenv run` (e.g. `pipenv run klibs run 24`, `pipenv run python missl.py`).

#### Option 2: Global Installation

Alternatively, to install the dependencies for the tasks in your global Python environment, run the following commands in a terminal window:

```bash
pip install https://github.com/a-hurst/klibs/releases/latest/download/klibs.tar.gz
pip install pyyaml
pip install MagPy-TMS==1.4
pip install LabJackPython
```

### Running TraceLab

TraceLab is a KLibs experiment, meaning that it is run using the `klibs` command at the terminal (running the 'experiment.py' file using `python` directly will not work, and will print a warning).

To run the experiment, navigate to the TraceLab folder in a terminal and run `klibs run [screensize]`,
replacing `[screensize]` with the diagonal size of your display in inches (e.g. `klibs run 24` for a 24-inch monitor). If you just want to test the program out for yourself and skip demographics collection, you can add the `-d` flag to the end of the command to launch the experiment in development mode.


### Running the MIISL

The MIISL task is programmed in Python using PySDL2, and can be run by nagivating to the MIISL folder in a terminal and running `python miisl.py` (or `pipenv run python miisl.py` if using pipenv).
