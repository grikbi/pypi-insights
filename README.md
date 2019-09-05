# pypi-insights
This repository contains the code for the model that serves the companion recommendations for Python ecosystem.
It also requires graph services `gremlin-http` to work in tandem with pypi-insights to provide end-users a companion recommendation with a specific version.

### Data set

- It consists of trained model comprising of 19k unique packages and around 75k user-item matrix known as a stack in developer's parlance.
- Graph data consists of a subset of packages based on the manifests found under [this organization](https://github.com/fabric8-analytics). 

### Run this locally via container

- cd to root directory
- docker-compose up -d
- Acces the service at `http://localhost:6006`

### Swagger
Swagger is available at `/docs` and redoc is available at `/redoc` endpoint.

### Run the tests locally
- cd to root directory
- sh runtest.sh
