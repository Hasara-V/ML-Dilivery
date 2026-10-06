# 1. Start from an official Python image
FROM python:3.12-slim

# 2. Set the working folder inside the image
WORKDIR /app

# 3. Copy requirements first, then install packages
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copy the source code
COPY train.py app.py ./

# 5. BUILD TIME: train the model and save iris_model.joblib into the image
RUN python train.py

# 6. Document the port the app uses
EXPOSE 5000

# 7. RUN TIME: start the app when a container starts
CMD ["python", "app.py"]
