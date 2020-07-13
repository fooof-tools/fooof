#!/usr/bin/bash

# Conda-forge instructions:
#   - Fork the feedstock repo (https://github.com/conda-forge/fooof-feedstock).
#   - Update the meta.yaml file.
#   - Make a pull request. Once merged, the package will be rebuilt on the conda-forge channel.

# Anaconda is required to upload to Anaconda Cloud.
if [[ $(which anaconda) == '' ]]; then
    echo "Anaconda is not installed or not in \$PATH. Exiting."
    exit 1
fi

# Install conda-build if not found.
if [[ $(conda list | grep conda-build) == '' ]]; then
    echo "Installing conda-build."
    conda install conda-build
fi

# Install anaconda-client if not found.
if [[ $(conda list | grep anaconda-client) == '' ]]; then
    echo "Installing anaconda-client."
    conda install anaconda-client
fi

# Build
mkdir -p build
echo "Building..."
conda build fooof --output-folder=build >> build.log 2>&1
build=$(conda build fooof --output-folder=build --output)

# Upload. Note: this will prompt a username/password
echo "Uploading to cloud..."
anaconda upload --user fooof-tools $build

echo -e "To install fooof with conda, run:\n\tconda install -c fooof-tools fooof"
