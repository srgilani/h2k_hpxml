# Base image compatible with the required OpenStudio version
ARG OPENSTUDIO_VERSION=3.7.0
FROM canmet/os_standards_devcontainer:${OPENSTUDIO_VERSION} as base

# Define versions for dependencies
ARG OPENSTUDIO_HPXML_VERSION=1.7.0
ARG PYTHON_VERSION=3.12
ARG H2K_HPXML_VERSION=1.7.0.1.1

# Install OpenStudio-HPXML and Python with virtual environment
RUN curl -k -L -o OpenStudio-HPXML-v${OPENSTUDIO_HPXML_VERSION}.zip https://github.com/NREL/OpenStudio-HPXML/releases/download/v${OPENSTUDIO_HPXML_VERSION}/OpenStudio-HPXML-v${OPENSTUDIO_HPXML_VERSION}.zip \
    && unzip OpenStudio-HPXML-v${OPENSTUDIO_HPXML_VERSION}.zip -d / \
    && rm OpenStudio-HPXML-v${OPENSTUDIO_HPXML_VERSION}.zip \
    && chmod -R 777 /OpenStudio-HPXML \
    && apt-get update \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends software-properties-common \
    && add-apt-repository -y ppa:deadsnakes \
    && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends python${PYTHON_VERSION}-venv \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    && python${PYTHON_VERSION} -m venv /venv

# Install H2K-HPXML and set up the environment
RUN curl -k -L -o H2K_HPXML_VERSION.zip https://github.com/canmet-energy/h2k_hpxml/archive/refs/heads/${H2K_HPXML_VERSION}.zip \
    && unzip H2K_HPXML_VERSION.zip -d /temp \
    && mv /temp/h2k_hpxml-${H2K_HPXML_VERSION} /h2k_hpxml \
    && rm H2K_HPXML_VERSION.zip \
    && chmod -R 777 /h2k_hpxml \
    && /venv/bin/pip install -r /h2k_hpxml/requirements.txt \
    && sed -i '1s/^/#!\/venv\/bin\/python\n/' /h2k_hpxml/bin/h2k2hpxml.py \
    && mkdir /shared \
    && chmod -R 777 /shared

# Create a CLI entry point
RUN echo -e '#!/bin/bash\n/h2k_hpxml/bin/h2k2hpxml.py "$@"' > /usr/bin/cli \
    && chmod +x /usr/bin/cli

# Set the virtual environment's Python as the default
ENV PATH=/venv/bin:$PATH

# Use the vscode user
USER vscode

# To run 
# docker build -t image_name .
# docker run -v //c/<path_to_your_h2k_files>:/shared image_name cli -h