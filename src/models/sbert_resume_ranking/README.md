---
tags:
- sentence-transformers
- sentence-similarity
- feature-extraction
- dense
- generated_from_trainer
- dataset_size:4069
- loss:CosineSimilarityLoss
base_model: sentence-transformers/all-MiniLM-L6-v2
widget:
- source_sentence: 'Required Skills: Excel, ARM, Credit and Accounts Receivable, Credit
    limits, AR insurance program, Reporting, Analytical reports, Customer listings,
    Aging analysis, Credit and Accounts Receivable experience, CPG, Manufacturing
    industry, Hard goods experience, Microsoft Word | Required Roles: Accountant,
    Accounts Receivable Specialist'
  sentences:
  - 'Skills: FASKB, GAAP, Oracle, CampusVue, Financial statement analysis, Analytical
    reasoning, Effective time management, Computer proficiency (PC and Mac), General
    ledger accounting, Account reconciliations, Journal entries, Inter company bank
    transactions, Month-end close process, Auditing, Tax accounting | Job Titles:
    Accountant II, Revenue Accountant, Financial Aid Officer'
  - 'Skills: SQL, Excel, VBA, Data Mining, MS Office, Business operations, Data interpretation,
    Analyzing trends, Operational improvement, Data management, Data Analysis, Workflow
    Optimization, Quality Assurance and Auditing, Project Management and Organization,
    Medical Billing and Coding | Job Titles: Master Data Management Analyst I, Cost
    Management/Medical Claims Analyst, Member Service Representative, Intake Coordinator/Communication
    Specialist'
  - 'Skills: Selenium WebDriver, TestNG, Selenium IDE, Jenkins, Maven, SVN Server,
    Oracle 11g, PL SQL, Java, HTML, Windows Server, Windows 2016, Windows 2008 R2,
    Linux, UNIX, Apache POI APIs, HP ALM 11, Caliber, HP-Quality Centre, CA Central
    Rally, Jira | Job Titles: Software Engineer Tester, Sr. Quality Analyst, Software
    Engineer (Testing)'
- source_sentence: 'Required Skills: GAAP, Microsoft Office Suite, QuickBooks, Excel,
    Access, Outlook, Word, PowerPoint, Financial Analysis, Bookkeeping, Financial
    Reporting, Account Reconciliation, Financial Statement Analysis, Data Analysis,
    Problem Solving | Required Roles: Accountant II, Financial Analyst, Financial
    Manager'
  sentences:
  - 'Skills: SQL, C++, C#, Microsoft Office Suite, Bloomberg, Morningstar, Quality
    Assurance, Automated Testing, Bug Testing, Performance Benchmarking, Process Innovation,
    Data Analysis, Financial Analysis, Mathematics | Job Titles: SQA Engineer III,
    Software Quality Assurance Engineer I, Process Innovation Intern'
  - 'Skills: Salesforce, SQL, Java, Mixpanel, Google Analytics, SharePoint, Oracle
    ATG, IBM WebSphere Commerce, JIRA, MS Visio, MS Project, Microsoft Office, SPSS,
    Adobe PClairetosClairep, API | Job Titles: Salesforce Business/Data Analyst, Business
    Analyst, Product Supervisor/Business Analyst'
  - 'Skills: Microsoft Office Suite, Salesforce, Google Analytics, DFP, The Trade
    Desk, QuickBooks, Account Management, Project Management, Sales, Invoicing, Contract
    Negotiation, Experiential Marketing, Social Media, Advertising, Digital Advertising
    | Job Titles: Account Manager, Project Management Leader, Senior Account Management
    Associate'
- source_sentence: 'Required Skills: SQL, MS Excel, Python, R, Google Analytics, Adobe
    Analytics, Statistics, AB Testing, Web Analytics, Data Analysis, Data Visualization,
    Marketing Analytics, Business Intelligence, Data Mining, Data Science | Required
    Roles: Sr. Marketing Analyst, Marketing Analyst, Business Analyst'
  sentences:
  - 'Skills: Java, JavaScript, Android, Python, Java EE, Servlets, JSP, JSF, REST,
    SOAP, JSON, XML, JMS, AWS, Cloud Foundry, Spring, Hibernate, Maven, Git | Job
    Titles: Java Software Engineer, Software Developer, Network Support Engineer'
  - 'Skills: Accounting cycle, Account reconciliation, General ledger accounting,
    Financial statement analysis, Budget Planning, Cash Management, Accounts Receivable,
    Accounts Payable, Inventory & Purchases, Fixed Assets, Auditing, Payroll, Taxes,
    Benefit and compensation, Microsoft Excel, Microsoft Office Suite, Quickbooks
    | Job Titles: Accountant, Accounting and Finance Supervisor, Administrator/Accountant,
    Assistant Controller, Seasonal Tax Advisor, Account Executive'
  - 'Skills: StatGraphics, Minitab, ProE, Solidworks, Microsoft Application Packages,
    ISO 14971 Risk Management System, ISO 13485, 21CFR 820.30, MDD 93/42/EEC Quality
    Management Systems, Matlab, Signal Processing, FMEA, Verification/Validation Protocols,
    Systems Testing, Risk Management, Vendor Audits | Job Titles: Product Development
    Engineer, Electrical Engineer, Biomedical Engineer'
- source_sentence: 'Required Skills: PHP, Golang, Docker, AWS, GCP, Kubernetes, EKS,
    GKE, AVC, HEVC, VP9, AV1, AAC, Container technology, CloudSaaS services | Required
    Roles: Senior Software Engineer, Software Engineer, Cloud Engineer'
  sentences:
  - 'Skills: Oracle Business Intelligence Enterprise Edition, BIP setup-configuration,
    Informatica - DAC setup & configuration, SQL, Oracle 9.x, Oracle 10g, MS Office
    Products, OBIEE, RPD / Report / Dashboard Development, Development Best Practices
    and Standards, Oracle, Siebel Applications, ETL, Database, Informatica, Toad |
    Job Titles: Senior Software Engineer, Assistant Systems Engineer, Module Lead'
  - 'Skills: Windows, Excel, Access, Office, Cognos BI, Lawson, SAP, Active Directory,
    MS Exchange Server, Oracle, SQL, MS Excel, Cognos Report Developer, Windows Active
    Directory 2005, PC imaging and deployment | Job Titles: Senior Supply Chain Data
    Analyst/Decision Support, Business Process Analyst/Engineering, Data Analyst'
  - 'Skills: Database design, LAN/WAN Network upgrades, Enterprise Technology, SAP,
    CRM interface, Excel, Access, Microsoft Server, AutoCAD, Civil Engineering, Internet
    and Intranet applications, Cross-tier components implementation, Technical specification
    creation, Diagnostic skills | Job Titles: Data Analyst, Business Analyst, Database
    Administrator'
- source_sentence: 'Required Skills: Golang, C++, Python, Machine Learning, Computer
    Vision, API, Cloud Applications, Data Analysis, Troubleshooting, IoT, Sensors,
    ML Models, Pipelines, Solid API Support, Developer Platforms | Required Roles:
    Software Engineer, Software Developer, Cloud Engineer'
  sentences:
  - 'Skills: QuickBooks, Sage Accounting, Peachtree Accounting, Microsoft Access,
    Microsoft Excel, Microsoft PowerPoint, Microsoft Outlook, Lotus note, GAAP, GASB,
    IFRS, General Ledger Accounting, Bank Reconciliation, Accounts Payable, Accounts
    Receivable | Job Titles: Accountant, Finance and Admin Manager, Finance Officer'
  - 'Skills: Microsoft Word, Excel, Access, Power Point, Windows, Office, SAP, Work
    Manager, Cognos, Data Entry, 10-key keyboard, Database, Dispatch, Dispatcher,
    Txdot, Coda | Job Titles: Data Control Clerk, Customer Service Representative,
    Customer Service Representative'
  - 'Skills: Power BI, Tableau, T-SQL, SSIS, SSRS, SQL Server 2008R2/2012/2014, Excel,
    Macros, Pivot table, Get Pivot Data, Dashboards, Power View, Power Map, Heat Map,
    SSAS, Business Intelligence Development Studio, DTS, SQL Profiler, MySQL, MS SQL
    2014/2012/2008 | Job Titles: BI Developer / Data Analyst, Network Administrator/CISCO,
    Technician III'
pipeline_tag: sentence-similarity
library_name: sentence-transformers
metrics:
- pearson_cosine
- spearman_cosine
model-index:
- name: SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2
  results:
  - task:
      type: semantic-similarity
      name: Semantic Similarity
    dataset:
      name: resume val
      type: resume-val
    metrics:
    - type: pearson_cosine
      value: 0.6903524015892694
      name: Pearson Cosine
    - type: spearman_cosine
      value: 0.6838393876962616
      name: Spearman Cosine
---

# SentenceTransformer based on sentence-transformers/all-MiniLM-L6-v2

This is a [sentence-transformers](https://www.SBERT.net) model finetuned from [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2). It maps sentences & paragraphs to a 384-dimensional dense vector space and can be used for semantic textual similarity, semantic search, paraphrase mining, text classification, clustering, and more.

## Model Details

### Model Description
- **Model Type:** Sentence Transformer
- **Base model:** [sentence-transformers/all-MiniLM-L6-v2](https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2) <!-- at revision c9745ed1d9f207416be6d2e6f8de32d1f16199bf -->
- **Maximum Sequence Length:** 256 tokens
- **Output Dimensionality:** 384 dimensions
- **Similarity Function:** Cosine Similarity
<!-- - **Training Dataset:** Unknown -->
<!-- - **Language:** Unknown -->
<!-- - **License:** Unknown -->

### Model Sources

- **Documentation:** [Sentence Transformers Documentation](https://sbert.net)
- **Repository:** [Sentence Transformers on GitHub](https://github.com/huggingface/sentence-transformers)
- **Hugging Face:** [Sentence Transformers on Hugging Face](https://huggingface.co/models?library=sentence-transformers)

### Full Model Architecture

```
SentenceTransformer(
  (0): Transformer({'max_seq_length': 256, 'do_lower_case': False, 'architecture': 'BertModel'})
  (1): Pooling({'word_embedding_dimension': 384, 'pooling_mode_cls_token': False, 'pooling_mode_mean_tokens': True, 'pooling_mode_max_tokens': False, 'pooling_mode_mean_sqrt_len_tokens': False, 'pooling_mode_weightedmean_tokens': False, 'pooling_mode_lasttoken': False, 'include_prompt': True})
  (2): Normalize()
)
```

## Usage

### Direct Usage (Sentence Transformers)

First install the Sentence Transformers library:

```bash
pip install -U sentence-transformers
```

Then you can load this model and run inference.
```python
from sentence_transformers import SentenceTransformer

# Download from the 🤗 Hub
model = SentenceTransformer("sentence_transformers_model_id")
# Run inference
sentences = [
    'Required Skills: Golang, C++, Python, Machine Learning, Computer Vision, API, Cloud Applications, Data Analysis, Troubleshooting, IoT, Sensors, ML Models, Pipelines, Solid API Support, Developer Platforms | Required Roles: Software Engineer, Software Developer, Cloud Engineer',
    'Skills: Microsoft Word, Excel, Access, Power Point, Windows, Office, SAP, Work Manager, Cognos, Data Entry, 10-key keyboard, Database, Dispatch, Dispatcher, Txdot, Coda | Job Titles: Data Control Clerk, Customer Service Representative, Customer Service Representative',
    'Skills: QuickBooks, Sage Accounting, Peachtree Accounting, Microsoft Access, Microsoft Excel, Microsoft PowerPoint, Microsoft Outlook, Lotus note, GAAP, GASB, IFRS, General Ledger Accounting, Bank Reconciliation, Accounts Payable, Accounts Receivable | Job Titles: Accountant, Finance and Admin Manager, Finance Officer',
]
embeddings = model.encode(sentences)
print(embeddings.shape)
# [3, 384]

# Get the similarity scores for the embeddings
similarities = model.similarity(embeddings, embeddings)
print(similarities)
# tensor([[ 1.0000,  0.0048, -0.0883],
#         [ 0.0048,  1.0000,  0.0631],
#         [-0.0883,  0.0631,  1.0000]])
```

<!--
### Direct Usage (Transformers)

<details><summary>Click to see the direct usage in Transformers</summary>

</details>
-->

<!--
### Downstream Usage (Sentence Transformers)

You can finetune this model on your own dataset.

<details><summary>Click to expand</summary>

</details>
-->

<!--
### Out-of-Scope Use

*List how the model may foreseeably be misused and address what users ought not to do with the model.*
-->

## Evaluation

### Metrics

#### Semantic Similarity

* Dataset: `resume-val`
* Evaluated with [<code>EmbeddingSimilarityEvaluator</code>](https://sbert.net/docs/package_reference/sentence_transformer/evaluation.html#sentence_transformers.evaluation.EmbeddingSimilarityEvaluator)

| Metric              | Value      |
|:--------------------|:-----------|
| pearson_cosine      | 0.6904     |
| **spearman_cosine** | **0.6838** |

<!--
## Bias, Risks and Limitations

*What are the known or foreseeable issues stemming from this model? You could also flag here known failure cases or weaknesses of the model.*
-->

<!--
### Recommendations

*What are recommendations with respect to the foreseeable issues? For example, filtering explicit content.*
-->

## Training Details

### Training Dataset

#### Unnamed Dataset

* Size: 4,069 training samples
* Columns: <code>sentence_0</code>, <code>sentence_1</code>, and <code>label</code>
* Approximate statistics based on the first 1000 samples:
  |         | sentence_0                                                                         | sentence_1                                                                          | label                                                          |
  |:--------|:-----------------------------------------------------------------------------------|:------------------------------------------------------------------------------------|:---------------------------------------------------------------|
  | type    | string                                                                             | string                                                                              | float                                                          |
  | details | <ul><li>min: 6 tokens</li><li>mean: 68.14 tokens</li><li>max: 159 tokens</li></ul> | <ul><li>min: 50 tokens</li><li>mean: 82.29 tokens</li><li>max: 256 tokens</li></ul> | <ul><li>min: 0.0</li><li>mean: 0.47</li><li>max: 1.0</li></ul> |
* Samples:
  | sentence_0                                                                                                                                                                                                                                                                                                                                                                    | sentence_1                                                                                                                                                                                                                                                                                                                                                                                                                          | label            |
  |:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|:-----------------|
  | <code>Required Skills: SAP S4HANA, GAAP, Financial Management, ERP Software, Microsoft Office Suite, Financial Reporting, Account Reconciliation, Bank Settlements, APAR Processing, Taxation Services, Financial Audits, General Ledger Accounts, Financial Records, Financial Management Software \| Required Roles: Staff Accountant, Accountant, Financial Analyst</code> | <code>Skills: Selenium IDE, Selenium RC, Selenium WebDriver, JUnit, Test NG, Mercury Interactive Automation tools like QTP, Java, API testing, Agile-SCRUM, ANT, Maven, JIRA, SOAP UI, Postman, SQL Queries, RESTFul Web Services, Functional Testing, Test Plans, Test Cases, Test Scripts, Test Automation \| Job Titles: Sr. Software Development Engineer, Software Quality Assurance Engineer, Test Automation Engineer</code> | <code>0.0</code> |
  | <code>Required Skills: SQL, Snowflake, Data Build Tool (dbt), Python, Airflow, integration platforms, git, command line, AWS, CloudFormation, Docker, Docker Compose \| Required Roles: Principal Data Engineer, Data Architect, Team Leader</code>                                                                                                                           | <code>Skills: Tableau Desktop, Tableau Server, Tableau Public, Tableau Online, Tableau Reader, MS Excel, SSRS, Snowflake DB, Cassandra, MEMsql, Oracle 11g, Oracle 10g, Oracle 9i, MS SQL Server 2005, MS SQL Server 2000, MS Access, Postgres, Amazon S3SQL, Python, T-SQL, HTML, CSS, Java \| Job Titles: Lead BI Developer/ Principal Data Analyst, Sr. Data Analyst, Data Analyst</code>                                        | <code>0.0</code> |
  | <code>Required Skills: JDE World, Homebuilder, Job Cost, Procurement, JDE World Homebuilder, JDE World, E1, JDE World to EnterpriseOne, Data preparation, Data conversion, Data validation, Migration \| Required Roles: JDE Business Analyst</code>                                                                                                                          | <code>Skills: HP Quality Center, SoapUI, SQL, XML, Windows, Linux, Unix, QTP, C, C++, Agile Methodologies, Test Plans, Test Cases, Test Processes, Defect / Bug Tracking, UAT and System Testing, Testing Automation, Regression & negative testing, Data interface and migration testing \| Job Titles: Senior Software Quality Assurance Tester, QA Tester (Senior SME), Operations Scheduler</code>                              | <code>1.0</code> |
* Loss: [<code>CosineSimilarityLoss</code>](https://sbert.net/docs/package_reference/sentence_transformer/losses.html#cosinesimilarityloss) with these parameters:
  ```json
  {
      "loss_fct": "torch.nn.modules.loss.MSELoss"
  }
  ```

### Training Hyperparameters
#### Non-Default Hyperparameters

- `eval_strategy`: steps
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `num_train_epochs`: 4
- `multi_dataset_batch_sampler`: round_robin

#### All Hyperparameters
<details><summary>Click to expand</summary>

- `do_predict`: False
- `eval_strategy`: steps
- `prediction_loss_only`: True
- `per_device_train_batch_size`: 16
- `per_device_eval_batch_size`: 16
- `gradient_accumulation_steps`: 1
- `eval_accumulation_steps`: None
- `torch_empty_cache_steps`: None
- `learning_rate`: 5e-05
- `weight_decay`: 0.0
- `adam_beta1`: 0.9
- `adam_beta2`: 0.999
- `adam_epsilon`: 1e-08
- `max_grad_norm`: 1
- `num_train_epochs`: 4
- `max_steps`: -1
- `lr_scheduler_type`: linear
- `lr_scheduler_kwargs`: None
- `warmup_ratio`: None
- `warmup_steps`: 0
- `log_level`: passive
- `log_level_replica`: warning
- `log_on_each_node`: True
- `logging_nan_inf_filter`: True
- `enable_jit_checkpoint`: False
- `save_on_each_node`: False
- `save_only_model`: False
- `restore_callback_states_from_checkpoint`: False
- `use_cpu`: False
- `seed`: 42
- `data_seed`: None
- `bf16`: False
- `fp16`: False
- `bf16_full_eval`: False
- `fp16_full_eval`: False
- `tf32`: None
- `local_rank`: -1
- `ddp_backend`: None
- `debug`: []
- `dataloader_drop_last`: False
- `dataloader_num_workers`: 0
- `dataloader_prefetch_factor`: None
- `disable_tqdm`: False
- `remove_unused_columns`: True
- `label_names`: None
- `load_best_model_at_end`: False
- `ignore_data_skip`: False
- `fsdp`: []
- `fsdp_config`: {'min_num_params': 0, 'xla': False, 'xla_fsdp_v2': False, 'xla_fsdp_grad_ckpt': False}
- `accelerator_config`: {'split_batches': False, 'dispatch_batches': None, 'even_batches': True, 'use_seedable_sampler': True, 'non_blocking': False, 'gradient_accumulation_kwargs': None}
- `parallelism_config`: None
- `deepspeed`: None
- `label_smoothing_factor`: 0.0
- `optim`: adamw_torch_fused
- `optim_args`: None
- `group_by_length`: False
- `length_column_name`: length
- `project`: huggingface
- `trackio_space_id`: trackio
- `ddp_find_unused_parameters`: None
- `ddp_bucket_cap_mb`: None
- `ddp_broadcast_buffers`: False
- `dataloader_pin_memory`: True
- `dataloader_persistent_workers`: False
- `skip_memory_metrics`: True
- `push_to_hub`: False
- `resume_from_checkpoint`: None
- `hub_model_id`: None
- `hub_strategy`: every_save
- `hub_private_repo`: None
- `hub_always_push`: False
- `hub_revision`: None
- `gradient_checkpointing`: False
- `gradient_checkpointing_kwargs`: None
- `include_for_metrics`: []
- `eval_do_concat_batches`: True
- `auto_find_batch_size`: False
- `full_determinism`: False
- `ddp_timeout`: 1800
- `torch_compile`: False
- `torch_compile_backend`: None
- `torch_compile_mode`: None
- `include_num_input_tokens_seen`: no
- `neftune_noise_alpha`: None
- `optim_target_modules`: None
- `batch_eval_metrics`: False
- `eval_on_start`: False
- `use_liger_kernel`: False
- `liger_kernel_config`: None
- `eval_use_gather_object`: False
- `average_tokens_across_devices`: True
- `use_cache`: False
- `prompts`: None
- `batch_sampler`: batch_sampler
- `multi_dataset_batch_sampler`: round_robin
- `router_mapping`: {}
- `learning_rate_mapping`: {}

</details>

### Training Logs
| Epoch  | Step | Training Loss | resume-val_spearman_cosine |
|:------:|:----:|:-------------:|:--------------------------:|
| 0.1961 | 50   | -             | 0.4109                     |
| 0.3922 | 100  | -             | 0.4891                     |
| 0.5882 | 150  | -             | 0.5345                     |
| 0.7843 | 200  | -             | 0.5564                     |
| 0.9804 | 250  | -             | 0.5975                     |
| 1.0    | 255  | -             | 0.5943                     |
| 1.1765 | 300  | -             | 0.5948                     |
| 1.3725 | 350  | -             | 0.6236                     |
| 1.5686 | 400  | -             | 0.6288                     |
| 1.7647 | 450  | -             | 0.6157                     |
| 1.9608 | 500  | 0.1221        | 0.6312                     |
| 2.0    | 510  | -             | 0.6440                     |
| 2.1569 | 550  | -             | 0.6303                     |
| 2.3529 | 600  | -             | 0.6429                     |
| 2.5490 | 650  | -             | 0.6610                     |
| 2.7451 | 700  | -             | 0.6631                     |
| 2.9412 | 750  | -             | 0.6626                     |
| 3.0    | 765  | -             | 0.6665                     |
| 3.1373 | 800  | -             | 0.6766                     |
| 3.3333 | 850  | -             | 0.6800                     |
| 3.5294 | 900  | -             | 0.6814                     |
| 3.7255 | 950  | -             | 0.6802                     |
| 3.9216 | 1000 | 0.0887        | 0.6838                     |


### Framework Versions
- Python: 3.12.13
- Sentence Transformers: 5.3.0
- Transformers: 5.0.0
- PyTorch: 2.10.0+cu128
- Accelerate: 1.13.0
- Datasets: 4.0.0
- Tokenizers: 0.22.2

## Citation

### BibTeX

#### Sentence Transformers
```bibtex
@inproceedings{reimers-2019-sentence-bert,
    title = "Sentence-BERT: Sentence Embeddings using Siamese BERT-Networks",
    author = "Reimers, Nils and Gurevych, Iryna",
    booktitle = "Proceedings of the 2019 Conference on Empirical Methods in Natural Language Processing",
    month = "11",
    year = "2019",
    publisher = "Association for Computational Linguistics",
    url = "https://arxiv.org/abs/1908.10084",
}
```

<!--
## Glossary

*Clearly define terms in order to be accessible across audiences.*
-->

<!--
## Model Card Authors

*Lists the people who create the model card, providing recognition and accountability for the detailed work that goes into its construction.*
-->

<!--
## Model Card Contact

*Provides a way for people who have updates to the Model Card, suggestions, or questions, to contact the Model Card authors.*
-->