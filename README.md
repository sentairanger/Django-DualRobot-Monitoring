# Django-DualRobot-Monitoring

## Introduction

Much like my previous project, this is also based on what I learned from the Cloud Native Application Architecture Nanodegree but this time using Django and the `django_prometheus` library. [Here](https://github.com/korfuri/django-prometheus) you can learn more about this library as it's far different from `prometheus_flask_exporter`. Just like before I will go through the same breakdown of the project. 

## Breakdown of Project

### Code

Unlike with Flask, there are several files that need to be emphasized.

* `dualrobot/settings.py`: Here the settings are established for the application. The main focus here is that the `django_prometheus` app is added under INSTALLED APPS as that is required for prometheus to scrape metrics. Also under MIDDLEWARE, both `django_prometheus.middleware.PrometheusBeforeMiddleware` and `django_prometheus.middleware.PrometheusAfterMiddleware` are also required. Under ALLOWED HOSTS, the asterisk is added to indicate that all hosts must be allowed. Otherwise Prometheus will not be able to scrape any metrics.
* `dualrobot/urls.py`: This lists the paths that are created from the views file. In this case `django_prometheus.urls` is added so that Prometheus can detect the application. Update: This should work now with Django 4.0.
* `dualrobotapp/views.py`: The views of the application are created here. Here is where you see the robots, servo motors, and LEDs defined as well as the Jaeger client. 
* `dualrobot/manage.py`: This is required for the application to run. 

The app design is shown below. Run the app with `python manage.py runserver` or `python3 manage.py runserver` as a test. You can add `0.0.0.0:8000` to expose it publicly. Once you are sure you can now package it with docker.

* ![App Design](https://github.com/sentairanger/Django-DualRobot-Monitoring/blob/main/images/app-design.png)

### Docker

Much like my other project that uses Flask the application is then packaged into a Docker container. The `Dockerfile` provided explains each step to run the container.  These are the same steps as in the Dual Robot Monitoring Project. The rundown is exactly the same:

* FROM: This sets up what the image will be based on. In this case it's `python:3.8-slim`. I chose slim as I wanted to reduce image size and only use the required libraries. This is good practice and avoids security issues.
* LABEL: This is an optional step as it names the maintainer of the image.
* COPY: Here the files from the current directory are copied to a directory called `/app`.
* WORKDIR: Here, the working directory is set as `/app`.
* RUN: Here, a command can be run on the image. In this case we are installing the necessary libraries from `requirements.txt`.
* CMD: Here the code is run using the command listed. Remember to separate with commas and quotations.

Just like before you can build the image with `docker build -t django-dual .`. And then test with `docker run -d -p 8000:8000 django-dual`. This will run the image detached in the background at port 8000. Then access the app with `0.0.0.0:8000` and the app should display. Test things out before closing it. Then tag the image with `docker tag django-dual  <your-dockerhub-username>/django-dual:<tag>`. Again, make sure you set up an account with Dockerhub. Then make sure to login with `docker login` and then push with `docker push <your-dockerhub-username>/django-dual:<tag>`.

### Kubernetes

Just like before, after packaging with Docker, Kubernetes is used to deploy the application. And as before here is the breakdown of the `django-dual.yaml` manifest file.

* The deployment section: This holds the docker image and adds the annotations for Jaeger and Prometheus. In order for Prometheus to work the scrape option should be set to true, with the `/metrics` endpoint and port 8000. Also make sure to set sidecar injection to true for Jaeger to work.
* The service section: This sets the service port to 8000 and the type is set to LoadBalancer. This is needed to port-foward the application.
* The service monitor section: This is used to monitor the application using the `/metrics` endpoint and the interval set at 15ms.

The diagram of the project is posted below. To run the application run `kubectl apply -f django-dual.yaml` and you should see a deploy, a service and a service monitor. You can test the app with the command `kubectl port-forward svc/django-dual 8000`. Or use `8000:8000` if running inside a VagrantBox.

* ![diagram](https://github.com/sentairanger/Django-DualRobot-Monitoring/blob/main/images/django-diagram.png)

### Github Actions

Continuous Integration is the action of merging code changes into a repository. And just like in my other project I created two workflows that merge any changes to the Docker Repository. 

* `docker-build.yml` builds a new image any time there is a change in the repo.
* `docker-sha-tag.yml` creates new sha-tags for each build. This is good for security.

### ArgoCD

Aside from running the cluster directly on the machine or a VagrantBox, ArgoCD is another way to deploy it. I have provided a script to install ArgoCD either on the host or on the VagrantBox. To access the GUI, I have provided the `argocd-service-nodeport.yaml` file and the service should now be exposed. Run the application with the same command `kubectl apply -f django-dual.yaml`. Then the application should appear in the GUI and then you can sync the application. An example of a successful deployment is posted below.

* ![ArgoCD](https://github.com/sentairanger/Django-DualRobot-Monitoring/blob/main/images/argocd-deploy.png)


### Jaeger

As before, Jaeger is used to find spans that are traced any time Linus or Torvald's eyes are blinked. For this to work, the `views.py` file sets up the Jaeger client and references the `JAEGER_HOST` found in the `django-dual.yaml` file. In order to use Jaeger I have provided an `observability-jaeger.sh` script and `helm-install.sh` to get Jaeger installed. To view the spans in my case I would run `kubectl port-forward svc/my-jaeger-tracing-default-query 16686`. If using a different query make sure to reference that instead. Go to `localhost:16686` and the Jaeger UI should be posted. If using VagrantBox, make sure to change `localhost` to the IP address of the VM. Then select the service, and then click on Find traces. The spans should show up. A sample span is posted below. 

* ![Jaeger](https://github.com/sentairanger/Django-DualRobot-Monitoring/blob/main/images/jaeger-sample-span.png)

### Prometheus

Prometheus is used to scrape and collect data from the `/metrics` endpoint as done before. I have provided a `monitoring-prometheus.sh` script to install both Prometheus and Grafana. Once installed then to make sure that Prometheus is monitoring the application run the command `kubectl port-forward -n monitoring svc/prometheus-kube-prometheus-prometheus 9090` and then go to `localhost:9090` or the IP address of your VM if using Vagrantbox. Then go under Status and then Targets. There you should see your application. A screenshot of what it would look like is shown below.

* ![Prometheus](https://github.com/sentairanger/Django-DualRobot-Monitoring/blob/main/images/prometheus-monitor.png)

### Grafana

Once Prometheus collects the data, that is processed in Grafana. To go to Grafana make sure to run the command `kubectl port-forward -n monitoring svc/prometheus-grafana 3000` and then go to either `localhost:3000` or replace `localhost` with the IP of your VM if using VagrantBox. Then login with admin and then prom-operator as the password. Change that as that is not secure. To display Jaeger spans, you need to go to Data Sources and then add a data source. Prometheus is added by default so make sure to use the correct FQDN of your Jaeger host and then the port 16686. In my case that's `my-jaeger-tracing-default-query.default.svc.local:16686`. Once that's done you can go to the plus symbol and create your own dashboard. I have provided a json file so that you can use that and adjust as you wish. The Dashboard I created is posted below to get an idea of what it is. However, this time I need address a few changes. While the CPU, RAM usage, pod uptime and Jaeger Spans have not changed, there are several changes from prometheus flask. So here are the metrics I used that can help you:

* `django_http_responses_total_by_status_total`: These are the total http responses made by the user.
* `django_http_requests_total_by_method_total`: This is the count of requests by method.
* `django_http_ajax_requests_total`: This is the count of AJAX requests if using something like JQuery. And this application does use JQuery which is found in the `dualrobotapp/static` directory.

* ![Grafana](https://github.com/sentairanger/Django-DualRobot-Monitoring/blob/main/images/grafana-dashboard.png)

### Using Vagrant

If using Mac or Windows I have provided a Vagrantfile that already has k3s and Docker ready to be installed. Make sure to install Vagrant first which the instructions can be found [here](https://www.vagrantup.com/downloads).
