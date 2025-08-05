import glob
import pandas as pd

def main():
    parquet_files = glob.glob("dane_*.parquet")
    
    parquet_files = sorted(parquet_files)
    
    df_list = []
    for file_path in parquet_files:
        print(f"Przetwarzam plik: {file_path}")
        df = pd.read_parquet(file_path)
        
        
        df_sample = df.sample(frac=0.05, random_state=42)
        
        df_list.append(df_sample)

    if df_list:
        df_final = pd.concat(df_list, ignore_index=True)
        df_final.to_parquet("dane.parquet", index=False)
        print("Zapisano plik dane.parquet")
    else:
        print("Nie znaleziono żadnych plików .parquet lub pliki były puste.")

if __name__ == "__main__":
    main()

