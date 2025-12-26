# From Unaligned to Aligned: Scaling Multilingual LLMs with Multi-Way Parallel Corpora (EMNLP 2025)

📄 Paper on arXiv: [https://arxiv.org/abs/2505.14045](https://arxiv.org/abs/2505.14045)

**Authors:**  
Yingli Shen<sup>1*</sup>, Wen Lai<sup>2,3*</sup>, Shuo Wang<sup>1</sup>, Ge Gao<sup>4</sup>, Kangyang Luo<sup>1</sup>, Alexander Fraser<sup>2,3</sup>, Maosong Sun<sup>1</sup>  
(* Equal contribution)

- <sup>1</sup> Tsinghua University  
- <sup>2</sup> Technical University of Munich  
- <sup>3</sup> Munich Center for Machine Learning  
- <sup>4</sup> Minzu University of China  

📧 Contact: wen.lai@tum.de, syl@mail.tsinghua.edu.cn

---

## 🚀 Overview

We introduce **TED2025**, a new multi-way parallel dataset derived from TED Talks, and investigate the following research questions:

- **RQ1:** How does fine-tuning on multi-way parallel data compare with training on unaligned multilingual text in terms of zero-shot cross-lingual transfer and representation alignment?  
- **RQ2:** Which strategies for selecting parallelism (e.g., degree of parallelism, language subsets) lead to the greatest improvements in multilingual LLM performance?  
- **RQ3:** Which instruction-tuning objectives can most effectively leverage the advantages of multi-way parallel data?  

---

## 📊 Dataset

- Due to [licensing restrictions](https://www.ted.com/about/our-organization/our-policies-terms/ted-com-terms-of-use), the dataset cannot be made publicly available.  
  - However, if you are interested in **research use**, please contact the author via email (wen.lai@tum.de). We can provide a Google Drive link directly for research purposes only.  
- While we cannot release the dataset itself, we do provide the **construction code** so that researchers can reproduce it (see [`code`](./code)).  
- Related dataset: [DCAD-2000](https://huggingface.co/datasets/openbmb/DCAD-2000).  

### 📈 Dataset Statistics

See the **Appendix** of our paper for details on domains and translation quality across language pairs.  

### ⚙️ Dataset Construction

**Step 1. Fetch the latest TED Talk IDs from RSS**
```python
python code/fetch_latest_ids.py \
    --limit 2000 \
    --output_csv outputs/ted_talks_ids.csv
```
**Step 2. Download subtitles and metadata by Talk IDs**
```python
# Option 1: From latest talk ID list
python code/crawl_ted_by_ids.py \
    --input_csv outputs/ted_talks_ids.csv \
    --output_dir outputs/transcripts \
    --meta_file outputs/meta_data.jsonl

# Option 2: By numeric ID range
python code/crawl_ted_by_range.py \
    --start_id 0 \
    --end_id 100000 \
    --output_dir outputs/transcripts \
    --meta_file outputs/meta_data.jsonl
```
**Step 3. Align multi-language transcripts into a parallel corpus**
```python
python code/align_transcripts.py \
    --input_dir outputs/transcripts \
    --output_file outputs/multi_way.jsonl
```

---

## 🧪 Experiments
+ Requirements: LLaMA-Factory (latest version).

### Run training:
```python
llamafactory-cli train $config_path
```
### Example Config
```yaml
### model
model_name_or_path: Qwen/Qwen2.5-72B-Instruct
trust_remote_code: true
cache_dir: **
hf_hub_token: **

### method
stage: pt
do_train: true
finetuning_type: lora
lora_rank: 8
lora_alpha: 32
lora_dropout: 0.1
lora_target: all

### dataset
dataset: ted_multi_way
cutoff_len: 2048
overwrite_cache: false
preprocessing_num_workers: 16
dataloader_num_workers: 4
dataset_dir: **

### output
output_dir: **
logging_steps: 10
save_steps: 500
plot_loss: true
overwrite_output_dir: true
save_only_model: false

### train
per_device_train_batch_size: 1
# gradient_accumulation_steps: 0
learning_rate: 1.0e-4
num_train_epochs: 3.0
lr_scheduler_type: cosine
warmup_ratio: 0.1
bf16: true
ddp_timeout: 180000000
resume_from_checkpoint: null
report_to: wandb
run_name: qwen_72b_ted
```

---

## 📖 Citation

[![DOI](https://img.shields.io/badge/DOI-10.48550/arXiv.2505.14045-green?color=FF8000?color=009922)](https://doi.org/10.48550/arXiv.2505.14045)
[![DOI](https://img.shields.io/badge/DOI-10.48550/arXiv.2502.11546-green?color=FF8000?color=009922)](https://doi.org/10.48550/arXiv.2502.11546)

If you find our work useful, please cite us:
```bibtex
@inproceedings{shen-etal-2025-unaligned,
    title = "From Unaligned to Aligned: Scaling Multilingual {LLM}s with Multi-Way Parallel Corpora",
    author = "Shen, Yingli  and
      Lai, Wen  and
      Wang, Shuo  and
      Gao, Ge  and
      Luo, Kangyang  and
      Fraser, Alexander  and
      Sun, Maosong",
    editor = "Christodoulopoulos, Christos  and
      Chakraborty, Tanmoy  and
      Rose, Carolyn  and
      Peng, Violet",
    booktitle = "Proceedings of the 2025 Conference on Empirical Methods in Natural Language Processing",
    month = nov,
    year = "2025",
    address = "Suzhou, China",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2025.emnlp-main.374/",
    doi = "10.18653/v1/2025.emnlp-main.374",
    pages = "7368--7390",
    ISBN = "979-8-89176-332-6",
}
```
```bibtex
@inproceedings{
    shen2025dcad,
    title={{DCAD}-2000: A Multilingual Dataset across 2000+ Languages with Data Cleaning as Anomaly Detection},
    author={Yingli Shen and Wen Lai and Shuo Wang and Xueren Zhang and Kangyang Luo and Alexander Fraser and Maosong Sun},
    booktitle={The Thirty-ninth Annual Conference on Neural Information Processing Systems Datasets and Benchmarks Track},
    year={2025},
    url={https://openreview.net/forum?id=Hqoywh28zV}
}
```
