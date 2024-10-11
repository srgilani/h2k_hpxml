# Use an official Python runtime as a parent image
FROM canmet/os_standards_devcontainer:3.7.0

# Set the working directory in the container
WORKDIR /workspace

# Install any needed packages specified in requirements.txt
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /workspace
COPY . /workspace