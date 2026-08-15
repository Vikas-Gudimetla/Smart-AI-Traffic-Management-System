# Smart AI Traffic Management System

An AI-powered traffic management system developed for **Smart India Hackathon 2025 (SIH)** to address urban traffic congestion through computer vision and reinforcement learning.

## Smart India Hackathon 2025

* **Problem Statement ID:** SIH25050
* **Problem Statement:** Smart AI Traffic Management System for Urban Congestion
* **Theme:** Transportation & Logistics
* **Category:** Software
* **Team Name:** ApexCoders
* **Team ID:** 76169
* **Idea:** Adaptive Flow: Reinventing the Traffic Light

## 📌 Project Overview

The system combines **YOLO-based computer vision** with **reinforcement learning** to monitor traffic conditions and optimize traffic signal control.

The computer vision component detects and tracks vehicles from traffic video, while the reinforcement learning component uses traffic-state information to learn adaptive traffic-light phase selection in a SUMO simulation environment.

## 🧠 Key Components

### 1. Computer Vision

The vehicle detection and tracking module uses:

* YOLO
* OpenCV
* Object tracking
* Vehicle counting
* Vehicle classification

The system tracks:

* Cars
* Motorcycles
* Buses
* Trucks
* Autos
* Rickshaws

Detected vehicles are assigned tracking IDs and displayed with bounding boxes and centroids.

### 2. Reinforcement Learning

The traffic signal optimization module uses **Q-learning** with SUMO.

The RL agent:

1. Observes traffic conditions from controlled lanes.
2. Calculates the number of halted vehicles.
3. Selects a traffic-light phase.
4. Receives a reward based on traffic waiting time.
5. Updates its Q-table.
6. Repeats the process to improve signal control.

The reward is based on negative total waiting time, so lower traffic waiting time produces a better reward.

### 3. Backend

The backend is implemented using:

* Flask
* Flask-SocketIO
* OpenCV
* YOLO

It provides:

* Traffic monitoring
* Real-time traffic data
* Video-frame streaming
* REST API endpoints
* Start/stop monitoring controls
* Real-time browser updates through Socket.IO

### 4. Traffic Simulation

The reinforcement learning component communicates with **SUMO through TraCI** to simulate traffic and control traffic-light phases.

## System Architecture

```text
             Traffic Video / Camera
                       │
                       ▼
              ┌─────────────────┐
              │   YOLO + OpenCV │
              │ Vehicle Detection│
              │   & Tracking     │
              └────────┬────────┘
                       │
                       ▼
              Traffic Information
                       │
             ┌─────────┴─────────┐
             │                   │
             ▼                   ▼
      Flask Backend         RL Controller
             │                   │
             ▼                   ▼
       Socket.IO/API       SUMO + TraCI
             │                   │
             ▼                   ▼
         Dashboard        Adaptive Signal
```

## 📊 Evaluation

The reinforcement learning system was evaluated against a fixed-signal baseline using total waiting time as the reward metric.

The generated results include multiple RL reward curves compared against a fixed baseline.

The repository also contains vehicle-tracking outputs showing detected vehicles, tracking IDs and vehicle counts.

## Results

### Vehicle Detection and Tracking

The computer vision component successfully demonstrates vehicle detection and tracking with bounding boxes, tracking IDs and total vehicle counts.

### Reinforcement Learning

The RL experiments compare learned traffic-signal control against a fixed-signal baseline using negative waiting time as the reward.

## 🛠️ Technologies

| Component               | Technology     |
| ----------------------- | -------------- |
| Programming             | Python         |
| Computer Vision         | YOLO, OpenCV   |
| Reinforcement Learning  | Q-learning     |
| Traffic Simulation      | SUMO, TraCI    |
| Backend                 | Flask          |
| Real-time Communication | Flask-SocketIO |
| Visualization           | Matplotlib     |

## 📁 Project Structure

```text
Smart-AI-Traffic-Management-System/
│
├── README.md
├── requirements.txt
│
├── backend/
│   └── app.py
│
├── computer_vision/
│   └── vehicle_tracking.py
│
├── reinforcement_learning/
│   └── rl_agent.py
│
└── results/
```

## Current Implementation

This repository contains the implemented computer-vision, reinforcement-learning, SUMO simulation and Flask backend components available from the project.

The original SIH proposal also described Kafka, SQL and a web dashboard as part of the broader system architecture. Those components are **not included in this repository unless their implementation is added separately**.

## Project Goals

* Reduce vehicle waiting time at intersections
* Adapt traffic-light phases according to traffic conditions
* Detect and monitor vehicles automatically
* Evaluate adaptive traffic control using simulation
* Provide real-time traffic monitoring capabilities

## Team

**ApexCoders — Smart India Hackathon 2025**

Team ID: **76169**

This project was developed collaboratively as part of Smart India Hackathon 2025.

## 📄 SIH Documentation

The project documentation contains the original problem statement, proposed solution, technical approach, feasibility analysis, impact and references.

## ⚠️ Note

This repository represents the project implementation and experimental work available from the team. Performance figures presented in the original SIH proposal should not be interpreted as measured results unless supported by corresponding experiments in this repository.
