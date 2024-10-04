# Use the official CUDA development image as the base image
FROM nvidia/cuda:12.1.0-devel-ubuntu20.04

# Install necessary dependencies
RUN apt-get update && apt-get install -y \
    wget \
    bzip2 \
    ca-certificates \
    curl \
    git \
    build-essential \
    python3-pip \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    -O /tmp/miniconda.sh && \
    /bin/bash /tmp/miniconda.sh -b -p $CONDA_DIR && \
    rm /tmp/miniconda.sh && \
    conda clean -a -y

# Update conda
RUN conda update -n base -c defaults conda -y

# Create a new conda environment with Python 3.10.15 from conda-forge
RUN conda create -n myenv -c conda-forge python=3.10.15 -y

# Install Poetry in the conda environment
RUN /bin/bash -c "source $CONDA_DIR/etc/profile.d/conda.sh && \
    conda activate myenv && \
    pip install poetry"

# Set the working directory
WORKDIR /app

# Copy pyproject.toml and poetry.lock
COPY pyproject.toml poetry.lock /app/

# Install dependencies using Poetry
RUN /bin/bash -c "source $CONDA_DIR/etc/profile.d/conda.sh && \
    conda activate myenv && \
    poetry install"

# Ensure conda environment is activated when the container runs
CMD ["/bin/bash", "-c", "source $CONDA_DIR/etc/profile.d/conda.sh && conda activate myenv && /bin/bash -i"]
