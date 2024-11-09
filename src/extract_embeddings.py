import sys
import re
import torch
import requests
from transformers import T5Tokenizer, T5EncoderModel
import os
import numpy as np
import argparse

def setup_device():
    device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
    print(f"Using device: {device}")
    return device

def load_model_and_tokenizer(device):
    tokenizer = T5Tokenizer.from_pretrained('Rostlab/ProstT5', do_lower_case=False)
    model = T5EncoderModel.from_pretrained("Rostlab/ProstT5").to(device)
    model.full() if device.type == 'cpu' else model.half()
    return tokenizer, model

def read_fasta(in_path, is_3Di=False):
    sequences = dict()
    with open(in_path, 'r') as fasta_f:
        for line in fasta_f:
            if line.startswith('>'):
                uniprot_id = line[line.find('P'):line.find('P')+6]
                sequences[uniprot_id] = ''
            else:
                sequence_line = ''.join(line.split()).replace("-", "")
                sequences[uniprot_id] += sequence_line.lower() if is_3Di else sequence_line
    return sequences

def preprocess_sequences(sequences):
    sequences = [" ".join(list(re.sub(r"[UZOB]", "X", sequence))) for sequence in sequences]
    sequence_input = [f"<AA2fold> {s}" if s.isupper() else f"<fold2AA> {s}" for s in sequences]
    return sequence_input

def generate_per_protein_embeddings(sequences, tokenizer, model, device, chunk_size=10):
    protein_embeddings = []
    
    # Process in chunks
    for i in range(0, len(sequences), chunk_size):
        chunk = sequences[i:i + chunk_size]
        print(f"Processing chunk {i // chunk_size + 1} with {len(chunk)} sequences.")
        
        ids = tokenizer.batch_encode_plus(chunk, add_special_tokens=True, padding="longest", return_tensors='pt').to(device)
        
        with torch.no_grad():
            embedding_rpr = model(ids.input_ids, attention_mask=ids.attention_mask)
        
        # Calculate per_protein embeddings
        for j, seq in enumerate(chunk):
            seq_len = len("".join(seq.split()))
            per_protein = embedding_rpr.last_hidden_state[j, 1:seq_len + 1].mean(dim=0)
            protein_embeddings.append(per_protein.cpu().numpy())
    
    # Convert to matrix
    embedding_matrix = np.stack(protein_embeddings)
    return embedding_matrix

def main(fasta_path, chunk_size=10):
    device = setup_device()
    tokenizer, model = load_model_and_tokenizer(device)
    
    # Load and preprocess sequences
    sequences_dict = read_fasta(fasta_path, is_3Di=False)
    sequences = list(sequences_dict.values())
    sequences = preprocess_sequences(sequences)
    print(f"Number of sequences: {len(sequences)}")
    
    # Generate embeddings
    embedding_matrix = generate_per_protein_embeddings(sequences, tokenizer, model, device, chunk_size=chunk_size)
    print("Embeddings generated successfully.")
    print(f"Embedding matrix shape: {embedding_matrix.shape}")
    
    # Comparison of chunkwise vs one-by-one embeddings
    print("Comparing chunkwise and one-by-one embeddings:")
    # Generate embeddings one-by-one
    one_by_one_embeddings = []
    for sequence in sequences:
        embedding = generate_per_protein_embeddings([sequence], tokenizer, model, device, chunk_size=1)
        one_by_one_embeddings.append(embedding[0])
    one_by_one_embeddings = np.stack(one_by_one_embeddings)
    
    # Check if they are almost equal
    try:
        np.testing.assert_almost_equal(embedding_matrix, one_by_one_embeddings, decimal=5)
        print("Embeddings generated chunkwise and one-by-one are almost equal.")
    except AssertionError as e:
        print("Embeddings generated chunkwise and one-by-one are not equal")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate per-protein embeddings from amino acid sequences.")
    parser.add_argument('--fasta', type=str, required=True, help="Path to the input FASTA file.")
    parser.add_argument('--chunk_size', type=int, default=10, help="Number of sequences to process per chunk.")
    args = parser.parse_args()
    
    main(args.fasta, args.chunk_size)
