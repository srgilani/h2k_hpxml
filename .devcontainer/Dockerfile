# Use an official Python runtime as a parent image
FROM canmet/os_standards_devcontainer:3.7.0

# Download and install https://github.com/NREL/OpenStudio-HPXML/releases/download/v1.7.0/OpenStudio-HPXML-v1.7.0.zip
RUN curl -L -o OpenStudio-HPXML-v1.7.0.zip https://github.com/NREL/OpenStudio-HPXML/releases/download/v1.7.0/OpenStudio-HPXML-v1.7.0.zip \
    && unzip OpenStudio-HPXML-v1.7.0.zip -d / \
    && rm OpenStudio-HPXML-v1.7.0.zip \
    && chmod -R 777 /OpenStudio-HPXML


# Install Python 3.12 as per Volta Development currently. 
RUN : \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        software-properties-common \
    && add-apt-repository -y ppa:deadsnakes \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
        python3.12-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && :

RUN python3.12 -m venv /venv
ENV PATH=/venv/bin:$PATH
USER vscode

