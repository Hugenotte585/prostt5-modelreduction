#!/bin/bash

set -e

update_rc=false
rc_file=~/.bashrc

test_conda() {
    eval "$(conda shell.bash hook)" # fixes a bug where conda isn't initialized in the shell

    if ! command -v conda &> /dev/null; then
        echo "Conda could not be found. Please install Conda."
        exit 1
    fi
}

setup_lora_env() {
    echo "-----------------------------------------------"
    echo "Setting up LoRAPrune environment..."
    pushd libs/LoRAPrune

    if [ ! -d "env" ]; then
        python3 -m venv env
        source env/bin/activate
        pip install -r requirements.txt
        deactivate
        echo "LoRAPrune environment setup complete."
        echo "Virtual environment name: env" # named like this because of gitignore
    else
        echo "LoRAPrune environment already exists."
        echo "To activate the environment, run the following command:"
        echo "source libs/LoRAPrune/env/bin/activate"
    fi
    popd
}

setup_mtdp_env() {
    echo "-----------------------------------------------"
    echo "Setting up MTDP environment..."

    test_conda

    pushd libs/MTDP
    
    if [[ ! $(conda env list | grep MTDP) ]]; then
        echo "Creating conda environment..."
        conda env create -f distillation.yaml
        echo "MTDP environment setup complete."
        echo "Conda environment name: MTDP"
    else
        echo "MTDP environment already exists."
        echo "To activate the environment, run the following command:"
        echo "conda activate MTDP"
    fi
    popd
}

setup_foldseek_env() {
    echo "-----------------------------------------------"
    echo "Setting up FoldSeek environment..."
    pushd libs

    test_conda
    
    # hence avx2 is less common than sse2 we will check if avx2 is supported
    distro=$(uname -s)
    # untested on mac
    if [ "$distro" == "Darwin" ]; then
        dl_link=https://mmseqs.com/foldseek/foldseek-macos.tar.gz
    elif grep -q avx2 /proc/cpuinfo; then
        dl_link=https://mmseqs.com/foldseek/foldseek-linux-avx2.tar.gz
    else
        dl_link=https://mmseqs.com/foldseek/foldseek-linux-sse2.tar.gz
    fi
    echo "Downloading FoldSeek..."
    if [ ! -d "foldseek" ]; then
        wget $dl_link 
        tar xvzf foldseek-linux-avx2.tar.gz
        rm foldseek-linux-avx2.tar.gz

        if $update_rc; then
            echo "export PATH=$(pwd)/foldseek/bin:\$PATH" >> $rc_file
            source $rc_file
        else
            echo "If you want to add the foldseek binary to your PATH permanently put the following line in your shell rc file:"
            echo "export PATH=$(pwd)/foldseek/bin:\$PATH"
            echo "After sourcing the rc file (or restarting the terminal), you can run FoldSeek commands from any directory."
            export PATH=$(pwd)/foldseek/bin:$PATH
        fi
    else
        echo "FoldSeek already exists."
        echo "To add the FoldSeek binary to your PATH, run the following command:"
        echo "export PATH=$(pwd)/foldseek/bin:\$PATH"
    fi

    # create conda environment
    if [[ ! $(conda env list | grep foldseek) ]]; then
        echo "Creating conda environment..."
        conda create -q --name foldseek -y
        echo "created env"
        echo $(conda env list)
        conda activate foldseek
        echo "activated env"
        echo $(which python)
        conda install -c conda-forge -c bioconda foldseek -y
        
        conda deactivate
    else
        echo "FoldSeek environment already exists."
        echo "To activate the environment, run the following command:"
        echo "conda activate foldseek"
    fi
    popd
}

setup_prostt5_env() {
    echo "-----------------------------------------------"
    echo "Setting up ProstT5 environment..."
    pushd libs/ProstT5
    if [ ! -d "env" ]; then
        python3 -m venv env
        source env/bin/activate
        pip install torch
        pip install transformers
        pip install sentencepiece
        pip install protobuf
        echo "ProstT5 environment setup complete."
        echo "Virtual environment name: env"
    else
        echo "ProstT5 environment already exists."
        echo "To activate the environment, run the following command from project root:"
        echo "source libs/ProstT5/env/bin/activate"
    fi

    popd
}

usage() {
    echo "Usage: $0 [--lora | --mtdp | --foldseek | --prostt5 | --all]"
    echo "  --lora      - Install the LoRAPrune environment"
    echo "  --mtdp      - Install the MTDP environment"
    echo "  --foldseek  - Install the FoldSeek environment"
    echo "  --prostt5   - Install the ProstT5 environment"
    echo "  --all       - Install all environments"
    exit 1
}

install_lora=false
install_mtdp=false
install_foldseek=false
install_prostt5=false

if [ $# -eq 0 ]; then
    install_lora=true
    install_mtdp=true
    install_foldseek=true
    install_prostt5=true
else
    for arg in "$@"; do
        case "$arg" in
            --lora)
                install_lora=true
                ;;
            --mtdp)
                install_mtdp=true
                ;;
            --foldseek)
                install_foldseek=true
                ;;
            --prostt5)
                install_prostt5=true
                ;;
            --all)
                install_lora=true
                install_mtdp=true
                install_foldseek=true
                install_prostt5=true
                ;;
            *)
                usage
                ;;
        esac
    done
fi

if [ "$install_lora" = true ]; then setup_lora_env; fi
if [ "$install_mtdp" = true ]; then setup_mtdp_env; fi
if [ "$install_foldseek" = true ]; then setup_foldseek_env; fi
if [ "$install_prostt5" = true ]; then setup_prostt5_env; fi