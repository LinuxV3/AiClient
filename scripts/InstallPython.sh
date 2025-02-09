#!/bin/bash

if [ -z "$1" ]; then
  echo "Usage: $0 <python_version>"
  echo "Example: $0 3.12.3"
  exit 1
fi

PYTHON_VERSION=$1
PYTHON_SOURCE="Python-${PYTHON_VERSION}"
PYTHON_URL="https://www.python.org/ftp/python/${PYTHON_VERSION}/${PYTHON_SOURCE}.tgz"

echo "Installing required dependencies..."
if command -v apt &> /dev/null; then
  sudo apt update
  sudo apt install -y build-essential libssl-dev zlib1g-dev \
    libncurses5-dev libncursesw5-dev libreadline-dev libsqlite3-dev \
    libgdbm-dev libdb5.3-dev libbz2-dev libexpat1-dev liblzma-dev \
    tk-dev libffi-dev libgdbm-compat-dev
elif command -v dnf &> /dev/null; then
  sudo dnf groupinstall -y "Development Tools"
  sudo dnf install -y openssl-devel bzip2-devel libffi-devel \
    zlib-devel ncurses-devel sqlite-devel readline-devel tk-devel \
    gdbm-devel xz-devel expat-devel
elif command -v yum &> /dev/null; then
  sudo yum groupinstall -y "Development Tools"
  sudo yum install -y openssl-devel bzip2-devel libffi-devel \
    zlib-devel ncurses-devel sqlite-devel readline-devel tk-devel \
    gdbm-devel xz-devel expat-devel
else
  echo "Unsupported package manager. Please install dependencies manually."
  exit 1
fi

echo "Downloading Python ${PYTHON_VERSION}..."
wget -q "${PYTHON_URL}" || { echo "Failed to download Python source code."; exit 1; }

echo "Extracting ${PYTHON_SOURCE}.tgz..."
tar -xzf "${PYTHON_SOURCE}.tgz" || { echo "Failed to extract Python source code."; exit 1; }

cd "${PYTHON_SOURCE}" || { echo "Failed to enter Python source directory."; exit 1; }

echo "Configuring Python build..."
./configure --enable-optimizations || { echo "Configuration failed."; exit 1; }

echo "Compiling Python..."
make -j$(nproc) || { echo "Compilation failed."; exit 1; }

echo "Installing Python..."
sudo make altinstall || { echo "Installation failed."; exit 1; }

echo "Verifying installation..."
python3.12 --version || { echo "Python installation verification failed."; exit 1; }

echo "Cleaning up..."
cd ..
rm -rf "${PYTHON_SOURCE}" "${PYTHON_SOURCE}.tgz"

echo "Python ${PYTHON_VERSION} installed successfully!"