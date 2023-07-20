<br/>
<p align="center">
  <h3 align="center">Plate_Recognition_System</h3>
</p>

![Contributors](https://img.shields.io/github/contributors/NickLin910221/Plate_Recognition?color=dark-green) ![Stargazers](https://img.shields.io/github/stars/NickLin910221/Plate_Recognition?style=social) ![Issues](https://img.shields.io/github/issues/NickLin910221/Plate_Recognition) ![License](https://img.shields.io/github/license/NickLin910221/Plate_Recognition) 

## Table Of Contents

* [About the Project](#about-the-project)
* [Built With](#built-with)
* [Getting Started](#getting-started)
  * [Prerequisites](#prerequisites)
  * [Installation](#installation)
* [Authors](#authors)
* [Acknowledgements](#acknowledgements)

## About The Project

This system aims to detect plate with custom environment. It can be compatible with the IP Camera of the RTSP protocol. This system uses Docker to execute the work of deployment. So follow the tutorial step it can build and run on your machine automatically. 

## Built With

Database : MySQL
Backend : Django
Plate_Detection : Yolov5, Yolov7
IPCam_Controller : Python

## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

This is an example of how to list things you need to use the software and how to install them.

* Docker
* Docker-Compose

```sh
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

### Installation

1. Clone the repo

```sh
git clone https://github.com/NickLin910221/Plate_Recognition.git
```

2. Cd into directory

```sh
cd Plate_Recognition
```

3. Build the system with docker-compose automatically (If you have the permission problem, add "sudo" at the top of the command.)

```sh
docker-compose up -d
```

4. Visit the home page of the system. (Change "localhost" to your target IP address)

[https://localhost/home](https://localhost/home)

5. If you adjusted the IPCam setting, please run the script to reset the IPCam fetching system.

```sh
bash update_IPCam.sh
```

## Authors

* **You-rui, Lin** - *National University Of Tainan* - [You-rui, Lin](https://github.com/NickLin910221/) - *Whole Project*

## Acknowledgements

* [陳宗禧](https://home.nutn.edu.tw/chents/index-c.html)
