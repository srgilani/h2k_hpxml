# Use os_standards image as base that is compatible with os_hpxml version used. 
ARG OPENSTUDIO_VERSION=3.7.0
FROM canmet/os_standards_devcontainer:${OPENSTUDIO_VERSION} as base
ARG OPENSTUDIO_HPXML_VERSION=1.7.0
ARG PYTHON_VERSION=3.12
ARG H2K_HPXML_VERSION=1.7.0.1
# Download and install OpenStudio-HPXML and install Python with virtual environment
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

RUN curl -k -L -o H2K_HPXML_VERSION.zip https://github.com/canmet-energy/h2k_hpxml/archive/refs/heads/${H2K_HPXML_VERSION}.zip \
    && unzip H2K_HPXML_VERSION.zip -d /temp \
    && mv /temp/h2k_hpxml-${H2K_HPXML_VERSION} /h2k_hpxml \
    && rm H2K_HPXML_VERSION.zip \
    && chmod -R 777 /h2k_hpxml \
    && /venv/bin/pip install -r /h2k_hpxml/requirements.txt \
    && sed -i '1s/^/#!\/venv\/bin\/python\n/' /h2k_hpxml/bin/h2k2hpxml.py \
    && mkdir /host_dir \
    && chmod -R 777 /host_dir
RUN echo -e '#!/bin/bash\n/h2k_hpxml/bin/h2k2hpxml.py "$@"' > /usr/bin/cli \
    && chmod +x /usr/bin/cli

# To run 
# docker run -v //c/<path_to_your_h2k_files>:/host image_name /h2k_hpxml/bin/h2k2hpxml.py

# Set it to be the default python
ENV PATH=/venv/bin:$PATH
USER vscode