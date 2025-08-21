From Unaligned to Aligned: Scaling Multilingual LLMs with Multi-Way Parallel Corpora (EMNLP 2025)
===
Paper: https://arxiv.org/abs/2505.14045

Authors: Yingli Shen<sup>1*</sup>, Wen Lai<sup>2,3*</sup>, Shuo Wang<sup>1</sup>, Ge Gao<sup>4</sup>, Kangyang Luo<sup>1</sup>, Alexander Fraser<sup>2,3</sup>, Maosong Sun<sup>1</sup> (* Equal Contribution)

$^1$ Tsinghua University, $^2$ Technical University of Munich, $^3$ Munich Center for Machine Learning, $^4$ Minzu University of China

Email: syl@mail.tsinghua.edu.cn, wen.lai@tum.de

## Overview
+ We introduce a new multi-way parallel dataset, TED2025, which source from TED Talks.
+ We investigate the following research question:
    - **RQ1:** How does fine-tuning on multi-way parallel data compare to training on unaligned multilingual text in terms of zero-shot cross-lingual transfer and representation alignment?
    - **RQ2:** Which strategies for selecting parallelism in multi-way parallel data (e.g., degree of parallelism and language subsets) lead to the greatest improvements in multilingual LLM performance?
    - **RQ3:** Which instruction-tuning objectives can most effectively leverage the advantages of multiway parallel data?

<!-- ![TED2025](./images/dataset_compare.png)
![TED2025](./images/ted_parallelism.png) -->

## Dataset
+ Unfortunately, due to [licensing restrictions](https://www.ted.com/about/our-organization/our-policies-terms/ted-com-terms-of-use), we are unable to make the dataset publicly available. However, if you are interested in using the dataset for research purposes, please contact the author via email (wen.lai@tum.de). We will be happy to provide it to you directly.
+ DCAD-2000 dataset: [DCAD-2000](https://huggingface.co/datasets/openbmb/DCAD-2000)

#### Dataset Statistics
+ Please refer to the appendix in our paper, which contains the domain, translation quality of each language pair.

## Experiments
+ Requirements: [LLaMA-Factory](https://llamafactory.readthedocs.io/en/latest/), please install the latest version.
+ Runing:
```
llamafactory-cli train $config_path
```
+ Config (example):
```
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

## Citation

[![DOI](https://img.shields.io/badge/DOI-10.48550/arXiv.2505.14045-green?color=FF8000?color=009922)](https://doi.org/10.48550/arXiv.2505.14045)
[![DOI](https://img.shields.io/badge/DOI-10.48550/arXiv.2502.11546-green?color=FF8000?color=009922)](https://doi.org/10.48550/arXiv.2502.11546)

Please cite our paper if it's helpful to your work!
```
@article{shen2025unaligned,
  title={From Unaligned to Aligned: Scaling Multilingual LLMs with Multi-Way Parallel Corpora},
  author={Shen, Yingli and Lai, Wen and Wang, Shuo and Luo, Kangyang and Fraser, Alexander and Sun, Maosong},
  journal={arXiv preprint arXiv:2505.14045},
  year={2025}
}
```
```
@article{shen2025dcad,
  title={DCAD-2000: A Multilingual Dataset across 2000+ Languages with Data Cleaning as Anomaly Detection},
  author={Shen, Yingli and Lai, Wen and Wang, Shuo and Zhang, Xueren and Luo, Kangyang and Fraser, Alexander and Sun, Maosong},
  journal={arXiv preprint arXiv:2502.11546},
  year={2025}
}
```
