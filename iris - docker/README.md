# LB2214 Week 13: package an ML prediction service

**Goal:** package a machine learning prediction application in a Docker image so another group can run it and request a prediction.

## Reference materials

Use these official pages when you need help. Read the sections relevant to your current problem.

| If you need to understand... | Read... |
| --- | --- |
| Dockerfile instructions such as `FROM`, `WORKDIR`, `COPY`, `RUN`, `EXPOSE`, and `CMD` | [Docker: Writing a Dockerfile](https://docs.docker.com/get-started/docker-concepts/building-images/writing-a-dockerfile/) and [Dockerfile reference](https://docs.docker.com/reference/dockerfile/) |
| How an image is built and tagged | [Docker: Build, tag, and publish an image](https://docs.docker.com/get-started/docker-concepts/building-images/build-tag-and-publish-an-image/) (use the build/tag sections; publishing is not required today) |
| How Flask routes and JSON responses work | [Flask Quickstart](https://flask.palletsprojects.com/en/stable/quickstart/) |
| The four Iris measurements and dataset | [scikit-learn: load_iris](https://scikit-learn.org/stable/modules/generated/sklearn.datasets.load_iris.html) |
| Why the application saves and loads a model | [scikit-learn: Model persistence](https://scikit-learn.org/stable/model_persistence.html) |
| How to inspect a failed or stopped container | [Docker: Container logs](https://docs.docker.com/reference/cli/docker/container/logs/) |

## Tasks

| Your work | Checkpoint |
| --- | --- |
| Read `train.py`, `app.py`, and `requirements.txt`. Draw the route from input JSON to prediction. | Point to the saved model, HTTP endpoint, and response. |
| Create a `Dockerfile` that copies dependencies and source, installs packages, runs `train.py` **while building**, and starts `app.py` **when the container starts**. | Show the Dockerfile and explain build time versus run time. |
| Build and run the container. Read build output and diagnose errors yourselves. | Show `docker ps` and the response at `http://localhost:5000/`. |
| Send one valid and one invalid prediction request. Explain status codes and response JSON. | Show both terminal outputs. |
| Change the home message in `app.py`, rebuild with a new tag, and run the updated image. | Explain why rebuilding is necessary. |
| Exchange your Dockerfile and commands with another group. Can they reproduce your result? Help them diagnose one issue using `docker logs`. | Record the issue and fix. |
| Submit the evidence below. | |

## Dockerfile clues (write it yourselves)

Use an official Python image; set `/app` as the working directory. Copy and install `requirements.txt`, then copy `train.py` and `app.py`. Run `python train.py` as a **build step**. Make `python app.py` the **startup command**. The application listens on container port 5000. A model file created during the build will remain in the image. Use Docker's official Dockerfile documentation if you need to look up instructions. Be ready to explain every line you wrote.

## Commands to try after writing the Dockerfile

```bash
docker build -t iris-predict:v1 .
docker run -d --name iris-lab -p 5000:5000 iris-predict:v1
docker ps
docker logs iris-lab
curl http://localhost:5000/
curl -i -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{"measurements":[5.1,3.5,1.4,0.2]}'
curl -i -X POST http://localhost:5000/predict -H 'Content-Type: application/json' -d '{"measurements":[5.1,3.5]}'
```

For the second image, stop and remove the old container first, edit the home message, then build `iris-predict:v2` and run a new container. If port 5000 is busy, use a different **host** port such as `-p 5001:5000` and use `localhost:5001` in requests. On Windows, run the `curl` commands in Git Bash or use `curl.exe` in PowerShell.

## Expected working results

- The image builds successfully and `docker images` shows `iris-predict`.
- `docker ps` shows a running container with host port 5000 connected to container port 5000 (or your alternative host port).
- `GET /` returns JSON describing the service.
- A valid `POST /predict` with `[5.1,3.5,1.4,0.2]` returns HTTP **200** and `{"prediction":"setosa"}`.
- A request containing only two measurements returns HTTP **400** and an error message.
- After changing the home message, rebuilding as `iris-predict:v2` changes the response from the new container. The original v1 image remains unchanged.

## Submit one result per group

1. Your `Dockerfile` and any code you changed.
2. A screenshot or copied output of `docker images` and `docker ps`.
3. The valid and invalid requests with their response bodies and HTTP status codes.
4. A labelled diagram showing input JSON, the app, the saved model, and the prediction response; plus one paragraph explaining what is stored in the image, what happens when a container starts, and why a code change requires a rebuild.
5. One problem your group diagnosed and how you found the cause.

## Cleanup

```bash
docker stop iris-lab
docker rm iris-lab
```

If you created another container for v2, stop and remove that one too. Do not delete images until you have shown your evidence.

## When something does not work

1. If `docker build` fails, read the **first meaningful error** in its output and check the Dockerfile line being executed.
2. If the build succeeds but the application does not respond, check `docker ps -a` and `docker logs iris-lab`. The model must exist before `app.py` starts.
3. If the name `iris-lab` is already in use, stop and remove the old container before using that name again.
4. If port 5000 is already in use, change only the host side of the mapping to `-p 5001:5000`, then request `localhost:5001`.
5. If a POST returns HTTP 400, check that the JSON key is `measurements` and that its list contains **four numbers**.
