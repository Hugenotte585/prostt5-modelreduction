# ProstT5-ModelReduction

This project aims to develop and implement model reduction techniques to enhance the efficiency of protein function prediction using the ProstT5 language model. 
As large protein language models become increasingly powerful but computationally expensive, there is a growing need for methods that can maintain high accuracy while reducing model size and computational requirements. The project focuses on applying distillation, quantization, and pruning techniques, including the combination of Low-Rank Adaptation (LoRA) with pruning, to ProstT5. The reduced models will be evaluated on the FLIP benchmarks to assess their performance in protein function prediction tasks.

1. **Induction to existing literature** and familiarization with protein language models, particularly ProstT5.
2. **Model reduction techniques**:
   - **Distillation**: Design and implement a smaller student model trained using knowledge distillation.
   - **Quantization**: Apply post-training quantization to ProstT5, experimenting with different schemes.
   - **Pruning**: Implement structured pruning techniques and explore combining them with LoRA.
3. **Integration of LoRA with Pruning**:
   - Develop and implement LoRA-guided pruning to effectively reduce model complexity.
4. **Evaluation on FLIP benchmarks** for protein function prediction and comparison with the original ProstT5 model.
5. **Analyze trade-offs** between model size, computational efficiency, and prediction performance.

## Getting Started

To clone this repository and include the submodules (e.g., MTDP and LoRAPrune), use the following command:

```bash
git clone --recursive https://gitlab.lrz.de/ge56naf/prostt5-modelreduction.git
````
