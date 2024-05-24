<p align="center">
  <a href="https://example.com/">
    <!-- <img src="https://via.placeholder.com/72" alt="Logo" width=72 height=72> -->
    <img src="./banner.jpg" alt="EYMO banner" width="400" height="200">
  </a>

  <h3 align="center">EYMO</h3>

  <p align="center">
    A compact robotic companion blending machine learning and generative AI to create personalized and interactive experiences.
    <br>
    <a href="https://github.com/xavi-burgos99/eymo/issues/new?template=bug.md">Report bug</a>
    ·
    <a href="https://github.com/xavi-burgos99/eymo/issues/new?template=feature.md&labels=feature">Request feature</a>
  </p>
</p>


## Table of contents

- [Table of contents](#table-of-contents)
- [Introduction](#introduction)
- [Installation](#installation)
   - [Cloud](#cloud)
   - [Physic Robot](#physic-robot)
- [What's included](#whats-included)
- [To Do](#to-do)
- [Bugs and feature requests](#bugs-and-feature-requests)
- [Contributing](#contributing)
- [Creators](#creators)
- [Acknowledgement](#acknowledgement)
- [References](#references)
- [License](#license)


## Introduction

Eymo is a compact robotic companion blending machine learning and generative AI to create personalized and interactive experiences. It learns from its interactions, offering customized conversations, entertainment, and learning opportunities. Eymo is the perfect blend of technology and companionship, making every moment more engaging and enjoyable.


## Installation

### Cloud

### Physic Robot

1. Clone the repo, install the dependencies and run the main file:

```bash
pip install -r requirements.txt
cd src/rpi
python main.py
```
The main file will start the robot and the cloud connection. The robot will be able to receive commands from the cloud and execute them. The robot will also be able to send information to the cloud.

## What's included

Within the download you'll find the following directories and files, logically grouping common assets and providing both compiled and minified variations. You'll see something like this:

```text
src/
├── rpi/
│    ├── graphics/
│    ├── mechanics/ 
│    ├── controllers/
│    ├── ...
│    └── main.py     
├── arduino/
│   ├── movements/
│   ├── sensors/
│   ├── ...
│   └── main.ino
└── cloud/
    ├── actions/
    ├── externals/
    │   ├── class/
    │   ├── functions/
    │   └── ...
    ├── resources/
    ├── ...
    └── main.py 
LICENSE.md
README.md
```

## Bugs and feature requests

Have a bug or a feature request? Please first read the ~~[issue guidelines](https://github.com/xavi-burgos99/eymo/blob/main/CONTRIBUTING.md)~~ and search for existing and closed issues. If your problem or idea is not addressed yet, [please open a new issue](https://github.com/xavi-burgos99/eymo/issues/new).

## Contributing

Please read through our ~~[contributing guidelines](https://reponame/blob/master/CONTRIBUTING.md)~~. Included are directions for opening issues, coding standards, and notes on development.

## Creators

1. **Xavier Burgos**
   - Website: <https://xburgos.es/>
   - GitHub: <https://github.com/xavi-burgos99/>
   - LinkedIn: <https://linkedin.com/in/xavi-burgos/>

2. **Yeray Cordero**
   - GitHub: <https://github.com/yeray142/>
   - LinkedIn: <https://linkedin.com/in/yeray142/>

3. **Javier Esmorris**
   - GitHub: <https://github.com/jaesmoris/>
   - LinkedIn: <https://www.linkedin.com/in/javier-esmoris-cerezuela-50840b253/>

4. **Gabriel Juan**
   - GitHub: <https://github.com/GabrielJuan349/>
   - LinkedIn: <https://linkedin.com/in/gabi-juan/>

5. **Samya Karzazi**
   - GitHub: <https://github.com/SamyaKarzaziElBachiri>
   - LinkedIn: <https://linkedin.com/in/samya-k-2ba678235/>


## Acknowledgement

This project has been made for the RLP (Robotics, Language and Planning) subject of the Computer Engineering degree at the [UAB (Universitat Autònoma de Barcelona)](https://www.uab.cat/). We would like to thank our teacher [Fernando Vilariño](https://linkedin.com/in/fernandovilarino) for his support and guidance throughout the project.

The Cloud project was built for the MS (Multimedia Systems) subject in the Computer Engineering degree at [UAB (Universitat Autònoma de Barcelona)](https://www.uab.cat/). We want to express our gratitude to our teacher [Jordi Serra](https://www.linkedin.com/in/jordiserraruiz/) for his assistance and support during this project in GCP (Google Cloud Platform).

## References

## License

Code and documentation copyright 2024 EYMO. Code released under the [MIT License](https://reponame/blob/master/LICENSE).
