#!/bin/bash

setup_lora_env() {
    echo "Setting up LoRAPrune environment..."
    pushd libs/LoRAPrune

    if [ ! -d "env" ]; then
        echo "Creating environment for LoRAPrune..."
        python3 -m venv env
        source env/bin/activate
        echo "Installing dependencies for LoRAPrune..."
        pip install -r requirements.txt
        deactivate
    else
        echo "LoRAPrune environment already exists."
    fi

    popd
}

setup_mtdp_env() {
    echo "Setting up MTDP environment..."

    if ! command -v conda &> /dev/null; then
        echo "Conda could not be found. Please install Conda."
        exit 1
    fi

    pushd libs/MTDP
    echo "Creating Conda environment for MTDP..."
    conda env create -f distillation.yaml
    popd
}

usage() {
    echo "Usage: $0 [lora|mtdp|all]"
    echo "  lora  - Install the LoRAPrune environment"
    echo "  mtdp  - Install the MTDP environment"
    echo "  all   - Install both environments"
    exit 1
}

if [ $# -eq 0 ]; then
    setup_lora_env
    setup_mtdp_env
else
    case "$1" in
        lora)
            setup_lora_envgg
        mtdp)
            setup_mtdp_env
            ;;
        all)
            setup_lora_env
            setup_mtdp_env
            ;;
        *)
            usage
            ;;
    esac
fi