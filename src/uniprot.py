import requests
import date
import os

def download_fasta_single(uniprot_id: str) -> str:
    url = f"https://www.uniprot.org/uniprot/{uniprot_id}.fasta"
    response = requests.get(url)
    return response.text

def download_fasta_single_test():
    uniprot_id = "P12345"
    fasta = download_fasta_single(uniprot_id)
    assert {uniprot_id} in fasta

def download_fasta(uniprot_ids: list[str], save=True, save_path = "../data/") -> list[str]:
    file_name = os.path.join(save_path, f"{date.today()}.fasta")

    fasta_list = []
    with open(file_name, "w") as file:
        for uniport_id in uniprot_ids:
            try:
                fasta = download_fasta_single(uniport_id)
            except Exception as e:
                print(f"Error downloading {uniport_id}: {e}")
                continue
            fasta_list.append(fasta)
            if save:
                file.write(fasta)
    return fasta_list

def download_fasta_test():
    uniprot_ids = ["P12345", "P12346", "P12347", "P12348"]

if __name__ == "__main__":
    download_fasta_single_test()