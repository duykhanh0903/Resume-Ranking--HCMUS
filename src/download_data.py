import os
import pandas as pd
from datasets import load_dataset

def main():
    print("1. Đang tải dataset mới (zevy17568/resume-job-description-fit)...")
    try:
        dataset = load_dataset("zevy17568/resume-job-description-fit")
        
        output_dir = "data/raw"
        os.makedirs(output_dir, exist_ok=True)
        
        if 'train' in dataset:
            df = pd.DataFrame(dataset['train'])
        else:
            first_split = list(dataset.keys())[0]
            df = pd.DataFrame(dataset[first_split])
            
        output_path = os.path.join(output_dir, "resume_jd_fit.csv")
        df.to_csv(output_path, index=False)
        
        print(f"2. Đã tải và lưu thành công tại: {output_path}")
        print(f"   Tổng số dòng dữ liệu: {len(df)}")
        print(f"   Các cột dữ liệu: {list(df.columns)}")
        
    except Exception as e:
        print(f"Có lỗi xảy ra trong quá trình tải: {e}")

if __name__ == "__main__":
    main()