# Serial Two-Joint Robot Manipulator Simulation and Control

This project focuses on real-time control algorithms for a serial two-joint robotic manipulator, incorporating precise control strategies and simulations. Developed as a part of the *University of Novi Sad* program, this project leverages advanced mathematical modeling, control theory, and hardware implementation to explore the challenges of robot arm manipulation.

## Table of Contents
- [Motivation](#motivation)
- [Project Goals](#project-goals)
- [System Architecture](#system-architecture)
- [Control Strategies](#control-strategies)
  - [PID Control](#pid-control)
  - [PID with Fuzzy Parameter Tuning](#pid-with-fuzzy-parameter-tuning)
  - [Sliding Mode Control (SMC)](#sliding-mode-control-smc)
- [User Interface](#user-interface)
- [Hardware Implementation](#hardware-implementation)
- [Evaluation and Results](#evaluation-and-results)
- [Requirements](#requirements)
- [Future Improvements](#future-improvements)
- [Credits](#credits)

## Motivation
Robotic manipulators play a vital role in automated systems across industrial, medical, and research sectors. This project addresses the challenges in precise motion control for robotic arms, focusing on managing system nonlinearity and real-time response requirements.

## Project Goals
1. Develop an accurate mathematical model for the robot arm’s kinematics and dynamics.
2. Implement and optimize control strategies to ensure stable and efficient movement.
3. Simulate the system to test control algorithms before hardware deployment.
4. Evaluate different control strategies’ performance to determine optimal configurations.
5. Test real-time implementations on sbRIO/cRIO hardware platforms.

## System Architecture
The robotic manipulator consists of two joints with movable segments. The system is modeled mathematically to describe the kinematics, dynamics, and energy characteristics. Key stages include:
- **Mathematical Model Creation**: Formulating equations for robot arm dynamics.
- **Linearization and Discretization**: Converting the model to a manageable form for digital control.

## Control Strategies
This project explores various control techniques to enhance the arm’s movement accuracy and stability.

### PID Control
The conventional PID control was implemented to provide baseline control, with parameters tuned iteratively to achieve stability. However, due to system nonlinearities, PID control faced limitations in maintaining steady-state accuracy.

### PID with Fuzzy Parameter Tuning
To overcome PID limitations, a fuzzy controller dynamically adjusts PID parameters based on error and change in error, resulting in improved steady-state performance and robustness.

### Sliding Mode Control (SMC)
For enhanced robustness and adaptability to system uncertainties, Sliding Mode Control was introduced. SMC maintains the system’s state along a predefined “sliding surface,” making it suitable for nonlinear behavior in the manipulator.

## User Interface
A LabVIEW-based GUI was developed, featuring:
- **Manual Control**: Via front panel sliders or HID devices like joysticks.
- **Automated Path Tracking**: Predefined circular, square, and triangular paths with state machine logic and a Producer-Consumer architecture.
- **Computer Vision Mode**: A hand-tracking mode using Python’s OpenCV and MediaPipe libraries enables intuitive robot control by following the user’s hand movements.

## Hardware Implementation
The control algorithms were deployed on sbRIO and cRIO platforms, chosen for their high performance in real-time applications. First-order filters were used to reduce noise and improve signal stability.

## Evaluation and Results
The system was tested in various scenarios to assess control accuracy and reliability. While hardware tests showed limitations in accuracy, simulations confirmed the system's robustness and stability, validating the project's goals.
## Requirements
- Python 3.8
- LabVIEW 2014+
- LabVIEW Robotics module
- Libraries for python:
- OpenCV
- mediapipe
- numpy
  
## Future Improvements
Potential improvements include:
- **Enhanced Discretization**: Using Runge-Kutta methods.
- **Extended Functionalities**: Adding grippers or other manipulative features.
- **Model Predictive Control (MPC)**: For more adaptive and optimized control.
- **Advanced Fuzzy Control**: Considering all state variables to refine precision.

## Credits

This project was completed in collaboration with the following team members:

- **Šećerov Nemanja**
- **Demirović Emina**
- **Tokić Ilija**
- **Grković Dušan**


Special thanks to **Professor Dr. Željko Kanović** and **Assistants Gluhović Mihailo and Golić Anastasija** from the *University of Novi Sad*, who provided valuable guidance throughout the project.

---

This project provides a comprehensive exploration of control strategies for robotic manipulators, with practical applications for complex, real-time automation systems.
