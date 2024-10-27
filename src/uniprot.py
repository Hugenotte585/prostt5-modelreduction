import requests
import datetime
import os
from multiprocessing import Pool
from math import ceil
import time

def download_fasta_single(uniprot_id: str, save=True, save_dir="../data/", retries=3, session=None) -> str:
    """
    Download a single FASTA file for the given UniProt ID.
    """
    url = f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta"
    attempts = 0
    while attempts < retries:
        try:
            if session is None:
              session = requests.Session()
            response = session.get(url)
            response.raise_for_status()
            if save:
                with open(os.path.join(save_dir,f"{uniprot_id}.fasta"), "w") as file:
                    file.write(response.text) 
            return response.text
        except requests.RequestException as e:
            attempts += 1
            #print(f"Retrying ({attempts}/{retries}) for {uniprot_id} due to error: {e}")
            time.sleep(0.5)
            
    print(f"Failed to download {uniprot_id} after {retries} attempts.")
    return None


def download_fasta(uniprot_ids: list[str], save=True, save_dir="../data/", retries=3) -> tuple[list[str], list[str]]:
    """
    Download multiple FASTA files sequentially and optionally save to a file.
    """
    os.makedirs(save_dir, exist_ok=True)
    file_name = os.path.join(save_dir, f"{datetime.date.today()}.fasta")
    
    fasta_list = []
    failed_ids = []
    if save:
      file = open(file_name, "w")
    
    session = requests.Session() # persistent session
    for uniprot_id in uniprot_ids:
        fasta = download_fasta_single(uniprot_id, save=False, retries=retries, session=session)
        if fasta:
            fasta_list.append(fasta)
            if save:
                file.write(fasta)
        else:
            failed_ids.append(uniprot_id)

    return fasta_list, failed_ids


def download_fasta_parallel(uniprot_ids: list[str], num_proc=8, save=True, save_dir="../data/", retries=3) -> tuple[list[str], list[str]]:
    """
    Download multiple FASTA files in parallel and optionally save to a file.
    """
    if len(uniprot_ids) < num_proc:
        num_proc = len(uniprot_ids)
    
    os.makedirs(save_dir, exist_ok=True)
    file_name = os.path.join(save_dir, f"{datetime.date.today()}.fasta")

    chunk_size = ceil(len(uniprot_ids) / num_proc)
    uniprot_chunks = [uniprot_ids[i:i + chunk_size] for i in range(0, len(uniprot_ids), chunk_size)]
    
    with Pool(num_proc) as pool:
        results = pool.starmap(download_fasta, [(chunk, False, save_dir, retries) for chunk in uniprot_chunks])
    
    fasta_list = [item for sublist in results for item in sublist[0]]
    failed_ids = [item for sublist in results for item in sublist[1]]
    
    if save:
        with open(file_name, "w") as file:
            for fasta in fasta_list:
                file.write(fasta)
    
    return fasta_list, failed_ids

def download_fasta_single_test():
    print("Running test for download_fasta_single")
    uniprot_id = "P12345"
    start_time = time.time()
    fasta = download_fasta_single(uniprot_id)
    end_time = time.time()
    print(f"Time taken for single download: {end_time - start_time:.2f} seconds")
    if fasta:
        assert uniprot_id in fasta, "Failed: FASTA data does not contain the UniProt ID."
    else:
        print("Warning: The download might have failed for UniProt ID:", uniprot_id)

def download_fasta_sequential_test():
    print("Running test for download_fasta (sequential)")
    uniprot_ids = [f"P{i:05d}" for i in range(12345, 13345)] 
    start_time = time.time()
    fasta_list, failed_ids = download_fasta(uniprot_ids)
    end_time = time.time()
    print(f"Time taken for sequential download: {end_time - start_time:.2f} seconds")
    print(f"Downloaded {len(fasta_list)} out of {len(uniprot_ids)} UniProt IDs.")
    print(f"Failed to download {len(failed_ids)} out of {len(uniprot_ids)} UniProt IDs.")
    assert len(fasta_list) + len(failed_ids) == len(uniprot_ids), "Failed: Some FASTA entries are missing."

def download_fasta_parallel_test():
    print("Running test for download_fasta_parallel")
    uniprot_ids = [f"P{i:05d}" for i in range(12345, 13345)]  
    start_time = time.time()
    fasta_list, failed_ids = download_fasta_parallel(uniprot_ids)
    end_time = time.time()
    print(f"Time taken for parallel download: {end_time - start_time:.2f} seconds")
    print(f"Downloaded {len(fasta_list)} out of {len(uniprot_ids)} UniProt IDs.")
    print(f"Failed to download {len(failed_ids)} out of {len(uniprot_ids)} UniProt IDs.")
    assert len(fasta_list) + len(failed_ids) == len(uniprot_ids), "Failed: Some FASTA entries are missing."

if __name__ == "__main__":
    download_fasta_single_test()
    download_fasta_sequential_test()
    download_fasta_parallel_test()
