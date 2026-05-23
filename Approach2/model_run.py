# ============================================================================
{
  "cells": [
    {
      "cell_type": "code",
      "source": [
        "# ============================================================================\n",
        "# STEP 0.1: LOAD THE RAW DATA FROM KEYWORD PROJECT\n",
        "# ============================================================================\n",
        "\n",
        "import sempy.fabric as fabric\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "from collections import defaultdict\n",
        "import re\n",
        "from datetime import datetime\n",
        "\n",
        "# Define workspace and dataset\n",
        "workspace = \"Operational Excellence [Development]\"\n",
        "dataset = \"Operations Dashboard\"\n",
        "\n",
        "print(\" Loading data from Fabric...\")\n",
        "\n",
        "# DAX query to get the full dataset\n",
        "key_f_2 = \"\"\"\n",
        "DEFINE\n",
        "\tVAR __DS0FilterTable = \n",
        "\t\tFILTER(\n",
        "\t\t\tKEEPFILTERS(VALUES('FACT_MATTER'[referral_date])),\n",
        "\t\t\tAND(\n",
        "\t\t\t\t'FACT_MATTER'[referral_date] >= DATE(2023, 7, 1),\n",
        "\t\t\t\t'FACT_MATTER'[referral_date] < DATE(2025, 6, 2)\n",
        "\t\t\t)\n",
        "\t\t)\n",
        "\n",
        "\tVAR __DS0Core = \n",
        "\t\tSELECTCOLUMNS(\n",
        "\t\t\tKEEPFILTERS(\n",
        "\t\t\t\tFILTER(\n",
        "\t\t\t\t\tKEEPFILTERS(\n",
        "\t\t\t\t\t\tSUMMARIZECOLUMNS(\n",
        "\t\t\t\t\t\t\t'FACT_MATTER'[referral_date],\n",
        "\t\t\t\t\t\t\t'DIM_MATTER'[Case_reference],\n",
        "\t\t\t\t\t\t\t'DIM_ISSUE'[Keyword_group],\n",
        "\t\t\t\t\t\t\t'DIM_ISSUE'[Tier_1],\n",
        "\t\t\t\t\t\t\t'DIM_ISSUE'[Tier_2],\n",
        "\t\t\t\t\t\t\t'DIM_ISSUE'[Tier_2_full_names],\n",
        "\t\t\t\t\t\t\t'DIM_MATTER'[Summary],\n",
        "\t\t\t\t\t\t\t'DIM_ISSUE'[ServiceType_external_reports],\n",
        "\t\t\t\t\t\t\t__DS0FilterTable,\n",
        "\t\t\t\t\t\t\t\"CountRowsBRG_MATTER_ISSUE\", COUNTROWS('BRG_MATTER_ISSUE')\n",
        "\t\t\t\t\t\t)\n",
        "\t\t\t\t\t),\n",
        "\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\t\t\t\t\t\tOR(\n",
        "\t\t\t\t\t\t\t\t\t\t\t\tNOT(ISBLANK('FACT_MATTER'[referral_date])),\n",
        "\t\t\t\t\t\t\t\t\t\t\t\tNOT(ISBLANK('DIM_MATTER'[Case_reference]))\n",
        "\t\t\t\t\t\t\t\t\t\t\t),\n",
        "\t\t\t\t\t\t\t\t\t\t\tNOT(ISBLANK('DIM_ISSUE'[Keyword_group]))\n",
        "\t\t\t\t\t\t\t\t\t\t),\n",
        "\t\t\t\t\t\t\t\t\t\tNOT(ISBLANK('DIM_ISSUE'[Tier_1]))\n",
        "\t\t\t\t\t\t\t\t\t),\n",
        "\t\t\t\t\t\t\t\t\tNOT(ISBLANK('DIM_ISSUE'[Tier_2]))\n",
        "\t\t\t\t\t\t\t\t),\n",
        "\t\t\t\t\t\t\t\tNOT(ISBLANK('DIM_ISSUE'[Tier_2_full_names]))\n",
        "\t\t\t\t\t\t\t),\n",
        "\t\t\t\t\t\t\tNOT(ISBLANK('DIM_MATTER'[Summary]))\n",
        "\t\t\t\t\t\t),\n",
        "\t\t\t\t\t\tNOT(ISBLANK('DIM_ISSUE'[ServiceType_external_reports]))\n",
        "\t\t\t\t\t)\n",
        "\t\t\t\t)\n",
        "\t\t\t),\n",
        "\t\t\t\"'FACT_MATTER'[referral_date]\", 'FACT_MATTER'[referral_date],\n",
        "\t\t\t\"'DIM_MATTER'[Case_reference]\", 'DIM_MATTER'[Case_reference],\n",
        "\t\t\t\"'DIM_ISSUE'[Keyword_group]\", 'DIM_ISSUE'[Keyword_group],\n",
        "\t\t\t\"'DIM_ISSUE'[Tier_1]\", 'DIM_ISSUE'[Tier_1],\n",
        "\t\t\t\"'DIM_ISSUE'[Tier_2]\", 'DIM_ISSUE'[Tier_2],\n",
        "\t\t\t\"'DIM_ISSUE'[Tier_2_full_names]\", 'DIM_ISSUE'[Tier_2_full_names],\n",
        "\t\t\t\"'DIM_MATTER'[Summary]\", 'DIM_MATTER'[Summary],\n",
        "\t\t\t\"'DIM_ISSUE'[ServiceType_external_reports]\", 'DIM_ISSUE'[ServiceType_external_reports]\n",
        "\t\t)\n",
        "\n",
        "EVALUATE\n",
        "\t__DS0Core\n",
        "\n",
        "ORDER BY\n",
        "\t'FACT_MATTER'[referral_date] DESC,\n",
        "\t'DIM_MATTER'[Case_reference],\n",
        "\t'DIM_ISSUE'[Keyword_group],\n",
        "\t'DIM_ISSUE'[Tier_1],\n",
        "\t'DIM_ISSUE'[Tier_2],\n",
        "\t'DIM_ISSUE'[Tier_2_full_names],\n",
        "\t'DIM_MATTER'[Summary],\n",
        "\t'DIM_ISSUE'[ServiceType_external_reports]\n",
        "\"\"\"\n",
        "\n",
        "# Execute DAX query\n",
        "dx3 = fabric.evaluate_dax(dataset, key_f_2, workspace)\n",
        "\n",
        "# Rename columns to clean names\n",
        "df3 = dx3.rename(columns={\n",
        "    \"FACT_MATTER[referral_date]\": \"referral_date\",\n",
        "    \"DIM_MATTER[Case_reference]\": \"case_reference\",\n",
        "    \"DIM_ISSUE[Keyword_group]\": \"keyword_group\",\n",
        "    \"DIM_ISSUE[Tier_1]\": \"tier_1\",\n",
        "    \"DIM_ISSUE[Tier_2]\": \"tier_2\",\n",
        "    \"DIM_ISSUE[Tier_2_full_names]\": \"Tier_2_full_names\",\n",
        "    \"DIM_MATTER[Summary]\": \"summary\",\n",
        "    \"DIM_ISSUE[ServiceType_external_reports]\": \"Service\"\n",
        "})\n",
        "\n",
        "# Convert date column\n",
        "df3[\"referral_date\"] = pd.to_datetime(df3[\"referral_date\"]).dt.date\n",
        "\n",
        "print(f\"Loaded {len(df3):,} rows\")\n",
        "print(f\" Date range: {df3['referral_date'].min()} to {df3['referral_date'].max()}\")\n",
        "print(f\"\\n Dataset structure:\")\n",
        "display(df3.head())"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "import subprocess, sys\n",
        "for pkg in [\"transformers\", \"torch\", \"scikit-learn\", \"tqdm\", \"pandas\", \"numpy\", \"nbformat\"]:\n",
        "    subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", pkg, \"-q\"])\n",
        "try:\n",
        "    import cleanlab\n",
        "    print(\"cleanlab already installed\")\n",
        "except ImportError:\n",
        "    subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", \"cleanlab\", \"-q\"])\n",
        "    print(\"cleanlab installed\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html\n  from .autonotebook import tqdm as notebook_tqdm\n"
        },
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "cleanlab already installed\n"
        }
      ],
      "execution_count": 1,
      "metadata": {
        "gather": {
          "logged": 1779144727816
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# !pip install gensim nltk scipy"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Requirement already satisfied: gensim in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (4.4.0)\r\nRequirement already satisfied: nltk in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (3.9.4)\r\nRequirement already satisfied: scipy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (1.10.1)\r\nRequirement already satisfied: numpy>=1.18.5 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from gensim) (1.26.4)\r\nRequirement already satisfied: smart_open>=1.8.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from gensim) (6.4.0)\r\nRequirement already satisfied: click in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nltk) (8.3.1)\r\nRequirement already satisfied: joblib in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nltk) (1.5.3)\r\nRequirement already satisfied: regex>=2021.8.3 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nltk) (2025.11.3)\r\nRequirement already satisfied: tqdm in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nltk) (4.67.3)\r\n"
        }
      ],
      "execution_count": 34,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "# !pip install --upgrade \"scipy<1.11\" gensim"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Requirement already satisfied: scipy<1.11 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (1.10.1)\nRequirement already satisfied: gensim in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (4.4.0)\nRequirement already satisfied: numpy<1.27.0,>=1.19.5 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from scipy<1.11) (1.26.4)\nRequirement already satisfied: smart_open>=1.8.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from gensim) (6.4.0)\n"
        }
      ],
      "execution_count": 35,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "from gensim.models import FastText\n",
        "from nltk.tokenize import word_tokenize\n",
        "\n",
        "from scipy.sparse import hstack\n",
        "import nltk\n",
        "nltk.download('punkt')\n",
        "nltk.download('punkt_tab')\n",
        "\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "[nltk_data] Downloading package punkt to /home/azureuser/nltk_data...\n[nltk_data]   Package punkt is already up-to-date!\n[nltk_data] Downloading package punkt_tab to\n[nltk_data]     /home/azureuser/nltk_data...\n[nltk_data]   Package punkt_tab is already up-to-date!\n"
        },
        {
          "output_type": "execute_result",
          "execution_count": 1,
          "data": {
            "text/plain": "True"
          },
          "metadata": {}
        }
      ],
      "execution_count": 1,
      "metadata": {
        "gather": {
          "logged": 1779158343003
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import pandas as pd\n",
        "import numpy as np\n",
        "import torch\n",
        "import torch.nn as nn\n",
        "import ast, random, os, json\n",
        "from pathlib import Path\n",
        "from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler\n",
        "from transformers import AutoTokenizer, AutoModel, get_linear_schedule_with_warmup\n",
        "from torch.optim import AdamW\n",
        "from sklearn.preprocessing import MultiLabelBinarizer\n",
        "from sklearn.model_selection import train_test_split, cross_val_predict\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.linear_model import LogisticRegression\n",
        "from sklearn.multiclass import OneVsRestClassifier\n",
        "from sklearn.metrics import f1_score, classification_report\n",
        "from tqdm import tqdm\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/tqdm/auto.py:21: TqdmWarning: IProgress not found. Please update jupyter and ipywidgets. See https://ipywidgets.readthedocs.io/en/stable/user_install.html\n  from .autonotebook import tqdm as notebook_tqdm\n"
        }
      ],
      "execution_count": 2,
      "metadata": {
        "gather": {
          "logged": 1779158369934
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.multiclass import OneVsRestClassifier\n",
        "from sklearn.metrics import f1_score, classification_report\n",
        "import xgboost as xgb\n",
        "import lightgbm as lgb\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import os"
      ],
      "outputs": [],
      "execution_count": 3,
      "metadata": {
        "gather": {
          "logged": 1779158376996
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "# Block 6 — Load CleanLab-Cleaned Data & Train/Val/Test Split\n",
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import json\n",
        "from pathlib import Path\n",
        "from sklearn.model_selection import train_test_split\n",
        "from sklearn.preprocessing import MultiLabelBinarizer\n",
        "\n",
        "print(\"Loading CleanLab-cleaned data...\")\n",
        "\n",
        "# ── Load cleaned data from CleanLab Block 3 ───────────────────────────────────\n",
        "# df_clean = pd.read_csv('cleaned_for_training.csv')"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Loading CleanLab-cleaned data...\n"
        }
      ],
      "execution_count": 4,
      "metadata": {
        "gather": {
          "logged": 1779158377274
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# #DATA_FILE = 'C:\\\\Users\\\\KritiYadav\\\\Downloads\\\\Complaint_keyword_dynamic\\\\data_extracted_fabric\\\\shortlisted_3500_fabric.csv'   # <-- YOUR FILE HERE\n",
        "\n",
        "# def parse_tags(val):\n",
        "#     if isinstance(val, list): return [t.strip() for t in val if str(t).strip()]\n",
        "#     if isinstance(val, str):\n",
        "#         val = val.strip()\n",
        "#         if val.startswith('['):\n",
        "#             try: return [t.strip() for t in ast.literal_eval(val) if str(t).strip()]\n",
        "#             except: pass\n",
        "#         return [t.strip() for t in val.split(',') if t.strip()]\n",
        "#     return []\n",
        "\n",
        "# def parse_list_str(val):\n",
        "#     if isinstance(val, list): return val\n",
        "#     if isinstance(val, str) and val.startswith('['):\n",
        "#         try: return ast.literal_eval(val)\n",
        "#         except: pass\n",
        "#     return [val] if isinstance(val, str) and val.strip() else []\n",
        "# df_short=pd.read_csv(\n",
        "#     \"cleaned_for_training.csv\",\n",
        "#     encoding=\"utf-8\",\n",
        "#     on_bad_lines=\"skip\"\n",
        "# )\n",
        "# df = df_short\n",
        "# df['tags_parsed']          = df['tier_2'].apply(parse_tags)\n",
        "# # df['keyword_group_parsed'] = df['keyword_group'].apply(parse_list_str)\n",
        "# df = df[df['tags_parsed'].apply(len) > 0].reset_index(drop=True)\n",
        "\n",
        "# mlb = MultiLabelBinarizer()\n",
        "# y   = mlb.fit_transform(df['tags_parsed'])\n",
        "# tag_counts_s    = pd.Series(y.sum(axis=0), index=mlb.classes_).sort_values(ascending=False)\n",
        "# n_total         = len(df)\n",
        "# imbalance_ratio = tag_counts_s.max() / max(tag_counts_s.min(), 1)\n",
        "# tags_per_row    = y.sum(axis=1)\n",
        "\n",
        "# print(f\"Loaded: {n_total} complaints  |  {len(mlb.classes_)} unique tier_2 tags\")\n",
        "# print(f\"Avg tags/complaint: {tags_per_row.mean():.2f}  |  Imbalance ratio: {imbalance_ratio:.0f}x\")\n",
        "# print(f\"\\nTop 5 tags:\\n{tag_counts_s.head().to_string()}\")\n",
        "# print(f\"\\nBottom 5 tags:\\n{tag_counts_s.tail().to_string()}\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Loaded: 3409 complaints  |  94 unique tier_2 tags\nAvg tags/complaint: 2.42  |  Imbalance ratio: 945x\n\nTop 5 tags:\nNo or delayed action                945\nService and equipment               429\nNo service                          241\nResolution agreed but not met       231\nNon-financial loss - not privacy    186\n\nBottom 5 tags:\nExcess call/sms/mms charges     2\nInformation inaccurat           1\nPremature objection             1\nResolution agreed but not me    1\nDefective notice                1\n"
        }
      ],
      "execution_count": 5,
      "metadata": {
        "gather": {
          "logged": 1778543345960
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "\n",
        "# MIN_TAG_SAMPLES = max(3, min(10, int(n_total * 0.005)))\n",
        "# RARE_THRESHOLD  = max(10, int(n_total * 0.01))\n",
        "# DOMINANT_FREQ   = 0.50\n",
        "# RARE_FREQ       = max(0.02, min(0.08, 1.5 / len(mlb.classes_)))\n",
        "# KW_DROPOUT      = min(0.55, 0.20 + (min(imbalance_ratio, 100) / 200))\n",
        "# #BASE_SMOOTH     = round(min(0.15, max(0.02, 0.02 + (1.0 - avg_quality) * 0.25)), 3)\n",
        "# GAMMA_NEG       = int(min(6, max(2, 2 + min(imbalance_ratio, 100) / 30)))\n",
        "# EPOCHS          = max(5, min(12, int(20000 / n_total + 3)))\n",
        "# BATCH_SIZE      = 32 if n_total >= 5000 else 16 if n_total >= 1000 else 8\n",
        "# EARLY_STOP_PAT  = 3 if n_total >= 2000 else 4\n",
        "# LR              = 2e-5\n",
        "# med_chars       = df['summary'].dropna().str.len().median() if 'summary' in df.columns else 600\n",
        "# MAX_LEN         = 512 if med_chars > 1200 else 384 if med_chars > 600 else 256\n",
        "# DO_AUGMENT      = bool((tag_counts_s < RARE_THRESHOLD).any())\n",
        "# DO_UNDERSAMPLE  = bool(imbalance_ratio > 5 and (tag_counts_s / n_total > DOMINANT_FREQ).any())\n",
        "\n",
        "# print(\"DATA DIAGNOSIS REPORT\")\n",
        "# print(\"=\" * 55)\n",
        "# print(f\"  Total complaints:       {n_total}\")\n",
        "# print(f\"  Unique tier_2 tags:     {len(mlb.classes_)}\")\n",
        "# print(f\"  Avg tags/complaint:     {tags_per_row.mean():.2f}\")\n",
        "# print(f\"  Imbalance ratio:        {imbalance_ratio:.0f}x\")\n",
        "# print(f\"  Most common tag:        '{tag_counts_s.index[0]}' ({int(tag_counts_s.max())} samples)\")\n",
        "# print(f\"  Least common tag:       '{tag_counts_s.index[-1]}' ({int(tag_counts_s.min())} samples)\")\n",
        "# print(f\"  Tags < 10 samples:       {(tag_counts_s < 5).sum()}\")\n",
        "# print(f\"  Tags < {RARE_THRESHOLD} samples:      {(tag_counts_s < RARE_THRESHOLD).sum()} (will be augmented)\")\n",
        "# #print(f\"  CleanLab available:     {HAS_CLEANLAB}\")\n",
        "# #print(f\"  Avg label quality:      {avg_quality:.3f}\")\n",
        "# #print(f\"  Pct flagged noisy:      {pct_flagged*100:.1f}%\")\n",
        "# print(\"  AUTO-COMPUTED SETTINGS:\")\n",
        "# print(f\"  MIN_TAG_SAMPLES={MIN_TAG_SAMPLES}  RARE_THRESHOLD={RARE_THRESHOLD}  KW_DROPOUT={KW_DROPOUT:.2f}\")\n",
        "# #print(f\"  BASE_SMOOTH={BASE_SMOOTH}  GAMMA_NEG={GAMMA_NEG}  EPOCHS={EPOCHS}\")\n",
        "# print(f\"  BATCH_SIZE={BATCH_SIZE}  MAX_LEN={MAX_LEN}  LR={LR}\")\n",
        "# print(f\"  DO_AUGMENT={DO_AUGMENT}  DO_UNDERSAMPLE={DO_UNDERSAMPLE}\")\n",
        "# print(\"=\" * 55)\n"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1778688473691
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# valid_mask = y.sum(axis=0) >= MIN_TAG_SAMPLES\n",
        "# assert len(valid_mask) == len(mlb.classes_), \"Mismatch between y and mlb.classes_\"\n",
        "# dropped    = mlb.classes_[~valid_mask]\n",
        "# valid_tags = mlb.classes_[valid_mask]\n",
        "# y          = y[:, valid_mask]\n",
        "# NUM_LABELS = len(valid_tags)\n",
        "\n",
        "# print(f\"Kept: {NUM_LABELS} tags  |  Dropped: {len(dropped)} tags with < {MIN_TAG_SAMPLES} samples\")\n",
        "# if len(dropped): print(f\"Dropped tags: {list(dropped)}\")\n",
        "\n",
        "# keep = y.sum(axis=1) > 0\n",
        "# df, y = df[keep].reset_index(drop=True), y[keep]\n",
        "# print(f\"Complaints after filter: {len(df)}\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Kept: 87 tags  |  Dropped: 7 tags with < 10 samples\nDropped tags: ['Defective notice', 'Excess call/sms/mms charges', 'General telecommunications enquiry', 'Information inaccurat', 'Mishandling of business information', 'Premature objection', 'Resolution agreed but not me']\nComplaints after filter: 3409\n"
        }
      ],
      "execution_count": 7,
      "metadata": {
        "gather": {
          "logged": 1778543346371
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "### PLEASE NOTE \n",
        "Dropped tags: ['Defective notice', 'Excess call/sms/mms charges', 'General telecommunications enquiry', 'Information inaccurat', 'Mishandling of business information', 'Premature objection', 'Resolution agreed but not me']"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "df.head()"
      ],
      "outputs": [
        {
          "output_type": "execute_result",
          "execution_count": 7,
          "data": {
            "text/plain": "  case_reference referral_date  \\\n0  2023-04-03073    24/07/2023   \n1  2023-05-02999    19/09/2023   \n2  2023-06-05074     3/07/2023   \n3  2023-06-05657     4/07/2023   \n4  2023-06-05976     6/07/2023   \n\n                                             summary   Service  \\\n0  CONSUMER SUMMARY AND PROVIDER'S RESPONSE:\\n- C...  Property   \n1  Consumer summary:\\n(from online form completed...    Mobile   \n2  Consumer summary:\\n(from online form completed...  Multiple   \n3  Consumer summary:\\n(from online form completed...  Property   \n4  CONSUMER SUMMARY AND PROVIDER'S RESPONSE:\\n- C...    Mobile   \n\n                                       keyword_group  \\\n0             ['4- Customer service', '5- Property']   \n1  ['1- Establishing a service', '4- Customer ser...   \n2  ['1- Establishing a service', '3- Payment for ...   \n3                                    ['5- Property']   \n4                       ['3- Payment for a service']   \n\n                                              tier_1  \\\n0  ['Compensation sought', 'Damage', 'Infrastruct...   \n1         ['Making a contract', 'Provider response']   \n2  ['Charges and fees', 'In contract', 'Provider ...   \n3                                         ['Damage']   \n4                               ['Charges and fees']   \n\n                                              tier_2  \\\n0  ['By provider', 'Hazardous, non-compliant or t...   \n1  ['Misleading conduct', 'Resolution agreed but ...   \n2  ['Failure to cancel', 'Resolution agreed but n...   \n3                                    ['By provider']   \n4                                        ['Roaming']   \n\n                                   Tier_2_full_names  \\\n0  ['By provider', 'Hazardous, non-compliant or t...   \n1  ['Misleading conduct when making a contract', ...   \n2  ['Failure to cancel a service', 'Resolution ag...   \n3                                    ['By provider']   \n4                                        ['Roaming']   \n\n                      tier2_consolidated_description  num_tier_1  ...  \\\n0  Compensation sought + A consumer is seeking co...           3  ...   \n1  Making a contract + A provider misled the cons...           2  ...   \n2  In contract + Consumer has requested the servi...           3  ...   \n3                                             Damage           1  ...   \n4  Charges and fees + The consumer disputes charg...           1  ...   \n\n   summary_length  summary_word_count  \\\n0            1253                 227   \n1            2150                 395   \n2            1292                 201   \n3            2165                 374   \n4            1480                 263   \n\n                                         tags_parsed noise_score  \\\n0  [['By provider', 'Hazardous, non-compliant or ...    0.124371   \n1  [['Misleading conduct', 'Resolution agreed but...    0.124371   \n2  [['Failure to cancel', 'Resolution agreed but ...    0.124371   \n3                                  [['By provider']]    0.497845   \n4                                      [['Roaming']]    0.497845   \n\n                                           tags_list  \\\n0  ['By provider', 'Hazardous non-compliant or te...   \n1  ['Misleading conduct', 'Resolution agreed but ...   \n2  ['Failure to cancel', 'Resolution agreed but n...   \n3                                    ['By provider']   \n4                                        ['Roaming']   \n\n                           tier2_description_example  \\\n0  By provider: A member or carrier, e.g. Telstra...   \n1  Misleading conduct: A provider misled the cons...   \n2  Failure to cancel: Consumer has requested the ...   \n3  By provider: A member or carrier, e.g. Telstra...   \n4  Roaming: The consumer disputes charges for roa...   \n\n                                 cleanlab_input_text  \\\n0  Property CONSUMER SUMMARY AND PROVIDER'S RESPO...   \n1  Mobile Consumer summary:\\n(from online form co...   \n2  Multiple Consumer summary:\\n(from online form ...   \n3  Property Consumer summary:\\n(from online form ...   \n4  Mobile CONSUMER SUMMARY AND PROVIDER'S RESPONS...   \n\n                                      tier_2_cleaned tags_removed  \\\n0  ['By provider', 'Hazardous non-compliant or te...          NaN   \n1  ['Misleading conduct', 'Resolution agreed but ...          NaN   \n2  ['Failure to cancel', 'Resolution agreed but n...          NaN   \n3                                    ['By provider']          NaN   \n4                                        ['Roaming']          NaN   \n\n  tags_flagged_for_review  \n0                     NaN  \n1                     NaN  \n2                     NaN  \n3                     NaN  \n4                     NaN  \n\n[5 rows x 21 columns]",
            "text/html": "<div>\n<style scoped>\n    .dataframe tbody tr th:only-of-type {\n        vertical-align: middle;\n    }\n\n    .dataframe tbody tr th {\n        vertical-align: top;\n    }\n\n    .dataframe thead th {\n        text-align: right;\n    }\n</style>\n<table border=\"1\" class=\"dataframe\">\n  <thead>\n    <tr style=\"text-align: right;\">\n      <th></th>\n      <th>case_reference</th>\n      <th>referral_date</th>\n      <th>summary</th>\n      <th>Service</th>\n      <th>keyword_group</th>\n      <th>tier_1</th>\n      <th>tier_2</th>\n      <th>Tier_2_full_names</th>\n      <th>tier2_consolidated_description</th>\n      <th>num_tier_1</th>\n      <th>...</th>\n      <th>summary_length</th>\n      <th>summary_word_count</th>\n      <th>tags_parsed</th>\n      <th>noise_score</th>\n      <th>tags_list</th>\n      <th>tier2_description_example</th>\n      <th>cleanlab_input_text</th>\n      <th>tier_2_cleaned</th>\n      <th>tags_removed</th>\n      <th>tags_flagged_for_review</th>\n    </tr>\n  </thead>\n  <tbody>\n    <tr>\n      <th>0</th>\n      <td>2023-04-03073</td>\n      <td>24/07/2023</td>\n      <td>CONSUMER SUMMARY AND PROVIDER'S RESPONSE:\\n- C...</td>\n      <td>Property</td>\n      <td>['4- Customer service', '5- Property']</td>\n      <td>['Compensation sought', 'Damage', 'Infrastruct...</td>\n      <td>['By provider', 'Hazardous, non-compliant or t...</td>\n      <td>['By provider', 'Hazardous, non-compliant or t...</td>\n      <td>Compensation sought + A consumer is seeking co...</td>\n      <td>3</td>\n      <td>...</td>\n      <td>1253</td>\n      <td>227</td>\n      <td>[['By provider', 'Hazardous, non-compliant or ...</td>\n      <td>0.124371</td>\n      <td>['By provider', 'Hazardous non-compliant or te...</td>\n      <td>By provider: A member or carrier, e.g. Telstra...</td>\n      <td>Property CONSUMER SUMMARY AND PROVIDER'S RESPO...</td>\n      <td>['By provider', 'Hazardous non-compliant or te...</td>\n      <td>NaN</td>\n      <td>NaN</td>\n    </tr>\n    <tr>\n      <th>1</th>\n      <td>2023-05-02999</td>\n      <td>19/09/2023</td>\n      <td>Consumer summary:\\n(from online form completed...</td>\n      <td>Mobile</td>\n      <td>['1- Establishing a service', '4- Customer ser...</td>\n      <td>['Making a contract', 'Provider response']</td>\n      <td>['Misleading conduct', 'Resolution agreed but ...</td>\n      <td>['Misleading conduct when making a contract', ...</td>\n      <td>Making a contract + A provider misled the cons...</td>\n      <td>2</td>\n      <td>...</td>\n      <td>2150</td>\n      <td>395</td>\n      <td>[['Misleading conduct', 'Resolution agreed but...</td>\n      <td>0.124371</td>\n      <td>['Misleading conduct', 'Resolution agreed but ...</td>\n      <td>Misleading conduct: A provider misled the cons...</td>\n      <td>Mobile Consumer summary:\\n(from online form co...</td>\n      <td>['Misleading conduct', 'Resolution agreed but ...</td>\n      <td>NaN</td>\n      <td>NaN</td>\n    </tr>\n    <tr>\n      <th>2</th>\n      <td>2023-06-05074</td>\n      <td>3/07/2023</td>\n      <td>Consumer summary:\\n(from online form completed...</td>\n      <td>Multiple</td>\n      <td>['1- Establishing a service', '3- Payment for ...</td>\n      <td>['Charges and fees', 'In contract', 'Provider ...</td>\n      <td>['Failure to cancel', 'Resolution agreed but n...</td>\n      <td>['Failure to cancel a service', 'Resolution ag...</td>\n      <td>In contract + Consumer has requested the servi...</td>\n      <td>3</td>\n      <td>...</td>\n      <td>1292</td>\n      <td>201</td>\n      <td>[['Failure to cancel', 'Resolution agreed but ...</td>\n      <td>0.124371</td>\n      <td>['Failure to cancel', 'Resolution agreed but n...</td>\n      <td>Failure to cancel: Consumer has requested the ...</td>\n      <td>Multiple Consumer summary:\\n(from online form ...</td>\n      <td>['Failure to cancel', 'Resolution agreed but n...</td>\n      <td>NaN</td>\n      <td>NaN</td>\n    </tr>\n    <tr>\n      <th>3</th>\n      <td>2023-06-05657</td>\n      <td>4/07/2023</td>\n      <td>Consumer summary:\\n(from online form completed...</td>\n      <td>Property</td>\n      <td>['5- Property']</td>\n      <td>['Damage']</td>\n      <td>['By provider']</td>\n      <td>['By provider']</td>\n      <td>Damage</td>\n      <td>1</td>\n      <td>...</td>\n      <td>2165</td>\n      <td>374</td>\n      <td>[['By provider']]</td>\n      <td>0.497845</td>\n      <td>['By provider']</td>\n      <td>By provider: A member or carrier, e.g. Telstra...</td>\n      <td>Property Consumer summary:\\n(from online form ...</td>\n      <td>['By provider']</td>\n      <td>NaN</td>\n      <td>NaN</td>\n    </tr>\n    <tr>\n      <th>4</th>\n      <td>2023-06-05976</td>\n      <td>6/07/2023</td>\n      <td>CONSUMER SUMMARY AND PROVIDER'S RESPONSE:\\n- C...</td>\n      <td>Mobile</td>\n      <td>['3- Payment for a service']</td>\n      <td>['Charges and fees']</td>\n      <td>['Roaming']</td>\n      <td>['Roaming']</td>\n      <td>Charges and fees + The consumer disputes charg...</td>\n      <td>1</td>\n      <td>...</td>\n      <td>1480</td>\n      <td>263</td>\n      <td>[['Roaming']]</td>\n      <td>0.497845</td>\n      <td>['Roaming']</td>\n      <td>Roaming: The consumer disputes charges for roa...</td>\n      <td>Mobile CONSUMER SUMMARY AND PROVIDER'S RESPONS...</td>\n      <td>['Roaming']</td>\n      <td>NaN</td>\n      <td>NaN</td>\n    </tr>\n  </tbody>\n</table>\n<p>5 rows × 21 columns</p>\n</div>"
          },
          "metadata": {}
        }
      ],
      "execution_count": 7,
      "metadata": {
        "gather": {
          "logged": 1778475059037
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "df_clean=df"
      ],
      "outputs": [],
      "execution_count": 9,
      "metadata": {
        "gather": {
          "logged": 1778489139830
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "df=pd.read_csv(\"saved_data/cleaned_for_training_q592.csv\")"
      ],
      "outputs": [],
      "execution_count": 5,
      "metadata": {
        "gather": {
          "logged": 1779158377746
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "# ENHANCE tier2_description_example FOR RARE TAG COMPLAINTS\n",
        "# In-place transformation: add LLM enrichment to rare tag cases only\n",
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "\n",
        "import pandas as pd\n",
        "import ast\n",
        "\n",
        "print(f\"{'='*80}\")\n",
        "print(f\"ENHANCING RARE TAG COMPLAINTS WITH LLM ENRICHMENT\")\n",
        "print(f\"{'='*80}\\n\")\n",
        "\n",
        "# ── Parse tags helper ─────────────────────────────────────────────────────────\n",
        "def parse_tags(val):\n",
        "    if isinstance(val, list): \n",
        "        return [t.strip() for t in val if str(t).strip()]\n",
        "    if isinstance(val, str):\n",
        "        val = val.strip()\n",
        "        if val.startswith('['):\n",
        "            try: \n",
        "                return [t.strip() for t in ast.literal_eval(val) if str(t).strip()]\n",
        "            except: \n",
        "                pass\n",
        "        return [t.strip() for t in val.split(',') if t.strip()]\n",
        "    return []\n",
        "\n",
        "# ── Load enriched data ────────────────────────────────────────────────────────\n",
        "print(f\"✓ Loaded: {len(df):,} complaints\\n\")\n",
        "\n",
        "# Parse tags\n",
        "df['tags_list'] = df['tier_2'].apply(parse_tags)\n",
        "\n",
        "# ── Identify rare tags from canonical_tag_map_enriched.csv ───────────────────\n",
        "tag_map = pd.read_csv('saved_data/canonical_tag_map_enriched.csv')\n",
        "rare_tags = set(tag_map[tag_map['is_rare'] == True]['canonical_tag'].tolist())\n",
        "\n",
        "print(f\"Rare tags: {len(rare_tags)}\")\n",
        "print(f\"Sample rare tags: {list(rare_tags)[:5]}\\n\")\n",
        "\n",
        "# ── Identify complaints with rare tags ────────────────────────────────────────\n",
        "def has_rare_tag(tags_list, rare_tag_set):\n",
        "    \"\"\"Check if complaint has any rare tags\"\"\"\n",
        "    return any(tag in rare_tag_set for tag in tags_list)\n",
        "\n",
        "df['has_rare_tag'] = df['tags_list'].apply(lambda tl: has_rare_tag(tl, rare_tags))\n",
        "rare_count = df['has_rare_tag'].sum()\n",
        "\n",
        "print(f\"Complaints with rare tags: {rare_count:,}/{len(df):,} ({rare_count/len(df)*100:.1f}%)\\n\")\n",
        "\n",
        "# ── Enhance tier2_description_example for rare tag complaints ────────────────\n",
        "print(f\"{'─'*80}\")\n",
        "print(f\"Updating tier2_description_example column...\")\n",
        "print(f\"{'─'*80}\\n\")\n",
        "\n",
        "def enhance_if_rare(row):\n",
        "    \"\"\"\n",
        "    If complaint has rare tag AND has LLM enrichment:\n",
        "        Combine tier2_description_example + tier2_llm_enrichment\n",
        "    Otherwise:\n",
        "        Keep tier2_description_example as is\n",
        "    \"\"\"\n",
        "    if not row['has_rare_tag']:\n",
        "        # No rare tags - keep original\n",
        "        return row['tier2_description_example']\n",
        "    \n",
        "    # Has rare tags - check if LLM enrichment exists\n",
        "    desc_ex = str(row.get('tier2_description_example', '')).strip()\n",
        "    llm_enrich = str(row.get('tier2_llm_enrichment', '')).strip()\n",
        "    \n",
        "    # Clean 'nan' strings\n",
        "    if desc_ex.lower() == 'nan': desc_ex = ''\n",
        "    if llm_enrich.lower() == 'nan': llm_enrich = ''\n",
        "    \n",
        "    # If both exist, combine them\n",
        "    if desc_ex and llm_enrich:\n",
        "        return f\"{desc_ex} [LLM_ENRICH] {llm_enrich}\"\n",
        "    else:\n",
        "        # Only one exists or neither - return what we have\n",
        "        return desc_ex\n",
        "\n",
        "# Apply enhancement\n",
        "original_lens = df['tier2_description_example'].str.len()\n",
        "df['tier2_description_example'] = df.apply(enhance_if_rare, axis=1)\n",
        "enhanced_lens = df['tier2_description_example'].str.len()\n",
        "\n",
        "# Count how many were actually enhanced\n",
        "enhanced_count = df[df['tier2_description_example'].str.contains('[LLM_ENRICH]', regex=False, na=False)].shape[0]\n",
        "\n",
        "print(f\"✓ Enhancement complete!\")\n",
        "print(f\"  Complaints enhanced: {enhanced_count:,}/{rare_count:,} rare tag complaints\")\n",
        "print(f\"  Complaints unchanged: {len(df) - enhanced_count:,}\\n\")\n",
        "\n",
        "# ── Length comparison ─────────────────────────────────────────────────────────\n",
        "print(f\"{'─'*80}\")\n",
        "print(f\"Text length comparison:\")\n",
        "print(f\"{'─'*80}\\n\")\n",
        "\n",
        "print(f\"Before enhancement (ALL):\")\n",
        "print(f\"  Mean: {original_lens.mean():.0f} chars\")\n",
        "print(f\"  Max:  {original_lens.max():.0f} chars\")\n",
        "\n",
        "print(f\"\\nAfter enhancement (ALL):\")\n",
        "print(f\"  Mean: {enhanced_lens.mean():.0f} chars\")\n",
        "print(f\"  Max:  {enhanced_lens.max():.0f} chars\")\n",
        "\n",
        "rare_mask = df['has_rare_tag']\n",
        "print(f\"\\nAfter enhancement (RARE TAG COMPLAINTS ONLY):\")\n",
        "print(f\"  Mean: {enhanced_lens[rare_mask].mean():.0f} chars\")\n",
        "print(f\"  Max:  {enhanced_lens[rare_mask].max():.0f} chars\")\n",
        "\n",
        "# ── Sample comparison ─────────────────────────────────────────────────────────\n",
        "print(f\"\\n{'='*80}\")\n",
        "print(f\"SAMPLE COMPARISON\")\n",
        "print(f\"{'='*80}\\n\")\n",
        "\n",
        "enhanced_sample = df[df['tier2_description_example'].str.contains('[LLM_ENRICH]', regex=False, na=False)]\n",
        "if len(enhanced_sample) > 0:\n",
        "    sample = enhanced_sample.iloc[0]\n",
        "    \n",
        "    print(f\"Case: {sample['case_reference']}\")\n",
        "    print(f\"Tags: {sample['tier_2'][:100]}...\")\n",
        "    print(f\"Has rare tag: {sample['has_rare_tag']}\")\n",
        "    \n",
        "    print(f\"\\n{'─'*80}\")\n",
        "    print(f\"ENHANCED tier2_description_example (first 600 chars):\")\n",
        "    print(f\"{'─'*80}\")\n",
        "    enhanced_text = sample['tier2_description_example']\n",
        "    print(enhanced_text[:600])\n",
        "    if len(enhanced_text) > 600:\n",
        "        print(\"...\")\n",
        "    \n",
        "    # Show where LLM enrichment starts\n",
        "    if '[LLM_ENRICH]' in enhanced_text:\n",
        "        llm_start = enhanced_text.find('[LLM_ENRICH]')\n",
        "        print(f\"\\n  LLM enrichment starts at character {llm_start}\")\n",
        "\n",
        "# ── Save updated file ─────────────────────────────────────────────────────────\n",
        "print(f\"\\n{'='*80}\")\n",
        "print(f\"SAVING UPDATED FILE\")\n",
        "print(f\"{'='*80}\\n\")\n",
        "\n",
        "# Drop temporary column\n",
        "df_output = df.drop(columns=['tags_list', 'has_rare_tag'])\n",
        "\n",
        "# Backup existing file\n",
        "import shutil\n",
        "from pathlib import Path\n",
        "\n",
        "backup_path = 'saved_data/shortlisted_3500_canonical_enriched.csv.backup2'\n",
        "if Path('saved_data/shortlisted_3500_canonical_enriched.csv').exists():\n",
        "    shutil.copy(\n",
        "        'saved_data/shortlisted_3500_canonical_enriched.csv',\n",
        "        backup_path\n",
        "    )\n",
        "    print(f\"✓ Backed up to: {backup_path}\")\n",
        "\n",
        "# Save\n",
        "df_output.to_csv('saved_data/shortlisted_3500_canonical_enriched.csv', index=False)\n",
        "\n",
        "print(f\"✓ Saved: saved_data/shortlisted_3500_canonical_enriched.csv\")\n",
        "print(f\"  Rows: {len(df_output):,}\")\n",
        "print(f\"  Columns: {len(df_output.columns)}\\n\")\n",
        "\n",
        "# ── Summary ───────────────────────────────────────────────────────────────────\n",
        "print(f\"{'='*80}\")\n",
        "print(f\"SUMMARY\")\n",
        "print(f\"{'='*80}\")\n",
        "print(f\"\\nWhat changed:\")\n",
        "print(f\"  ✓ {enhanced_count:,} complaints with rare tags got LLM enrichment added\")\n",
        "print(f\"  ✓ {len(df) - enhanced_count:,} complaints unchanged (no rare tags or no LLM data)\")\n",
        "print(f\"  ✓ tier2_description_example column updated in-place\")\n",
        "print(f\"  ✓ All other columns preserved\")\n",
        "print(f\"\\nFormat:\")\n",
        "print(f\"  Regular:  [description] EXAMPLE 1: [...] [SEP] ...\")\n",
        "print(f\"  Enhanced: [description] EXAMPLE 1: [...] [LLM_ENRICH] [llm enrichment] [SEP] ...\")\n",
        "print(f\"\\nNext step:\")\n",
        "print(f\"  Use this file for training - rare tag complaints have richer context!\")\n",
        "print(f\"{'='*80}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "================================================================================\nENHANCING RARE TAG COMPLAINTS WITH LLM ENRICHMENT\n================================================================================\n\n✓ Loaded: 3,316 complaints\n\nRare tags: 20\nSample rare tags: ['Mishandling of business information', 'Premature objection', 'By consumer', 'Defective notice', '3rd party']\n\nComplaints with rare tags: 344/3,316 (10.4%)\n\n────────────────────────────────────────────────────────────────────────────────\nUpdating tier2_description_example column...\n────────────────────────────────────────────────────────────────────────────────\n\n✓ Enhancement complete!\n  Complaints enhanced: 344/344 rare tag complaints\n  Complaints unchanged: 2,972\n\n────────────────────────────────────────────────────────────────────────────────\nText length comparison:\n────────────────────────────────────────────────────────────────────────────────\n\nBefore enhancement (ALL):\n  Mean: 1883 chars\n  Max:  8161 chars\n\nAfter enhancement (ALL):\n  Mean: 2190 chars\n  Max:  28314 chars\n\nAfter enhancement (RARE TAG COMPLAINTS ONLY):\n  Mean: 4817 chars\n  Max:  28314 chars\n\n================================================================================\nSAMPLE COMPARISON\n================================================================================\n\nCase: 2023-06-06537\nTags: ['Cooling off', 'Inadequate explanation of product', 'Termination']...\nHas rare tag: True\n\n────────────────────────────────────────────────────────────────────────────────\nENHANCED tier2_description_example (first 600 chars):\n────────────────────────────────────────────────────────────────────────────────\nThe consumer disputes a charge for ending a contract EXAMPLE: The consumer disputes the charges & claims he has made the final payment. I understand the matter is about the consumer has asked to cancel a service & has been advised he owes a further $1140 with no further detail or information provided. Consumer impact: Pre 1 July 2025 complaint - Please refer to complaint description Provider Response: Pre 1 July 2025 complaint - Please refer to complaint description Consumer seeking: Accept the $87.72 that was told was what I owe for the account which includes the device and any outstanding fe\n...\n\n  LLM enrichment starts at character 658\n\n================================================================================\nSAVING UPDATED FILE\n================================================================================\n\n✓ Backed up to: saved_data/shortlisted_3500_canonical_enriched.csv.backup2\n✓ Saved: saved_data/shortlisted_3500_canonical_enriched.csv\n  Rows: 3,316\n  Columns: 24\n\n================================================================================\nSUMMARY\n================================================================================\n\nWhat changed:\n  ✓ 344 complaints with rare tags got LLM enrichment added\n  ✓ 2,972 complaints unchanged (no rare tags or no LLM data)\n  ✓ tier2_description_example column updated in-place\n  ✓ All other columns preserved\n\nFormat:\n  Regular:  [description] EXAMPLE 1: [...] [SEP] ...\n  Enhanced: [description] EXAMPLE 1: [...] [LLM_ENRICH] [llm enrichment] [SEP] ...\n\nNext step:\n  Use this file for training - rare tag complaints have richer context!\n================================================================================\n"
        }
      ],
      "execution_count": 6,
      "metadata": {
        "gather": {
          "logged": 1779158379010
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "df_clean=df_output"
      ],
      "outputs": [],
      "execution_count": 7,
      "metadata": {
        "gather": {
          "logged": 1779158379498
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "\n",
        "def parse_tags(val):\n",
        "    if isinstance(val, list): return [t.strip() for t in val if str(t).strip()]\n",
        "    if isinstance(val, str):\n",
        "        val = val.strip()\n",
        "        if val.startswith('['):\n",
        "            try: return [t.strip() for t in ast.literal_eval(val) if str(t).strip()]\n",
        "            except: pass\n",
        "        return [t.strip() for t in val.split(',') if t.strip()]\n",
        "    return []\n",
        "\n",
        "# ── Parse CLEANED tags (tier_2_cleaned column from CleanLab) ──────────────────\n",
        "df_clean['tags_list'] = df_clean['tier_2'].apply(parse_tags)\n",
        "df_clean = df_clean[df_clean['tags_list'].apply(len) > 0].reset_index(drop=True)\n",
        "\n",
        "print(f\"Loaded cleaned data: {len(df_clean):,} complaints (after noisy label removal)\")\n",
        "\n",
        "# ── Rebuild label matrix with cleaned tags ────────────────────────────────────\n",
        "mlb = MultiLabelBinarizer()\n",
        "y = mlb.fit_transform(df_clean['tags_list'])\n",
        "valid_tags = mlb.classes_\n",
        "NUM_LABELS = len(valid_tags)\n",
        "\n",
        "tag_counts = y.sum(axis=0)\n",
        "tag_counts_s = pd.Series(tag_counts, index=valid_tags).sort_values(ascending=False)\n",
        "\n",
        "print(f\"Unique tags after CleanLab: {NUM_LABELS}\")\n",
        "print(f\"Avg tags/complaint: {y.sum(axis=1).mean():.2f}\")\n",
        "print(f\"\\nTop 10 tags (cleaned data):\")\n",
        "print(tag_counts_s.head(10).to_string())\n",
        "\n",
        "# ── Verify we have cleaned descriptions ───────────────────────────────────────\n",
        "if 'tier2_description_example_cleaned' not in df_clean.columns:\n",
        "    print(\"\\n⚠ WARNING: tier2_description_example_cleaned column not found!\")\n",
        "    print(\"  CleanLab Block 3 should have created this column.\")\n",
        "    print(\"  Falling back to tier2_description_example (original)\")\n",
        "    df_clean['tier2_description_example_cleaned'] = df_clean['tier2_description_example']\n",
        "\n",
        "# ── Train / Val / Test split (before any augmentation) ─────────────────────────\n",
        "idx = np.arange(len(df_clean))\n",
        "tr_idx, temp = train_test_split(idx, test_size=0.2, random_state=42)\n",
        "val_idx, te_idx = train_test_split(temp, test_size=0.5, random_state=42)\n",
        "\n",
        "df_tr, y_tr = df_clean.iloc[tr_idx].reset_index(drop=True), y[tr_idx]\n",
        "df_val, y_val = df_clean.iloc[val_idx].reset_index(drop=True), y[val_idx]\n",
        "df_te, y_te = df_clean.iloc[te_idx].reset_index(drop=True), y[te_idx]\n",
        "\n",
        "# ── Save splits ────────────────────────────────────────────────────────────────\n",
        "df_tr.to_csv('saved_data/train_split_cleaned.csv', index=False)\n",
        "df_val.to_csv('saved_data/val_split_cleaned.csv', index=False)\n",
        "df_te.to_csv('saved_data/test_split_cleaned.csv', index=False)\n",
        "np.save('saved_data/y_tr_cleaned.npy', y_tr)\n",
        "np.save('saved_data/y_val_cleaned.npy', y_val)\n",
        "np.save('saved_data/y_te_cleaned.npy', y_te)\n",
        "\n",
        "# Save valid tags for reference\n",
        "with open('saved_data/valid_tags_cleaned.json', 'w') as f:\n",
        "    json.dump(list(valid_tags), f)\n",
        "\n",
        "print(f\"\\nSplit sizes:\")\n",
        "print(f\"  Train: {len(df_tr):,} ({len(df_tr)/len(df_clean)*100:.1f}%)\")\n",
        "print(f\"  Val:   {len(df_val):,} ({len(df_val)/len(df_clean)*100:.1f}%)\")\n",
        "print(f\"  Test:  {len(df_te):,} ({len(df_te)/len(df_clean)*100:.1f}%)\")\n",
        "\n",
        "print(f\"\\nSaved splits to saved_data/:\")\n",
        "print(f\"  - train_split_cleaned.csv / val_split_cleaned.csv / test_split_cleaned.csv\")\n",
        "print(f\"  - y_tr_cleaned.npy / y_val_cleaned.npy / y_te_cleaned.npy\")\n",
        "print(f\"  - valid_tags_cleaned.json\")\n",
        "print(\"Computing settings for imbalance handling...\")\n",
        "\n",
        "\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Loaded cleaned data: 3,316 complaints (after noisy label removal)\nUnique tags after CleanLab: 88\nAvg tags/complaint: 2.44\n\nTop 10 tags (cleaned data):\nNo or delayed action                                    944\nService and equipment                                   441\nNo service                                              240\nResolution agreed but not met                           231\nHazardous, non-compliant or temporary infrastructure    226\nNon-financial loss - not privacy                        186\nInadequate fault testing                                175\nLocation of equipment                                   170\nBy provider                                             162\nEnhanced/add-on feature                                 159\n\n⚠ WARNING: tier2_description_example_cleaned column not found!\n  CleanLab Block 3 should have created this column.\n  Falling back to tier2_description_example (original)\n\nSplit sizes:\n  Train: 2,652 (80.0%)\n  Val:   332 (10.0%)\n  Test:  332 (10.0%)\n\nSaved splits to saved_data/:\n  - train_split_cleaned.csv / val_split_cleaned.csv / test_split_cleaned.csv\n  - y_tr_cleaned.npy / y_val_cleaned.npy / y_te_cleaned.npy\n  - valid_tags_cleaned.json\nComputing settings for imbalance handling...\n"
        }
      ],
      "execution_count": 8,
      "metadata": {
        "gather": {
          "logged": 1779158389737
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ── Basic statistics ───────────────────────────────────────────────────────────\n",
        "n_total = len(df_clean)\n",
        "tag_counts = y.sum(axis=0)\n",
        "tag_counts_s = pd.Series(tag_counts, index=valid_tags).sort_values(ascending=False)\n",
        "tags_per_row = y.sum(axis=1)\n",
        "imbalance_ratio = tag_counts_s.max() / max(tag_counts_s.min(), 1)\n",
        "\n",
        "# ── Compute thresholds ─────────────────────────────────────────────────────────\n",
        "RARE_THRESHOLD = max(10, int(n_total * 0.01))\n",
        "DOMINANT_FREQ = 0.50\n",
        "RARE_FREQ = max(0.02, min(0.08, 1.5 / NUM_LABELS))\n",
        "\n",
        "# ── Decide whether to augment/undersample ─────────────────────────────────────\n",
        "DO_AUGMENT = bool((tag_counts_s < RARE_THRESHOLD).any())\n",
        "DO_UNDERSAMPLE = bool(imbalance_ratio > 5 and (tag_counts_s / n_total > DOMINANT_FREQ).any())\n",
        "\n",
        "# ── Compute noise-based smoothing ─────────────────────────────────────────────\n",
        "if 'noise_score' in df_clean.columns:\n",
        "    avg_noise = df_clean['noise_score'].mean()\n",
        "    BASE_SMOOTH = round(min(0.15, max(0.02, 0.02 + avg_noise * 0.25)), 3)\n",
        "else:\n",
        "    avg_noise = 0.0\n",
        "    BASE_SMOOTH = 0.05\n",
        "\n",
        "# ── Other training settings ────────────────────────────────────────────────────\n",
        "GAMMA_NEG = int(min(6, max(2, 2 + min(imbalance_ratio, 100) / 30)))\n",
        "EPOCHS = max(5, min(12, int(20000 / n_total + 3)))\n",
        "BATCH_SIZE = 32 if n_total >= 5000 else 16 if n_total >= 1000 else 8\n",
        "EARLY_STOP_PAT = 3 if n_total >= 2000 else 4\n",
        "LR = 2e-5\n",
        "\n",
        "# Compute MAX_LEN based on summary length\n",
        "if 'summary' in df_clean.columns:\n",
        "    med_chars = df_clean['summary'].dropna().str.len().median()\n",
        "else:\n",
        "    med_chars = 600\n",
        "MAX_LEN = 512 if med_chars > 1200 else 384 if med_chars > 600 else 256\n"
      ],
      "outputs": [],
      "execution_count": 10,
      "metadata": {
        "gather": {
          "logged": 1779158406172
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# df_clean.to_csv('saved_data/df_clean_before_block7_imbalance.csv', index=False)"
      ],
      "outputs": [],
      "execution_count": 10,
      "metadata": {
        "gather": {
          "logged": 1778690363867
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ── Training set statistics ────────────────────────────────────────────────────\n",
        "tag_counts_tr = y_tr.sum(axis=0)\n",
        "tag_freq_tr = tag_counts_tr / len(y_tr)\n",
        "\n",
        "rare_tags_count = int((tag_counts_tr < RARE_THRESHOLD).sum())\n",
        "dominant_tags_count = int((tag_freq_tr > DOMINANT_FREQ).sum())\n",
        "\n",
        "print(f\"\\n{'='*70}\")\n",
        "print(f\"SETTINGS FOR BLOCK 7 (Imbalance Handling)\")\n",
        "print(f\"{'='*70}\")\n",
        "print(f\"Data Statistics:\")\n",
        "print(f\"  Total complaints (cleaned):  {n_total:,}\")\n",
        "print(f\"  Unique tags:                 {NUM_LABELS}\")\n",
        "print(f\"  Avg tags/complaint:          {tags_per_row.mean():.2f}\")\n",
        "print(f\"  Imbalance ratio:             {imbalance_ratio:.0f}x\")\n",
        "print(f\"\\nTraining Set:\")\n",
        "print(f\"  Train size:                  {len(df_tr):,}\")\n",
        "print(f\"  Tags < {RARE_THRESHOLD} samples:       {rare_tags_count} (will augment)\")\n",
        "print(f\"  Tags > {DOMINANT_FREQ*100:.0f}% frequency:     {dominant_tags_count} (will undersample)\")\n",
        "print(f\"\\nComputed Settings:\")\n",
        "print(f\"  DO_AUGMENT:                  {DO_AUGMENT}\")\n",
        "print(f\"  DO_UNDERSAMPLE:              {DO_UNDERSAMPLE}\")\n",
        "print(f\"  RARE_THRESHOLD:              {RARE_THRESHOLD}\")\n",
        "print(f\"  DOMINANT_FREQ:               {DOMINANT_FREQ}\")\n",
        "print(f\"  RARE_FREQ:                   {RARE_FREQ:.4f}\")\n",
        "print(f\"  BASE_SMOOTH:                 {BASE_SMOOTH}\")\n",
        "print(f\"  GAMMA_NEG:                   {GAMMA_NEG}\")\n",
        "print(f\"\\nTraining Hyperparameters:\")\n",
        "print(f\"  EPOCHS:                      {EPOCHS}\")\n",
        "print(f\"  BATCH_SIZE:                  {BATCH_SIZE}\")\n",
        "print(f\"  MAX_LEN:                     {MAX_LEN}\")\n",
        "print(f\"  LR:                          {LR}\")\n",
        "print(f\"  EARLY_STOP_PAT:              {EARLY_STOP_PAT}\")\n",
        "print(f\"{'='*70}\")\n",
        "\n",
        "if rare_tags_count > 0:\n",
        "    print(f\"\\nRare tags to be augmented:\")\n",
        "    rare_tag_names = [valid_tags[i] for i in range(len(valid_tags)) if tag_counts_tr[i] < RARE_THRESHOLD]\n",
        "    for tag in rare_tag_names[:10]:  # Show first 10\n",
        "        count = tag_counts_tr[list(valid_tags).index(tag)]\n",
        "        print(f\"  - {tag:<40} ({count} samples)\")\n",
        "    if len(rare_tag_names) > 10:\n",
        "        print(f\"  ... and {len(rare_tag_names) - 10} more\")\n",
        "\n",
        "if dominant_tags_count > 0:\n",
        "    print(f\"\\nDominant tags (for undersampling):\")\n",
        "    dominant_tag_names = [valid_tags[i] for i in range(len(valid_tags)) if tag_freq_tr[i] > DOMINANT_FREQ]\n",
        "    for tag in dominant_tag_names[:5]:  # Show first 5\n",
        "        freq = tag_freq_tr[list(valid_tags).index(tag)]\n",
        "        print(f\"  - {tag:<40} ({freq*100:.1f}% of training data)\")\n",
        "    if len(dominant_tag_names) > 5:\n",
        "        print(f\"  ... and {len(dominant_tag_names) - 5} more\")\n",
        "\n",
        "print(f\"\\n✓ All variables ready for Block 7\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\n======================================================================\nSETTINGS FOR BLOCK 7 (Imbalance Handling)\n======================================================================\nData Statistics:\n  Total complaints (cleaned):  3,316\n  Unique tags:                 88\n  Avg tags/complaint:          2.44\n  Imbalance ratio:             944x\n\nTraining Set:\n  Train size:                  2,652\n  Tags < 33 samples:       12 (will augment)\n  Tags > 50% frequency:     0 (will undersample)\n\nComputed Settings:\n  DO_AUGMENT:                  True\n  DO_UNDERSAMPLE:              False\n  RARE_THRESHOLD:              33\n  DOMINANT_FREQ:               0.5\n  RARE_FREQ:                   0.0200\n  BASE_SMOOTH:                 0.097\n  GAMMA_NEG:                   5\n\nTraining Hyperparameters:\n  EPOCHS:                      9\n  BATCH_SIZE:                  16\n  MAX_LEN:                     512\n  LR:                          2e-05\n  EARLY_STOP_PAT:              3\n======================================================================\n\nRare tags to be augmented:\n  - 3rd party                                (21 samples)\n  - Cooling off                              (23 samples)\n  - Defective notice                         (1 samples)\n  - Directory listing - business             (10 samples)\n  - Disability equipment                     (13 samples)\n  - Equipment finance agreement              (18 samples)\n  - Excess call/sms/mms charges              (1 samples)\n  - General telecommunications enquiry       (2 samples)\n  - Mishandling of business information      (2 samples)\n  - No notice of activity                    (9 samples)\n  ... and 2 more\n\n✓ All variables ready for Block 7\n"
        }
      ],
      "execution_count": 11,
      "metadata": {
        "gather": {
          "logged": 1779158408730
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import random\n",
        "import torch\n",
        "from torch.utils.data import WeightedRandomSampler\n",
        "\n",
        "from torch.utils.data import Dataset, DataLoader"
      ],
      "outputs": [],
      "execution_count": 12,
      "metadata": {
        "gather": {
          "logged": 1779158415855
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "ENRICHING THE RARE TAGS with LLM enriched explanation those complains "
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Layer 1: Text augmentation for rare tags\n",
        "def augment_text(text):\n",
        "    words = str(text).split()\n",
        "    if len(words) < 6: return text\n",
        "    op = random.choice(['swap', 'drop', 'repeat'])\n",
        "    if op == 'swap' and len(words) > 3:\n",
        "        i = random.randint(0, len(words)-2)\n",
        "        words[i], words[i+1] = words[i+1], words[i]\n",
        "    elif op == 'drop' and len(words) > 8:\n",
        "        words.pop(random.randint(1, len(words)-2))\n",
        "    elif op == 'repeat':\n",
        "        mid = len(words)//2; words = words + words[mid:mid+6]\n",
        "    return ' '.join(words)\n",
        "\n",
        "if DO_AUGMENT:\n",
        "    tag_counts_tr = y_tr.sum(axis=0)\n",
        "    rare_idx      = np.where(tag_counts_tr < RARE_THRESHOLD)[0]\n",
        "    aug_rows, aug_y = [], []\n",
        "    for i in range(len(df_tr)):\n",
        "        if y_tr[i, rare_idx].any():\n",
        "            r = df_tr.iloc[i].copy()\n",
        "            r['summary'] = augment_text(str(r.get('summary', '')))\n",
        "            aug_rows.append(r); aug_y.append(y_tr[i])\n",
        "    if aug_rows:\n",
        "        df_tr = pd.concat([df_tr, pd.DataFrame(aug_rows)], ignore_index=True)\n",
        "        y_tr  = np.vstack([y_tr, np.array(aug_y)])\n",
        "        print(f\"Layer 1: Augmented {len(aug_rows)} rare-tag rows -> train size: {len(df_tr)}\")\n",
        "else:\n",
        "    print(\"Layer 1: Augmentation skipped (no rare tags below threshold)\")\n",
        "\n",
        "# Layer 2: Undersample dominant-only rows\n",
        "if DO_UNDERSAMPLE:\n",
        "    tag_freq_tr = y_tr.sum(axis=0) / len(y_tr)\n",
        "    dom_set     = set(np.where(tag_freq_tr > DOMINANT_FREQ)[0])\n",
        "    keep_i      = [i for i in range(len(df_tr))\n",
        "                   if not set(np.where(y_tr[i]==1)[0]).issubset(dom_set)\n",
        "                   or random.random() < 0.5]\n",
        "    removed = len(df_tr) - len(keep_i)\n",
        "    df_tr = df_tr.iloc[keep_i].reset_index(drop=True)\n",
        "    y_tr  = y_tr[keep_i]\n",
        "    print(f\"Layer 2: Removed {removed} dominant-only rows -> train size: {len(df_tr)}\")\n",
        "else:\n",
        "    print(\"Layer 2: Undersampling skipped (no dominant tags)\")\n",
        "\n",
        "# Layer 3: WeightedRandomSampler\n",
        "tag_w = 1.0 / (y_tr.sum(axis=0) + 1e-6)\n",
        "if 'sample_weight' in df_tr.columns:\n",
        "    sw = df_tr['sample_weight'].fillna(1.0).values.astype(np.float32)\n",
        "    sw = sw * (y_tr @ tag_w + 1e-6)\n",
        "    print(\"Layer 3: Using existing sample_weight x rare-tag boost for sampler\")\n",
        "else:\n",
        "    sw = (y_tr @ tag_w).astype(np.float32)\n",
        "    print(\"Layer 3: Computed sample weights from inverse tag frequency\")\n",
        "\n",
        "sampler = WeightedRandomSampler(torch.tensor(sw, dtype=torch.float32), len(sw), replacement=True)\n",
        "print(f\"WeightedRandomSampler ready: {len(sw)} weights\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Layer 1: Augmented 112 rare-tag rows -> train size: 2764\nLayer 2: Undersampling skipped (no dominant tags)\nLayer 3: Computed sample weights from inverse tag frequency\nWeightedRandomSampler ready: 2764 weights\n"
        }
      ],
      "execution_count": 13,
      "metadata": {
        "gather": {
          "logged": 1779158428834
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "KW_DROPOUT=0.55"
      ],
      "outputs": [],
      "execution_count": 14,
      "metadata": {
        "gather": {
          "logged": 1779158430109
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Install required libraries for feature engineering\n",
        "import subprocess\n",
        "import sys\n",
        "\n",
        "packages = ['textstat', 'vaderSentiment']\n",
        "print(\"Installing feature engineering libraries...\")\n",
        "for pkg in packages:\n",
        "    subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", pkg, \"-q\"])\n",
        "\n",
        "print(\"✓ Libraries installed\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Installing feature engineering libraries...\n✓ Libraries installed\n"
        }
      ],
      "execution_count": 15,
      "metadata": {
        "gather": {
          "logged": 1779158437693
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "def build_text(row, is_training=False):\n",
        "    parts = []\n",
        "    for label, col in [('Service', 'Service'),\n",
        "                        ('Complaint', 'summary'),\n",
        "                        ('Context', 'tier2_description_example')]:\n",
        "        val = str(row.get(col, '')).strip()\n",
        "        if val and val.lower() not in ('nan','none',''):\n",
        "            parts.append(f\"{label}: {val}\")\n",
        "    return ' [SEP] '.join(parts)\n",
        "\n",
        "class ComplaintDataset(Dataset):\n",
        "    def __init__(self, df_rows, labels, is_training=False):\n",
        "        self.df = df_rows.reset_index(drop=True)\n",
        "        self.labels = labels\n",
        "        self.is_training = is_training\n",
        "\n",
        "    def __len__(self):\n",
        "        return len(self.df)\n",
        "\n",
        "  \n",
        "    # def __getitem__(self, idx):\n",
        "    #     row = self.df.iloc[idx]\n",
        "    #     enc = tokenizer(build_text(row, self.is_training),\n",
        "    #                     max_length=MAX_LEN, padding='max_length',\n",
        "    #                     truncation=True, return_tensors='pt')\n",
        "    #     lbl = torch.tensor(self.labels[idx], dtype=torch.float32)\n",
        "    #     if self.is_training:\n",
        "    #         ns     = float(row.get('noise_score', BASE_SMOOTH))\n",
        "    #         smooth = min(0.20, max(0.01, BASE_SMOOTH + ns * 0.10))\n",
        "    #         lbl    = lbl * (1 - smooth) + smooth * 0.5\n",
        "    #     return {\n",
        "    #         'input_ids':      enc['input_ids'].squeeze(),\n",
        "    #         'attention_mask': enc['attention_mask'].squeeze(),\n",
        "    #         'labels':         lbl\n",
        "    #     }\n",
        "# So tokenization happens only when:\n",
        "\n",
        "# You iterate over a DataLoader batch\n",
        "# And only for Transformer training / inference\n",
        "\n",
        "# At that moment:\n",
        "\n",
        "# [SEP] (string) → converted into the tokenizer’s SEP token (if available)\n",
        "# Text → input IDs\n",
        "# Attention mask created\n",
        "\n",
        "#  This feeds your Transformer model only- so this is only used in Distrilbert \n",
        "\n",
        "train_loader = DataLoader(ComplaintDataset(df_tr,  y_tr,  True),\n",
        "                          batch_size=BATCH_SIZE, sampler=sampler, num_workers=0)\n",
        "val_loader   = DataLoader(ComplaintDataset(df_val, y_val), batch_size=BATCH_SIZE, num_workers=0)\n",
        "test_loader  = DataLoader(ComplaintDataset(df_te,  y_te),  batch_size=BATCH_SIZE, num_workers=0)\n",
        "\n",
        "print(f\"DataLoaders ready\")\n",
        "print(f\"  Train: {len(train_loader)} batches | Val: {len(val_loader)} | Test: {len(test_loader)}\")\n",
        "print(f\"  MAX_LEN={MAX_LEN} | BATCH_SIZE={BATCH_SIZE} | KW_DROPOUT={KW_DROPOUT:.2f}\")\n",
        "# After all augmentation/undersampling:\n",
        "train_texts = [build_text(row) for _, row in df_tr.iterrows()]\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "DataLoaders ready\n  Train: 173 batches | Val: 21 | Test: 21\n  MAX_LEN=512 | BATCH_SIZE=16 | KW_DROPOUT=0.55\n"
        }
      ],
      "execution_count": 17,
      "metadata": {
        "gather": {
          "logged": 1779158466189
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ── BLOCK 9B: Baseline Comparison — OvR XGBoost & LightGBM ──────────────\n",
        "\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.multiclass import OneVsRestClassifier\n",
        "from sklearn.metrics import f1_score, classification_report\n",
        "import xgboost as xgb\n",
        "import lightgbm as lgb\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import os\n",
        "\n",
        "# ── Create output folder ──────────────────────────────────────────────────\n",
        "os.makedirs('saved_data/results', exist_ok=True)\n",
        "\n",
        "RANDOM_SEED = 42\n",
        "# ── Helper: save per-tag F1 report to CSV ────────────────────────────────\n",
        "def save_per_tag_results(y_true, y_pred, tag_names, model_name):\n",
        "    \"\"\"Saves per-tag precision, recall, F1, support to CSV.\"\"\"\n",
        "    rows = []\n",
        "    for i, tag in enumerate(tag_names):\n",
        "        tp = int(((y_true[:, i] == 1) & (y_pred[:, i] == 1)).sum())\n",
        "        fp = int(((y_true[:, i] == 0) & (y_pred[:, i] == 1)).sum())\n",
        "        fn = int(((y_true[:, i] == 1) & (y_pred[:, i] == 0)).sum())\n",
        "        support = int(y_true[:, i].sum())\n",
        "        prec   = tp / (tp + fp) if (tp + fp) > 0 else 0.0\n",
        "        rec    = tp / (tp + fn) if (tp + fn) > 0 else 0.0\n",
        "        f1     = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0\n",
        "        rows.append({\n",
        "            'tag':       tag,\n",
        "            'precision': round(prec, 4),\n",
        "            'recall':    round(rec, 4),\n",
        "            'f1':        round(f1, 4),\n",
        "            'support':   support,\n",
        "            'model':     model_name\n",
        "        })\n",
        "    df_out = pd.DataFrame(rows).sort_values('f1', ascending=False)\n",
        "    path = f'saved_data/results/{model_name.lower().replace(\" \", \"_\")}_results.csv'\n",
        "    df_out.to_csv(path, index=False)\n",
        "    print(f\"  Saved: {path}\")\n",
        "    return df_out\n",
        "\n",
        "\n",
        "# ── Helper: compute summary metrics ──────────────────────────────────────\n",
        "def get_summary(y_true, y_pred, model_name):\n",
        "    return {\n",
        "        'model':      model_name,\n",
        "        'macro_f1':   round(f1_score(y_true, y_pred, average='macro',    zero_division=0), 4),\n",
        "        'micro_f1':   round(f1_score(y_true, y_pred, average='micro',    zero_division=0), 4),\n",
        "        'weighted_f1':round(f1_score(y_true, y_pred, average='weighted', zero_division=0), 4),\n",
        "        'samples_f1': round(f1_score(y_true, y_pred, average='samples',  zero_division=0), 4),\n",
        "    }\n"
      ],
      "outputs": [],
      "execution_count": 18,
      "metadata": {
        "gather": {
          "logged": 1779158470698
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Define directory structure\n",
        "DATA_DIR = Path(\"saved_data\")\n",
        "MODELS_DIR = Path(\"saved_models\")\n",
        "RESULTS_DIR = DATA_DIR / \"results\"\n",
        "CHECKPOINTS_DIR = Path(\"checkpoints\")"
      ],
      "outputs": [],
      "execution_count": 19,
      "metadata": {
        "gather": {
          "logged": 1779158473751
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "# ADVANCED FEATURE ENGINEERING"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "- Sentiment scores → Distinguish angry complaints vs neutral inquiries\n",
        "- Keyword flags → Direct indicators of specific complaint types\n",
        "- Dollar amounts → Financial disputes have different patterns\n",
        "- Readability metrics → Complex complaints vs simple issues\n",
        "- Service type → Different services have different complaint patterns\n",
        "- Punctuation patterns → Urgency and emotional state\n",
        "- Text length → Brief vs detailed complaints\n",
        "- Repetition → Emphasis and frustration indicators"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# # Core Python\n",
        "# import re\n",
        "# import string\n",
        "# import pickle\n",
        "# from collections import Counter\n",
        "# from pathlib import Path\n",
        "\n",
        "# # Numerical / Data\n",
        "# import numpy as np\n",
        "# import pandas as pd\n",
        "\n",
        "# # NLP\n",
        "# from nltk.tokenize import word_tokenize\n",
        "# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n",
        "\n",
        "# # Readability metrics\n",
        "# from textstat import (\n",
        "#     flesch_reading_ease,\n",
        "#     flesch_kincaid_grade,\n",
        "#     automated_readability_index\n",
        "# )\n",
        "\n",
        "# # Scikit‑learn\n",
        "# from sklearn.preprocessing import StandardScaler"
      ],
      "outputs": [],
      "execution_count": 19,
      "metadata": {
        "gather": {
          "logged": 1778690368173
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# print(\"\\n\" + \"=\" * 70)\n",
        "# print(\"PHASE 3.5: ADVANCED FEATURE ENGINEERING\")\n",
        "# print(\"=\" * 70)\n",
        "# import re\n",
        "# import string\n",
        "# from collections import Counter\n",
        "# from textstat import flesch_reading_ease, flesch_kincaid_grade, automated_readability_index\n",
        "# from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer\n",
        "# from sklearn.preprocessing import StandardScaler\n",
        "\n",
        "# # Initialize sentiment analyzer\n",
        "# sentiment_analyzer = SentimentIntensityAnalyzer()\n",
        "\n",
        "# def extract_advanced_features(df):\n",
        "#     \"\"\"\n",
        "#     Extract comprehensive features from complaint text.\n",
        "    \n",
        "#     Features include:\n",
        "#     - Text statistics (length, word count, etc.)\n",
        "#     - Sentiment scores\n",
        "#     - Readability metrics\n",
        "#     - Punctuation and capitalization patterns\n",
        "#     - Complaint-specific keywords\n",
        "#     - Service type encoding\n",
        "#     \"\"\"\n",
        "#     features = []\n",
        "    \n",
        "#     for idx, row in df.iterrows():\n",
        "#         # Build full text\n",
        "#         text = build_text(row)\n",
        "#         summary = str(row.get('summary', '')).strip()\n",
        "#         description = str(row.get('tier2_description_example', '')).strip()\n",
        "#         service = str(row.get('Service', '')).strip()\n",
        "        \n",
        "#         feat_dict = {}\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 1. TEXT LENGTH FEATURES\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         feat_dict['text_length'] = len(text)\n",
        "#         feat_dict['summary_length'] = len(summary)\n",
        "#         feat_dict['description_length'] = len(description)\n",
        "#         feat_dict['word_count'] = len(text.split())\n",
        "#         feat_dict['char_count'] = len(text.replace(' ', ''))\n",
        "#         feat_dict['avg_word_length'] = np.mean([len(w) for w in text.split()]) if text.split() else 0\n",
        "#         feat_dict['sentence_count'] = text.count('.') + text.count('!') + text.count('?')\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 2. SENTIMENT FEATURES\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         sentiment_scores = sentiment_analyzer.polarity_scores(text)\n",
        "#         feat_dict['sentiment_neg'] = sentiment_scores['neg']\n",
        "#         feat_dict['sentiment_neu'] = sentiment_scores['neu']\n",
        "#         feat_dict['sentiment_pos'] = sentiment_scores['pos']\n",
        "#         feat_dict['sentiment_compound'] = sentiment_scores['compound']\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 3. READABILITY METRICS\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         try:\n",
        "#             feat_dict['flesch_reading_ease'] = flesch_reading_ease(text) if len(text) > 10 else 0\n",
        "#             feat_dict['flesch_kincaid_grade'] = flesch_kincaid_grade(text) if len(text) > 10 else 0\n",
        "#             feat_dict['automated_readability'] = automated_readability_index(text) if len(text) > 10 else 0\n",
        "#         except:\n",
        "#             feat_dict['flesch_reading_ease'] = 0\n",
        "#             feat_dict['flesch_kincaid_grade'] = 0\n",
        "#             feat_dict['automated_readability'] = 0\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 4. PUNCTUATION & CAPITALIZATION FEATURES\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         feat_dict['question_marks'] = text.count('?')\n",
        "#         feat_dict['exclamation_marks'] = text.count('!')\n",
        "#         feat_dict['comma_count'] = text.count(',')\n",
        "#         feat_dict['period_count'] = text.count('.')\n",
        "#         feat_dict['uppercase_ratio'] = sum(1 for c in text if c.isupper()) / len(text) if text else 0\n",
        "#         feat_dict['digit_count'] = sum(1 for c in text if c.isdigit())\n",
        "#         feat_dict['special_char_count'] = sum(1 for c in text if c in string.punctuation)\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 5. COMPLAINT-SPECIFIC KEYWORDS (HIGH-IMPACT)\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         text_lower = text.lower()\n",
        "        \n",
        "#         # Problem indicators\n",
        "#         feat_dict['has_fault'] = int('fault' in text_lower or 'faulty' in text_lower)\n",
        "#         feat_dict['has_delay'] = int('delay' in text_lower or 'delayed' in text_lower)\n",
        "#         feat_dict['has_no_service'] = int('no service' in text_lower or 'not working' in text_lower)\n",
        "#         feat_dict['has_disconnection'] = int('disconnect' in text_lower or 'disconnection' in text_lower)\n",
        "#         feat_dict['has_billing'] = int('bill' in text_lower or 'charge' in text_lower or 'payment' in text_lower)\n",
        "#         feat_dict['has_refund'] = int('refund' in text_lower or 'reimburs' in text_lower)\n",
        "#         feat_dict['has_fraud'] = int('fraud' in text_lower or 'unauthorised' in text_lower or 'unauthorized' in text_lower)\n",
        "#         feat_dict['has_cancel'] = int('cancel' in text_lower or 'cancellation' in text_lower)\n",
        "#         feat_dict['has_misleading'] = int('mislead' in text_lower or 'misinform' in text_lower or 'lied' in text_lower)\n",
        "#         feat_dict['has_slow'] = int('slow' in text_lower or 'poor speed' in text_lower)\n",
        "#         feat_dict['has_outage'] = int('outage' in text_lower or 'down' in text_lower)\n",
        "#         feat_dict['has_transfer'] = int('transfer' in text_lower or 'port' in text_lower)\n",
        "#         feat_dict['has_equipment'] = int('equipment' in text_lower or 'device' in text_lower or 'modem' in text_lower)\n",
        "#         feat_dict['has_technician'] = int('technician' in text_lower or 'tech' in text_lower or 'appointment' in text_lower)\n",
        "#         feat_dict['has_contract'] = int('contract' in text_lower or 'agreement' in text_lower)\n",
        "#         feat_dict['has_privacy'] = int('privacy' in text_lower or 'data breach' in text_lower)\n",
        "#         feat_dict['has_harassment'] = int('harass' in text_lower or 'threaten' in text_lower)\n",
        "#         feat_dict['has_disability'] = int('disability' in text_lower or 'accessible' in text_lower)\n",
        "#         feat_dict['has_nbn'] = int('nbn' in text_lower)\n",
        "#         feat_dict['has_landline'] = int('landline' in text_lower or 'home phone' in text_lower)\n",
        "        \n",
        "#         # Urgency indicators\n",
        "#         feat_dict['has_urgent'] = int('urgent' in text_lower or 'emergency' in text_lower or 'immediate' in text_lower)\n",
        "#         feat_dict['has_complaint'] = int('complaint' in text_lower or 'complain' in text_lower)\n",
        "#         feat_dict['has_unresolved'] = int('unresolved' in text_lower or 'not resolved' in text_lower)\n",
        "        \n",
        "#         # Emotional indicators\n",
        "#         feat_dict['has_frustrated'] = int('frustrat' in text_lower or 'angry' in text_lower or 'upset' in text_lower)\n",
        "#         feat_dict['has_poor_service'] = int('poor service' in text_lower or 'terrible' in text_lower or 'awful' in text_lower)\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 6. DOLLAR AMOUNTS & NUMBERS\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         dollar_amounts = re.findall(r'\\$\\s*\\d+(?:,\\d{3})*(?:\\.\\d{2})?', text)\n",
        "#         feat_dict['has_dollar_amount'] = int(len(dollar_amounts) > 0)\n",
        "#         feat_dict['num_dollar_amounts'] = len(dollar_amounts)\n",
        "        \n",
        "#         # Extract max dollar amount if exists\n",
        "#         if dollar_amounts:\n",
        "#             amounts = [float(re.sub(r'[$,]', '', amt)) for amt in dollar_amounts]\n",
        "#             feat_dict['max_dollar_amount'] = max(amounts)\n",
        "#             feat_dict['total_dollar_amount'] = sum(amounts)\n",
        "#         else:\n",
        "#             feat_dict['max_dollar_amount'] = 0\n",
        "#             feat_dict['total_dollar_amount'] = 0\n",
        "        \n",
        "#         # Phone numbers\n",
        "#         phone_numbers = re.findall(r'\\b\\d{4}\\s?\\d{3}\\s?\\d{3}\\b|\\b\\d{10}\\b', text)\n",
        "#         feat_dict['num_phone_numbers'] = len(phone_numbers)\n",
        "        \n",
        "#         # Dates\n",
        "#         date_patterns = re.findall(r'\\d{1,2}[/-]\\d{1,2}[/-]\\d{2,4}', text)\n",
        "#         feat_dict['num_dates'] = len(date_patterns)\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 7. SERVICE TYPE FEATURES (ONE-HOT ENCODING)\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         common_services = ['Mobile', 'Internet', 'Landline', 'NBN', 'Broadband', 'Bundle']\n",
        "#         for svc in common_services:\n",
        "#             feat_dict[f'service_is_{svc.lower()}'] = int(svc.lower() in service.lower())\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 8. TEMPORAL PATTERNS\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         feat_dict['mentions_months'] = int(bool(re.search(r'\\b(month|year|week|day)s?\\b', text_lower)))\n",
        "#         feat_dict['mentions_timeframe'] = int(bool(re.search(r'\\b(\\d+)\\s*(month|year|week|day)s?\\b', text_lower)))\n",
        "        \n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         # 9. REPETITION FEATURES\n",
        "#         # ═══════════════════════════════════════════════════════════════\n",
        "#         words = text_lower.split()\n",
        "#         if words:\n",
        "#             word_freq = Counter(words)\n",
        "#             most_common = word_freq.most_common(1)[0][1] if word_freq else 0\n",
        "#             feat_dict['max_word_repetition'] = most_common\n",
        "#             feat_dict['unique_word_ratio'] = len(set(words)) / len(words)\n",
        "#         else:\n",
        "#             feat_dict['max_word_repetition'] = 0\n",
        "#             feat_dict['unique_word_ratio'] = 0\n",
        "        \n",
        "#         features.append(feat_dict)\n",
        "    \n",
        "#     return pd.DataFrame(features)\n"
      ],
      "outputs": [],
      "execution_count": 20,
      "metadata": {
        "gather": {
          "logged": 1778690368615
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "# # Check if features already exist\n",
        "# advanced_features_path = DATA_DIR / 'advanced_features2.npz'\n",
        "\n",
        "# if advanced_features_path.exists():\n",
        "#     print(\"✓ Found existing advanced features. Loading from disk...\")\n",
        "    \n",
        "#     loaded = np.load(advanced_features_path, allow_pickle=True)\n",
        "#     X_tr_advanced = loaded['X_tr_advanced']\n",
        "#     X_val_advanced = loaded['X_val_advanced']\n",
        "#     X_te_advanced = loaded['X_te_advanced']\n",
        "    \n",
        "#     print(f\"  Train: {X_tr_advanced.shape}\")\n",
        "#     print(f\"  Val: {X_val_advanced.shape}\")\n",
        "#     print(f\"  Test: {X_te_advanced.shape}\")\n",
        "    \n",
        "# else:\n",
        "#     print(\"✗ Advanced features not found. Extracting...\")\n",
        "    \n",
        "#     # Extract features\n",
        "#     print(\"\\n  Extracting train features...\")\n",
        "#     train_features_df = extract_advanced_features(df_tr)\n",
        "    \n",
        "#     print(\"  Extracting validation features...\")\n",
        "#     val_features_df = extract_advanced_features(df_val)\n",
        "    \n",
        "#     print(\"  Extracting test features...\")\n",
        "#     test_features_df = extract_advanced_features(df_te)\n",
        "    \n",
        "#     print(f\"\\n  Feature count: {len(train_features_df.columns)}\")\n",
        "#     print(f\"  Feature names: {list(train_features_df.columns[:10])}...\")\n",
        "    \n",
        "#     # Standardize features\n",
        "#     print(\"\\n  Standardizing features...\")\n",
        "#     scaler = StandardScaler()\n",
        "#     X_tr_advanced = scaler.fit_transform(train_features_df)\n",
        "#     X_val_advanced = scaler.transform(val_features_df)\n",
        "#     X_te_advanced = scaler.transform(test_features_df)\n",
        "    \n",
        "#     # Save features\n",
        "#     np.savez(advanced_features_path,\n",
        "#              X_tr_advanced=X_tr_advanced,\n",
        "#              X_val_advanced=X_val_advanced,\n",
        "#              X_te_advanced=X_te_advanced)\n",
        "    \n",
        "#     # Save scaler\n",
        "#     with open(DATA_DIR / 'advanced_features_scaler.pkl', 'wb') as f:\n",
        "#         pickle.dump(scaler, f)\n",
        "    \n",
        "#     print(f\"\\n  ✓ Saved to {advanced_features_path}\")\n",
        "#     print(f\"  Train: {X_tr_advanced.shape}\")\n",
        "#     print(f\"  Val: {X_val_advanced.shape}\")\n",
        "#     print(f\"  Test: {X_te_advanced.shape}\")\n",
        "\n",
        "# print(\"\\n\" + \"=\" * 70)"
      ],
      "outputs": [],
      "execution_count": 21,
      "metadata": {
        "gather": {
          "logged": 1778690369075
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "### IMPROVED VECTORS : this is like a phase 2 of trying to improve the model \n",
        "I am referring to a paper here which helps in improving the creation of vector what it does :To address this, a\n",
        "hybrid approach combining Term Frequency-Inverse Document\n",
        "Frequency (TF-IDF) and Recurrent Neural Network (RNN) has\n",
        "been proposed. The approach involves preprocessing a dataset\n",
        "of Hypertext Markup Language (HTML) documents, selecting\n",
        "specific HTML tags to generate embeddings using TF-IDF, and\n",
        "using an RNN model for multi-label classification.\n",
        "\n",
        "###  TF-IDF andFastText. \n",
        "The TF-IDF statistic evaluates the importance of a\n",
        "term in a document by considering its frequency and inverse\n",
        "document frequency . FastText, on the other hand, is\n",
        "a neural network-based approach that captures the semantic\n",
        "meaning of words through word embeddings \n",
        "\n",
        "\n",
        "PAPER : \n",
        "A Hybrid TF-IDF and RNN Model for Multi-label Classification of the Deep and Dark Web\n",
        "https://www.researchgate.net/publication/372926098_A_Hybrid_TF-IDF_and_RNN_Model_for_Multi-label_Classification_of_the_Deep_and_Dark_Web#full-text\n"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import nltk\n",
        "from nltk.tokenize import word_tokenize\n",
        "nltk.download('punkt')\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from scipy.sparse import hstack\n",
        "from gensim.models import FastText\n",
        "import numpy as np"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "[nltk_data] Downloading package punkt to /home/azureuser/nltk_data...\n[nltk_data]   Package punkt is already up-to-date!\n"
        }
      ],
      "execution_count": 20,
      "metadata": {
        "gather": {
          "logged": 1779158479552
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "## ADVANCE FEATURE VEC CREATION"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "\n",
        "# ── Step 1: Build TF-IDF features ────────────────────────────────────────\n",
        "print(\"Building TF-IDF features...\")\n",
        "tfidf = TfidfVectorizer(\n",
        "    max_features=20000,\n",
        "    ngram_range=(1, 2),\n",
        "    sublinear_tf=True\n",
        ")\n",
        "train_texts = [build_text(row) for _, row in df_tr.iterrows()]\n",
        "X_tr_tfidf = tfidf.fit_transform(train_texts)\n",
        "val_texts   = [build_text(row) for _, row in df_val.iterrows()]\n",
        "test_texts  = [build_text(row) for _, row in df_te.iterrows()]\n",
        "\n",
        "\n",
        "\n",
        "X_tr_tfidf  = tfidf.fit_transform(train_texts)\n",
        "X_val_tfidf = tfidf.transform(val_texts)\n",
        "X_te_tfidf  = tfidf.transform(test_texts)\n",
        "print(f\"TF-IDF shape: {X_tr_tfidf.shape}\")\n",
        "\n",
        "summary_rows = []   # collects summary metrics for all models\n",
        "\n",
        "#----(TF‑IDF + FastText + MLP)---------\n",
        "\n",
        "\n",
        "\n",
        "# Tokenize documents\n",
        "tokenized_texts = [word_tokenize(t.lower()) for t in train_texts]\n",
        "\n",
        "# Train FastText\n",
        "ft_model = FastText(\n",
        "    sentences=tokenized_texts,\n",
        "    vector_size=100,   # typical: 100–300\n",
        "    window=5,\n",
        "    min_count=2,\n",
        "    workers=4,\n",
        "    sg=1               # skip‑gram\n",
        ")\n",
        "#----------Convert documents to FastText vectors-------------\n",
        "\n",
        "import numpy as np\n",
        "\n",
        "def doc_to_fasttext_vector(text, model, dim=100):\n",
        "    tokens = word_tokenize(text.lower())\n",
        "    vecs = [model.wv[w] for w in tokens if w in model.wv]\n",
        "    if len(vecs) == 0:\n",
        "        return np.zeros(dim)\n",
        "    return np.mean(vecs, axis=0)\n",
        "X_tr_ft = np.vstack([doc_to_fasttext_vector(t, ft_model) for t in train_texts])\n",
        "X_val_ft = np.vstack([doc_to_fasttext_vector(t, ft_model) for t in val_texts])\n",
        "X_te_ft  = np.vstack([doc_to_fasttext_vector(t, ft_model) for t in test_texts])\n",
        "\n",
        "\n",
        "#-----COMBINE\n",
        "\n",
        "X_tr_combined  = hstack([X_tr_tfidf, X_tr_ft])\n",
        "X_val_combined = hstack([X_val_tfidf, X_val_ft])\n",
        "X_te_combined  = hstack([X_te_tfidf,  X_te_ft])\n",
        "\n",
        "print(\"Combined feature shape:\", X_tr_combined.shape)\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Building TF-IDF features...\nTF-IDF shape: (2764, 20000)\nCombined feature shape: (2764, 20100)\n"
        }
      ],
      "execution_count": 21,
      "metadata": {
        "gather": {
          "logged": 1779158536767
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from scipy.sparse import hstack, csr_matrix\n",
        "from scipy.sparse import save_npz, load_npz"
      ],
      "outputs": [],
      "execution_count": 22,
      "metadata": {
        "gather": {
          "logged": 1779158537831
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import pandas as pd\n",
        "import numpy as np\n",
        "import ast\n",
        "from sklearn.preprocessing import MultiLabelBinarizer\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.model_selection import cross_val_predict\n",
        "from sklearn.metrics.pairwise import cosine_similarity\n",
        "from cleanlab.rank import get_label_quality_scores\n",
        "from pathlib import Path\n",
        "from tqdm import tqdm\n",
        "\n",
        "# ── Install sentence-transformers if needed ──────────────────────────────────\n",
        "try:\n",
        "    from sentence_transformers import SentenceTransformer, util\n",
        "    print(\"Sentence Transformers found\")\n",
        "except ImportError:\n",
        "    import subprocess, sys\n",
        "    subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", \"sentence-transformers\", \"-q\"])\n",
        "    from sentence_transformers import SentenceTransformer, util\n",
        "    print(\"Sentence Transformers installed\")\n",
        "\n",
        "try:\n",
        "    import lightgbm as lgb\n",
        "    print(\"LightGBM found\")\n",
        "except ImportError:\n",
        "    import subprocess, sys\n",
        "    subprocess.run([sys.executable, \"-m\", \"pip\", \"install\", \"lightgbm\", \"-q\"])\n",
        "    import lightgbm as lgb\n",
        "    print(\"LightGBM installed\")\n",
        "\n",
        "Path('saved_data').mkdir(exist_ok=True)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Sentence Transformers found\nLightGBM found\n"
        }
      ],
      "execution_count": 23,
      "metadata": {
        "gather": {
          "logged": 1779158539439
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "!pip uninstall -y torch transformers sentence-transformers\n",
        "!pip install torch==2.1.0 transformers==4.41.0 sentence-transformers==2.7.0"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Found existing installation: torch 2.1.0\nUninstalling torch-2.1.0:\n  Successfully uninstalled torch-2.1.0\nFound existing installation: transformers 4.41.0\nUninstalling transformers-4.41.0:\n  Successfully uninstalled transformers-4.41.0\nFound existing installation: sentence-transformers 2.7.0\nUninstalling sentence-transformers-2.7.0:\n  Successfully uninstalled sentence-transformers-2.7.0\nCollecting torch==2.1.0\n  Using cached torch-2.1.0-cp310-cp310-manylinux1_x86_64.whl.metadata (25 kB)\nCollecting transformers==4.41.0\n  Using cached transformers-4.41.0-py3-none-any.whl.metadata (43 kB)\nCollecting sentence-transformers==2.7.0\n  Using cached sentence_transformers-2.7.0-py3-none-any.whl.metadata (11 kB)\nRequirement already satisfied: filelock in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (3.20.0)\nRequirement already satisfied: typing-extensions in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (4.15.0)\nRequirement already satisfied: sympy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (1.14.0)\nRequirement already satisfied: networkx in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (3.4.2)\nRequirement already satisfied: jinja2 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (3.1.6)\nRequirement already satisfied: fsspec in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (2023.10.0)\nRequirement already satisfied: nvidia-cuda-nvrtc-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: nvidia-cuda-runtime-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: nvidia-cuda-cupti-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: nvidia-cudnn-cu12==8.9.2.26 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (8.9.2.26)\nRequirement already satisfied: nvidia-cublas-cu12==12.1.3.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.3.1)\nRequirement already satisfied: nvidia-cufft-cu12==11.0.2.54 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (11.0.2.54)\nRequirement already satisfied: nvidia-curand-cu12==10.3.2.106 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (10.3.2.106)\nRequirement already satisfied: nvidia-cusolver-cu12==11.4.5.107 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (11.4.5.107)\nRequirement already satisfied: nvidia-cusparse-cu12==12.1.0.106 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.0.106)\nRequirement already satisfied: nvidia-nccl-cu12==2.18.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (2.18.1)\nRequirement already satisfied: nvidia-nvtx-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: triton==2.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (2.1.0)\nRequirement already satisfied: huggingface-hub<1.0,>=0.23.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (0.36.2)\nRequirement already satisfied: numpy>=1.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (1.26.4)\nRequirement already satisfied: packaging>=20.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (25.0)\nRequirement already satisfied: pyyaml>=5.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (6.0.3)\nRequirement already satisfied: regex!=2019.12.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (2025.11.3)\nRequirement already satisfied: requests in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (2.32.5)\nRequirement already satisfied: tokenizers<0.20,>=0.19 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (0.19.1)\nRequirement already satisfied: safetensors>=0.4.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (0.7.0)\nRequirement already satisfied: tqdm>=4.27 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (4.67.3)\nRequirement already satisfied: scikit-learn in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (1.5.1)\nRequirement already satisfied: scipy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (1.10.1)\nRequirement already satisfied: Pillow in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (9.2.0)\nRequirement already satisfied: nvidia-nvjitlink-cu12 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nvidia-cusolver-cu12==11.4.5.107->torch==2.1.0) (12.8.93)\nRequirement already satisfied: hf-xet<2.0.0,>=1.1.3 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub<1.0,>=0.23.0->transformers==4.41.0) (1.5.0)\nRequirement already satisfied: MarkupSafe>=2.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from jinja2->torch==2.1.0) (3.0.3)\nRequirement already satisfied: charset_normalizer<4,>=2 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (3.4.4)\nRequirement already satisfied: idna<4,>=2.5 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (3.11)\nRequirement already satisfied: urllib3<3,>=1.21.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (2.6.2)\nRequirement already satisfied: certifi>=2017.4.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (2026.1.4)\nRequirement already satisfied: joblib>=1.2.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from scikit-learn->sentence-transformers==2.7.0) (1.5.3)\nRequirement already satisfied: threadpoolctl>=3.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from scikit-learn->sentence-transformers==2.7.0) (3.6.0)\nRequirement already satisfied: mpmath<1.4,>=1.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sympy->torch==2.1.0) (1.3.0)\nUsing cached torch-2.1.0-cp310-cp310-manylinux1_x86_64.whl (670.2 MB)\nUsing cached transformers-4.41.0-py3-none-any.whl (9.1 MB)\nUsing cached sentence_transformers-2.7.0-py3-none-any.whl (171 kB)\nInstalling collected packages: torch, transformers, sentence-transformers\n\u001b[2K   \u001b[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m \u001b[32m3/3\u001b[0m [sentence-transformers]sformers]\n\u001b[1A\u001b[2K\u001b[31mERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.\nazureml-automl-dnn-nlp 1.61.0 requires torch==2.2.2, but you have torch 2.1.0 which is incompatible.\ntorchaudio 2.9.1 requires torch==2.9.1, but you have torch 2.1.0 which is incompatible.\ntorchvision 0.24.1 requires torch==2.9.1, but you have torch 2.1.0 which is incompatible.\u001b[0m\u001b[31m\n\u001b[0mSuccessfully installed sentence-transformers-2.7.0 torch-2.1.0 transformers-4.41.0\n"
        }
      ],
      "execution_count": 64,
      "metadata": {
        "gather": {
          "logged": 1778689438853
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "%pip uninstall -y torch transformers sentence-transformers\n",
        "%pip cache purge"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Found existing installation: torch 2.1.0\nUninstalling torch-2.1.0:\n  Successfully uninstalled torch-2.1.0\nFound existing installation: transformers 4.41.0\nUninstalling transformers-4.41.0:\n  Successfully uninstalled transformers-4.41.0\nFound existing installation: sentence-transformers 2.7.0\nUninstalling sentence-transformers-2.7.0:\n  Successfully uninstalled sentence-transformers-2.7.0\nNote: you may need to restart the kernel to use updated packages.\nFiles removed: 970 (7324.1 MB)\nNote: you may need to restart the kernel to use updated packages.\n"
        }
      ],
      "execution_count": 66,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "# %pip install torch==2.1.0\n",
        "# %pip install transformers==4.41.0\n",
        "# %pip install sentence-transformers==2.7.0"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Collecting torch==2.1.0\n  Downloading torch-2.1.0-cp310-cp310-manylinux1_x86_64.whl.metadata (25 kB)\nRequirement already satisfied: filelock in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (3.20.0)\nRequirement already satisfied: typing-extensions in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (4.15.0)\nRequirement already satisfied: sympy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (1.14.0)\nRequirement already satisfied: networkx in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (3.4.2)\nRequirement already satisfied: jinja2 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (3.1.6)\nRequirement already satisfied: fsspec in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (2023.10.0)\nRequirement already satisfied: nvidia-cuda-nvrtc-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: nvidia-cuda-runtime-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: nvidia-cuda-cupti-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: nvidia-cudnn-cu12==8.9.2.26 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (8.9.2.26)\nRequirement already satisfied: nvidia-cublas-cu12==12.1.3.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.3.1)\nRequirement already satisfied: nvidia-cufft-cu12==11.0.2.54 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (11.0.2.54)\nRequirement already satisfied: nvidia-curand-cu12==10.3.2.106 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (10.3.2.106)\nRequirement already satisfied: nvidia-cusolver-cu12==11.4.5.107 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (11.4.5.107)\nRequirement already satisfied: nvidia-cusparse-cu12==12.1.0.106 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.0.106)\nRequirement already satisfied: nvidia-nccl-cu12==2.18.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (2.18.1)\nRequirement already satisfied: nvidia-nvtx-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (12.1.105)\nRequirement already satisfied: triton==2.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch==2.1.0) (2.1.0)\nRequirement already satisfied: nvidia-nvjitlink-cu12 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nvidia-cusolver-cu12==11.4.5.107->torch==2.1.0) (12.8.93)\nRequirement already satisfied: MarkupSafe>=2.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from jinja2->torch==2.1.0) (3.0.3)\nRequirement already satisfied: mpmath<1.4,>=1.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sympy->torch==2.1.0) (1.3.0)\nDownloading torch-2.1.0-cp310-cp310-manylinux1_x86_64.whl (670.2 MB)\n\u001b[2K   \u001b[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m \u001b[32m670.2/670.2 MB\u001b[0m \u001b[31m11.5 MB/s\u001b[0m  \u001b[33m0:00:27\u001b[0mm0:00:01\u001b[0m00:01\u001b[0m\n\u001b[?25hInstalling collected packages: torch\n\u001b[31mERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.\nazureml-automl-dnn-nlp 1.61.0 requires transformers[sentencepiece,torch]<=4.48.0, which is not installed.\nazureml-automl-dnn-nlp 1.61.0 requires torch==2.2.2, but you have torch 2.1.0 which is incompatible.\ntorchaudio 2.9.1 requires torch==2.9.1, but you have torch 2.1.0 which is incompatible.\ntorchvision 0.24.1 requires torch==2.9.1, but you have torch 2.1.0 which is incompatible.\u001b[0m\u001b[31m\n\u001b[0mSuccessfully installed torch-2.1.0\nNote: you may need to restart the kernel to use updated packages.\nCollecting transformers==4.41.0\n  Downloading transformers-4.41.0-py3-none-any.whl.metadata (43 kB)\nRequirement already satisfied: filelock in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (3.20.0)\nRequirement already satisfied: huggingface-hub<1.0,>=0.23.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (0.36.2)\nRequirement already satisfied: numpy>=1.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (1.26.4)\nRequirement already satisfied: packaging>=20.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (25.0)\nRequirement already satisfied: pyyaml>=5.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (6.0.3)\nRequirement already satisfied: regex!=2019.12.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (2025.11.3)\nRequirement already satisfied: requests in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (2.32.5)\nRequirement already satisfied: tokenizers<0.20,>=0.19 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (0.19.1)\nRequirement already satisfied: safetensors>=0.4.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (0.7.0)\nRequirement already satisfied: tqdm>=4.27 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers==4.41.0) (4.67.3)\nRequirement already satisfied: fsspec>=2023.5.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub<1.0,>=0.23.0->transformers==4.41.0) (2023.10.0)\nRequirement already satisfied: hf-xet<2.0.0,>=1.1.3 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub<1.0,>=0.23.0->transformers==4.41.0) (1.5.0)\nRequirement already satisfied: typing-extensions>=3.7.4.3 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub<1.0,>=0.23.0->transformers==4.41.0) (4.15.0)\nRequirement already satisfied: charset_normalizer<4,>=2 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (3.4.4)\nRequirement already satisfied: idna<4,>=2.5 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (3.11)\nRequirement already satisfied: urllib3<3,>=1.21.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (2.6.2)\nRequirement already satisfied: certifi>=2017.4.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers==4.41.0) (2026.1.4)\nDownloading transformers-4.41.0-py3-none-any.whl (9.1 MB)\n\u001b[2K   \u001b[90m━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\u001b[0m \u001b[32m9.1/9.1 MB\u001b[0m \u001b[31m59.9 MB/s\u001b[0m  \u001b[33m0:00:00\u001b[0m\n\u001b[?25hInstalling collected packages: transformers\n\u001b[31mERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.\nazureml-automl-dnn-nlp 1.61.0 requires torch==2.2.2, but you have torch 2.1.0 which is incompatible.\u001b[0m\u001b[31m\n\u001b[0mSuccessfully installed transformers-4.41.0\nNote: you may need to restart the kernel to use updated packages.\nCollecting sentence-transformers==2.7.0\n  Downloading sentence_transformers-2.7.0-py3-none-any.whl.metadata (11 kB)\nRequirement already satisfied: transformers<5.0.0,>=4.34.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (4.41.0)\nRequirement already satisfied: tqdm in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (4.67.3)\nRequirement already satisfied: torch>=1.11.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (2.1.0)\nRequirement already satisfied: numpy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (1.26.4)\nRequirement already satisfied: scikit-learn in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (1.5.1)\nRequirement already satisfied: scipy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (1.10.1)\nRequirement already satisfied: huggingface-hub>=0.15.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (0.36.2)\nRequirement already satisfied: Pillow in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sentence-transformers==2.7.0) (9.2.0)\nRequirement already satisfied: filelock in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (3.20.0)\nRequirement already satisfied: packaging>=20.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (25.0)\nRequirement already satisfied: pyyaml>=5.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (6.0.3)\nRequirement already satisfied: regex!=2019.12.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (2025.11.3)\nRequirement already satisfied: requests in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (2.32.5)\nRequirement already satisfied: tokenizers<0.20,>=0.19 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (0.19.1)\nRequirement already satisfied: safetensors>=0.4.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (0.7.0)\nRequirement already satisfied: fsspec>=2023.5.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub>=0.15.1->sentence-transformers==2.7.0) (2023.10.0)\nRequirement already satisfied: hf-xet<2.0.0,>=1.1.3 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub>=0.15.1->sentence-transformers==2.7.0) (1.5.0)\nRequirement already satisfied: typing-extensions>=3.7.4.3 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from huggingface-hub>=0.15.1->sentence-transformers==2.7.0) (4.15.0)\nRequirement already satisfied: sympy in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (1.14.0)\nRequirement already satisfied: networkx in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (3.4.2)\nRequirement already satisfied: jinja2 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (3.1.6)\nRequirement already satisfied: nvidia-cuda-nvrtc-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (12.1.105)\nRequirement already satisfied: nvidia-cuda-runtime-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (12.1.105)\nRequirement already satisfied: nvidia-cuda-cupti-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (12.1.105)\nRequirement already satisfied: nvidia-cudnn-cu12==8.9.2.26 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (8.9.2.26)\nRequirement already satisfied: nvidia-cublas-cu12==12.1.3.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (12.1.3.1)\nRequirement already satisfied: nvidia-cufft-cu12==11.0.2.54 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (11.0.2.54)\nRequirement already satisfied: nvidia-curand-cu12==10.3.2.106 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (10.3.2.106)\nRequirement already satisfied: nvidia-cusolver-cu12==11.4.5.107 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (11.4.5.107)\nRequirement already satisfied: nvidia-cusparse-cu12==12.1.0.106 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (12.1.0.106)\nRequirement already satisfied: nvidia-nccl-cu12==2.18.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (2.18.1)\nRequirement already satisfied: nvidia-nvtx-cu12==12.1.105 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (12.1.105)\nRequirement already satisfied: triton==2.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from torch>=1.11.0->sentence-transformers==2.7.0) (2.1.0)\nRequirement already satisfied: nvidia-nvjitlink-cu12 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from nvidia-cusolver-cu12==11.4.5.107->torch>=1.11.0->sentence-transformers==2.7.0) (12.8.93)\nRequirement already satisfied: MarkupSafe>=2.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from jinja2->torch>=1.11.0->sentence-transformers==2.7.0) (3.0.3)\nRequirement already satisfied: charset_normalizer<4,>=2 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (3.4.4)\nRequirement already satisfied: idna<4,>=2.5 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (3.11)\nRequirement already satisfied: urllib3<3,>=1.21.1 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (2.6.2)\nRequirement already satisfied: certifi>=2017.4.17 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from requests->transformers<5.0.0,>=4.34.0->sentence-transformers==2.7.0) (2026.1.4)\nRequirement already satisfied: joblib>=1.2.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from scikit-learn->sentence-transformers==2.7.0) (1.5.3)\nRequirement already satisfied: threadpoolctl>=3.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from scikit-learn->sentence-transformers==2.7.0) (3.6.0)\nRequirement already satisfied: mpmath<1.4,>=1.1.0 in /anaconda/envs/azureml_py38/lib/python3.10/site-packages (from sympy->torch>=1.11.0->sentence-transformers==2.7.0) (1.3.0)\nDownloading sentence_transformers-2.7.0-py3-none-any.whl (171 kB)\nInstalling collected packages: sentence-transformers\nSuccessfully installed sentence-transformers-2.7.0\nNote: you may need to restart the kernel to use updated packages.\n"
        }
      ],
      "execution_count": 67,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"ADDING SENTENCE TRANSFORMER EMBEDDINGS\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "# Load model (use 'all-MiniLM-L6-v2' for 384-dim if memory is tight)\n",
        "st_model = SentenceTransformer('all-mpnet-base-v2')  # 768-dim embeddings\n",
        "\n",
        "# Combine summary + tier2_description_example for richer embeddings\n",
        "def create_st_text(df_subset):\n",
        "    \"\"\"Concatenate summary + tier2 description+example for sentence transformer input\"\"\"\n",
        "    texts = []\n",
        "    for _, row in df_subset.iterrows():\n",
        "        summary = str(row.get('summary', '')).strip()\n",
        "        tier2_desc = str(row.get('tier2_description_example', '')).strip()\n",
        "        \n",
        "        # Combine both with separator\n",
        "        combined = f\"{summary}\"\n",
        "        if tier2_desc and tier2_desc.lower() not in ('nan', 'none', ''):\n",
        "            combined += f\" [CONTEXT: {tier2_desc}]\"\n",
        "        \n",
        "        texts.append(combined)\n",
        "    return texts\n",
        "\n",
        "print(\"\\nPreparing text for encoding (summary + tier2 descriptions)...\")\n",
        "train_texts = create_st_text(df_tr)\n",
        "val_texts = create_st_text(df_val)\n",
        "test_texts = create_st_text(df_te)\n",
        "\n",
        "print(f\"Sample combined text (first train case):\")\n",
        "print(f\"  {train_texts[0][:200]}...\")\n",
        "\n",
        "# Generate embeddings for train/val/test\n",
        "print(\"\\nGenerating embeddings (this may take 2-5 minutes)...\")\n",
        "X_tr_st = st_model.encode(\n",
        "    train_texts,\n",
        "    show_progress_bar=True,\n",
        "    batch_size=32\n",
        ")\n",
        "X_val_st = st_model.encode(\n",
        "    val_texts,\n",
        "    show_progress_bar=True,\n",
        "    batch_size=32\n",
        ")\n",
        "X_te_st = st_model.encode(\n",
        "    test_texts,\n",
        "    show_progress_bar=True,\n",
        "    batch_size=32\n",
        ")\n",
        "\n",
        "print(f\"\\nSentence transformer embeddings: {X_tr_st.shape}\")\n",
        "\n",
        "# Convert to sparse (even though ST embeddings are dense, this maintains consistency)\n",
        "X_tr_st_sparse = csr_matrix(X_tr_st)\n",
        "X_val_st_sparse = csr_matrix(X_val_st)\n",
        "X_te_st_sparse = csr_matrix(X_te_st)\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\n======================================================================\nADDING SENTENCE TRANSFORMER EMBEDDINGS\n======================================================================\n\nPreparing text for encoding (summary + tier2 descriptions)...\nSample combined text (first train case):\n  CONSUMER SUMMARY AND PROVIDER'S RESPONSE:\n- Consumer has landline service with NBN Co\n- Consumer has advised the TIO that they are the account holder \n\nSpeaking to Leisette -\n- Consumer realized that ...\n\nGenerating embeddings (this may take 2-5 minutes)...\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "Batches: 100%|██████████| 87/87 [14:37<00:00, 10.09s/it]\nBatches: 100%|██████████| 11/11 [01:45<00:00,  9.61s/it]\nBatches:  91%|█████████ | 10/11 [01:41<00:10, 10.21s/it]\n"
        }
      ],
      "execution_count": 24,
      "metadata": {
        "gather": {
          "logged": 1779159646857
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "# MEGA COMBINE: super_combined + sentence transformers\n",
        "X_tr_mega = hstack([X_tr_combined, X_tr_st_sparse])\n",
        "X_val_mega = hstack([X_val_combined, X_val_st_sparse])\n",
        "X_te_mega = hstack([X_te_combined, X_te_st_sparse])\n",
        "\n",
        "print(f\"\\nFinal mega-combined feature breakdown:\")\n",
        "print(f\"  TF-IDF:              {X_tr_tfidf.shape[1]:,}\")\n",
        "print(f\"  FastText:            100\")\n",
        "#print(f\"  Advanced:            {X_tr_advanced.shape[1]}\")\n",
        "print(f\"  Sentence Transform:  {X_tr_st.shape[1]} (summary + tier2_desc)\")\n",
        "print(f\"  ───────────────────────────────────────\")\n",
        "print(f\"  TOTAL:              {X_tr_mega.shape[1]:,} features\")\n",
        "\n",
        "print(f\"\\nShapes:\")\n",
        "print(f\"  Train: {X_tr_mega.shape}\")\n",
        "print(f\"  Val:   {X_val_mega.shape}\")\n",
        "print(f\"  Test:  {X_te_mega.shape}\")\n",
        "\n",
        "# Save mega-combined\n",
        "save_npz(DATA_DIR / 'X_tr_mega_combined.npz', X_tr_mega)\n",
        "save_npz(DATA_DIR / 'X_val_mega_combined.npz', X_val_mega)\n",
        "save_npz(DATA_DIR / 'X_te_mega_combined.npz', X_te_mega)\n",
        "\n",
        "print(f\"\\n✓ Mega-combined features saved!\")\n",
        "print(f\"✓ Sentence embeddings include: summary + tier2_description_example\")\n",
        "print(\"=\" * 70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nFinal mega-combined feature breakdown:\n  TF-IDF:              20,000\n  FastText:            100\n  Sentence Transform:  768 (summary + tier2_desc)\n  ───────────────────────────────────────\n  TOTAL:              20,868 features\n\nShapes:\n  Train: (2764, 20868)\n  Val:   (332, 20868)\n  Test:  (332, 20868)\n\n✓ Mega-combined features saved!\n✓ Sentence embeddings include: summary + tier2_description_example\n======================================================================\n"
        }
      ],
      "execution_count": 25,
      "metadata": {
        "gather": {
          "logged": 1779159651223
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "print(f\"\\nFeature breakdown:\")\n",
        "print(f\"  TF-IDF:              {X_tr_tfidf.shape[1]:,}\")\n",
        "print(f\"  FastText:            {X_tr_ft.shape[1]}\")\n",
        "print(f\"  Sentence Transform:  {X_tr_st.shape[1]}\")\n",
        "print(f\"  ───────────────────────────────────────\")\n",
        "print(f\"  TOTAL:              {X_tr_mega.shape[1]:,} features\")\n",
        "\n",
        "print(f\"\\nFinal shapes:\")\n",
        "print(f\"  Train: {X_tr_mega.shape}\")\n",
        "print(f\"  Val:   {X_val_mega.shape}\")\n",
        "print(f\"  Test:  {X_te_mega.shape}\")\n",
        "\n",
        "# Train LightGBM with optimized hyperparameters for large feature set\n",
        "print(\"\\nTraining OvR LightGBM...\")\n",
        "\n",
        "lgb_mega = OneVsRestClassifier(\n",
        "    lgb.LGBMClassifier(\n",
        "        objective='binary',\n",
        "        metric='binary_logloss',\n",
        "        n_estimators=300,\n",
        "        num_leaves=31,\n",
        "        feature_fraction=0.7,      # Sample 70% of features per tree (important with 20k+ features)\n",
        "        bagging_fraction=0.8,\n",
        "        bagging_freq=5,\n",
        "        min_data_in_leaf=20,\n",
        "        lambda_l1=0.5,             # L1 regularization for sparsity\n",
        "        lambda_l2=1.0,\n",
        "        max_depth=6,\n",
        "        learning_rate=0.05,\n",
        "        subsample=0.8,\n",
        "        colsample_bytree=0.8,\n",
        "        class_weight='balanced',\n",
        "        random_state=42,\n",
        "        n_jobs=-1,\n",
        "        verbose=-1\n",
        "    ),\n",
        "    n_jobs=1\n",
        ")\n",
        "\n",
        "lgb_mega.fit(X_tr_mega, y_tr)\n",
        "\n",
        "# Predict on validation and test sets\n",
        "print(\"\\nEvaluating on validation set...\")\n",
        "lgb_preds_val = lgb_mega.predict(X_val_mega)\n",
        "val_macro = f1_score(y_val, lgb_preds_val, average='macro', zero_division=0)\n",
        "val_micro = f1_score(y_val, lgb_preds_val, average='micro', zero_division=0)\n",
        "\n",
        "print(f\"  Val Macro F1: {val_macro:.4f}\")\n",
        "print(f\"  Val Micro F1: {val_micro:.4f}\")\n",
        "\n",
        "print(\"\\nEvaluating on test set...\")\n",
        "lgb_preds_test = lgb_mega.predict(X_te_mega)\n",
        "test_macro = f1_score(y_te, lgb_preds_test, average='macro', zero_division=0)\n",
        "test_micro = f1_score(y_te, lgb_preds_test, average='micro', zero_division=0)\n",
        "\n",
        "print(f\"\\n{'='*70}\")\n",
        "print(f\"  LightGBM (TF-IDF + FastText + ST) RESULTS:\")\n",
        "print(f\"  Test Macro F1: {test_macro:.4f}\")\n",
        "print(f\"  Test Micro F1: {test_micro:.4f}\")\n",
        "print(f\"{'='*70}\")\n",
        "\n",
        "# Save results\n",
        "save_per_tag_results(\n",
        "    y_te, lgb_preds_test, valid_tags,\n",
        "    \"lightgbm_tfidf_fasttext_sentence_transformers\"\n",
        ")\n",
        "\n",
        "# Add to summary\n",
        "summary_rows.append({\n",
        "    'model': 'LightGBM (TF-IDF + FastText + ST)',\n",
        "    'macro_f1': round(test_macro, 4),\n",
        "    'micro_f1': round(test_micro, 4)\n",
        "})\n",
        "\n",
        "print(f\"\\n✓ Training complete!\")\n",
        "print(\"=\" * 70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nFeature breakdown:\n  TF-IDF:              20,000\n  FastText:            100\n  Sentence Transform:  768\n  ───────────────────────────────────────\n  TOTAL:              20,868 features\n\nFinal shapes:\n  Train: (2764, 20868)\n  Val:   (332, 20868)\n  Test:  (332, 20868)\n\nTraining OvR LightGBM...\n\nEvaluating on validation set...\n  Val Macro F1: 0.7981\n  Val Micro F1: 0.9181\n\nEvaluating on test set...\n\n======================================================================\n  LightGBM (TF-IDF + FastText + ST) RESULTS:\n  Test Macro F1: 0.8468\n  Test Micro F1: 0.9416\n======================================================================\n  Saved: saved_data/results/lightgbm_tfidf_fasttext_sentence_transformers_results.csv\n\n✓ Training complete!\n======================================================================\n"
        }
      ],
      "execution_count": 26,
      "metadata": {
        "gather": {
          "logged": 1779160563143
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from sklearn.metrics import precision_score, recall_score"
      ],
      "outputs": [],
      "execution_count": 28,
      "metadata": {
        "gather": {
          "logged": 1779160664861
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# From Step 1 - these are calculated on your test set\n",
        "test_macro_prec = precision_score(y_te, lgb_preds_test, average='macro', zero_division=0)\n",
        "test_macro_rec = recall_score(y_te, lgb_preds_test, average='macro', zero_division=0)"
      ],
      "outputs": [],
      "execution_count": 29,
      "metadata": {
        "gather": {
          "logged": 1779160665332
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import joblib\n",
        "from datetime import datetime\n",
        "import json\n",
        "\n",
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"  SAVING MODEL & COMPONENTS\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "# Create models directory\n",
        "from pathlib import Path\n",
        "Path('saved_models').mkdir(exist_ok=True)\n",
        "\n",
        "# 1. Save the trained LightGBM model\n",
        "model_path = 'saved_models/lgb_mega_model.pkl'\n",
        "joblib.dump(lgb_mega, model_path)\n",
        "print(f\"✅ Model saved: {model_path}\")\n",
        "\n",
        "# 2. Save the vectorizers/transformers (CRITICAL for inference!)\n",
        "tfidf_path = 'saved_models/tfidf_vectorizer.pkl'\n",
        "joblib.dump(tfidf, tfidf_path)\n",
        "print(f\"✅ TF-IDF vectorizer saved: {tfidf_path}\")\n",
        "\n",
        "fasttext_path = 'saved_models/fasttext_model.pkl'\n",
        "joblib.dump(ft_model, fasttext_path)\n",
        "print(f\"✅ FastText model saved: {fasttext_path}\")\n",
        "\n",
        "# Note: sentence-transformers model is loaded from pretrained, no need to save\n",
        "\n",
        "# 3. Save metadata\n",
        "metadata = {\n",
        "    'model_type': 'LightGBM + OneVsRestClassifier',\n",
        "    'features': {\n",
        "        'tfidf_features': X_tr_tfidf.shape[1],\n",
        "        'fasttext_features': X_tr_ft.shape[1],\n",
        "        'sentence_transformer_features': X_tr_st.shape[1],\n",
        "        'total_features': X_tr_mega.shape[1]\n",
        "    },\n",
        "    'performance': {\n",
        "        'val_macro_f1': round(val_macro, 4),\n",
        "        'val_micro_f1': round(val_micro, 4),\n",
        "        'test_macro_f1': round(test_macro, 4),\n",
        "        'test_micro_f1': round(test_micro, 4),\n",
        "        'test_macro_precision': round(test_macro_prec, 4),\n",
        "        'test_macro_recall': round(test_macro_rec, 4)\n",
        "    },\n",
        "    'tags': {\n",
        "        'num_tags': len(valid_tags),\n",
        "        'tag_list': valid_tags.tolist() if isinstance(valid_tags, np.ndarray) else list(valid_tags)\n",
        "    },\n",
        "    'hyperparameters': {\n",
        "        'n_estimators': 300,\n",
        "        'learning_rate': 0.05,\n",
        "        'feature_fraction': 0.7,\n",
        "        'lambda_l1': 0.5,\n",
        "        'lambda_l2': 1.0,\n",
        "        'max_depth': 6\n",
        "    },\n",
        "    'training_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),\n",
        "    'model_version': '1.0'\n",
        "}\n",
        "\n",
        "metadata_path = 'saved_models/model_metadata.json'\n",
        "with open(metadata_path, 'w') as f:\n",
        "    json.dump(metadata, f, indent=2)\n",
        "print(f\"✅ Metadata saved: {metadata_path}\")\n",
        "\n",
        "# 4. Save valid tags separately for easy loading\n",
        "np.save('saved_models/valid_tags.npy', valid_tags)\n",
        "print(f\"✅ Valid tags saved: saved_models/valid_tags.npy\")\n",
        "\n",
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"  MODEL PACKAGE SUMMARY\")\n",
        "print(\"=\" * 70)\n",
        "print(f\"  Model:           {model_path}\")\n",
        "print(f\"  TF-IDF:          {tfidf_path}\")\n",
        "print(f\"  FastText:        {fasttext_path}\")\n",
        "print(f\"  Metadata:        {metadata_path}\")\n",
        "print(f\"  Valid tags:      saved_models/valid_tags.npy\")\n",
        "print(f\"\\n  Test Macro F1:   {test_macro:.4f}\")\n",
        "print(f\"  Total features:  {X_tr_mega.shape[1]:,}\")\n",
        "print(\"=\" * 70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\n======================================================================\n  SAVING MODEL & COMPONENTS\n======================================================================\n✅ Model saved: saved_models/lgb_mega_model.pkl\n✅ TF-IDF vectorizer saved: saved_models/tfidf_vectorizer.pkl\n"
        }
      ],
      "execution_count": 30,
      "metadata": {
        "gather": {
          "logged": 1779160565922
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "## Trying API call and Model saving preparing an interface to use this model and a pipeline "
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "import joblib\n",
        "\n",
        "model = joblib.load(\"saved_models/lgb_mega_model.pkl\")\n",
        "\n"
      ],
      "outputs": [],
      "execution_count": 3,
      "metadata": {
        "gather": {
          "logged": 1779258113802
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "sentence_model = SentenceTransformer('all-mpnet-base-v2')\n",
        "sentence_model.save(\"saved_models/sentence_model\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/huggingface_hub/file_download.py:949: FutureWarning: `resume_download` is deprecated and will be removed in version 1.0.0. Downloads always resume when possible. If you want to force a new download, use `force_download=True`.\n  warnings.warn(\n"
        }
      ],
      "execution_count": 7,
      "metadata": {
        "gather": {
          "logged": 1779258576100
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from fastapi import FastAPI\n",
        "import joblib\n",
        "import numpy as np\n",
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "app = FastAPI()\n",
        "\n",
        "# Load everything\n",
        "model = joblib.load(\"saved_models/lgb_mega_model.pkl\")\n",
        "tfidf = joblib.load(\"saved_models/tfidf_vectorizer.pkl\")\n",
        "sentence_model = SentenceTransformer(\"saved_models/sentence_model\")\n",
        "\n",
        "@app.post(\"/predict\")\n",
        "def predict(data: dict):\n",
        "    text = data[\"text\"]\n",
        "    \n",
        "    tfidf_vec = tfidf.transform([text]).toarray()\n",
        "    st_vec = sentence_model.encode([text])\n",
        "    \n",
        "    combined = np.hstack([tfidf_vec, st_vec])\n",
        "    \n",
        "    preds = model.predict(combined)\n",
        "    \n",
        "    return {\"prediction\": preds.tolist()}"
      ],
      "outputs": [],
      "execution_count": 8,
      "metadata": {
        "gather": {
          "logged": 1779258587809
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"=\" * 70)\n",
        "print(\"  GENERATING TOP-20 PREDICTIONS PER COMPLAINT\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "# Get probability predictions from LightGBM\n",
        "# For OneVsRestClassifier, extract probabilities for each class\n",
        "test_probs = np.zeros((len(y_te), len(valid_tags)))\n",
        "for i, estimator in enumerate(lgb_mega.estimators_):\n",
        "    probs = estimator.predict_proba(X_te_mega)\n",
        "    # Take probability of positive class (index 1)\n",
        "    test_probs[:, i] = probs[:, 1] if probs.shape[1] > 1 else probs[:, 0]\n",
        "\n",
        "top_k = 20\n",
        "top20_rows = []\n",
        "\n",
        "for i in range(len(df_te)):\n",
        "    case_ref = df_te.iloc[i]['case_reference']\n",
        "    summary = df_te.iloc[i]['summary']  # FULL summary, no truncation\n",
        "    \n",
        "    # FIX: Get actual tags as proper list\n",
        "    actual_tags_list = df_te.iloc[i]['tags_parsed']\n",
        "    # Ensure it's a proper list (not string representation)\n",
        "    if isinstance(actual_tags_list, str):\n",
        "        actual_tags_list = parse_tags(actual_tags_list)\n",
        "    \n",
        "    # Get probabilities for all tags\n",
        "    probs = test_probs[i]\n",
        "    \n",
        "    # Get top-20 by probability\n",
        "    top_indices = probs.argsort()[-top_k:][::-1]\n",
        "    top_tags = [valid_tags[j] for j in top_indices]\n",
        "    top_probs = [round(float(probs[j]), 4) for j in top_indices]\n",
        "    \n",
        "    # Check which predictions are correct\n",
        "    top_tags_correct = [tag in actual_tags_list for tag in top_tags]\n",
        "    num_correct_in_top20 = sum(top_tags_correct)\n",
        "    num_actual_tags = len(actual_tags_list)\n",
        "    \n",
        "    precision_at_20 = num_correct_in_top20 / 20 if top_k > 0 else 0\n",
        "    recall_at_20 = num_correct_in_top20 / num_actual_tags if num_actual_tags > 0 else 0\n",
        "    \n",
        "    top20_rows.append({\n",
        "        'case_reference': case_ref,\n",
        "        'summary': summary,  # FULL summary - no truncation\n",
        "        'actual_tags': ', '.join(actual_tags_list),  # FIX: Join as comma-separated string\n",
        "        'num_actual_tags': num_actual_tags,\n",
        "        'top_20_predicted_tags': ' | '.join([f\"{tag}({prob:.3f})\" for tag, prob in zip(top_tags, top_probs)]),\n",
        "        'num_correct_in_top20': num_correct_in_top20,\n",
        "        'precision@20': round(precision_at_20, 4),\n",
        "        'recall@20': round(recall_at_20, 4)\n",
        "    })\n",
        "\n",
        "top20_df = pd.DataFrame(top20_rows)\n",
        "\n",
        "# Calculate overall metrics\n",
        "avg_precision_at_20 = top20_df['precision@20'].mean()\n",
        "avg_recall_at_20 = top20_df['recall@20'].mean()\n",
        "perfect_recall = (top20_df['recall@20'] == 1.0).sum()\n",
        "\n",
        "print(f\"\\n  Total test complaints:         {len(top20_df)}\")\n",
        "print(f\"  Average Precision@20:          {avg_precision_at_20:.4f}\")\n",
        "print(f\"  Average Recall@20:             {avg_recall_at_20:.4f}\")\n",
        "print(f\"  Cases with all tags in top-20: {perfect_recall} ({perfect_recall/len(top20_df)*100:.1f}%)\")\n",
        "\n",
        "# Save to CSV\n",
        "top20_df.to_csv('saved_data/lightgbm22_top20_predictions.csv', index=False)\n",
        "print(f\"\\n✅ Saved: saved_data/lightgbm_top20_predictions.csv\")\n",
        "\n",
        "# Show sample (first 5 rows)\n",
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"  SAMPLE TOP-20 PREDICTIONS\")\n",
        "print(\"=\" * 70)\n",
        "display(top20_df[['case_reference', 'actual_tags', 'num_actual_tags', \n",
        "                   'num_correct_in_top20', 'precision@20', 'recall@20']].head())"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1779160566072
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"=\" * 70)\n",
        "print(\"  GENERATING TOP-20 PREDICTIONS (VALIDATION & TEST ONLY)\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "# Get probability predictions from LightGBM for val and test\n",
        "# Extract probabilities for each class from OneVsRestClassifier\n",
        "def get_probabilities(X_data, model):\n",
        "    \"\"\"Extract probabilities from OneVsRestClassifier\"\"\"\n",
        "    probs = np.zeros((len(X_data.toarray() if hasattr(X_data, 'toarray') else X_data), len(valid_tags)))\n",
        "    for i, estimator in enumerate(model.estimators_):\n",
        "        prob_output = estimator.predict_proba(X_data)\n",
        "        # Take probability of positive class (index 1)\n",
        "        probs[:, i] = prob_output[:, 1] if prob_output.shape[1] > 1 else prob_output[:, 0]\n",
        "    return probs\n",
        "\n",
        "# Get probabilities for validation and test sets\n",
        "val_probs = get_probabilities(X_val_mega, lgb_mega)\n",
        "test_probs = get_probabilities(X_te_mega, lgb_mega)\n",
        "\n",
        "top_k = 20\n",
        "\n",
        "# ======================================================================\n",
        "# VALIDATION SET TOP-20\n",
        "# ======================================================================\n",
        "print(\"\\n📊 Processing VALIDATION set...\")\n",
        "val_top20_rows = []\n",
        "\n",
        "for i in range(len(df_val)):\n",
        "    case_ref = df_val.iloc[i]['case_reference']\n",
        "    summary = df_val.iloc[i]['summary']  # FULL summary\n",
        "    \n",
        "    # FIX: Get actual tags as proper list\n",
        "    actual_tags_list = df_val.iloc[i]['tags_parsed']\n",
        "    if isinstance(actual_tags_list, str):\n",
        "        actual_tags_list = parse_tags(actual_tags_list)\n",
        "    \n",
        "    # Get probabilities for all tags\n",
        "    probs = val_probs[i]\n",
        "    \n",
        "    # Get top-20 by probability\n",
        "    top_indices = probs.argsort()[-top_k:][::-1]\n",
        "    top_tags = [valid_tags[j] for j in top_indices]\n",
        "    top_probs = [round(float(probs[j]), 4) for j in top_indices]\n",
        "    \n",
        "    # Check which are correct\n",
        "    num_correct = sum([tag in actual_tags_list for tag in top_tags])\n",
        "    num_actual = len(actual_tags_list)\n",
        "    \n",
        "    val_top20_rows.append({\n",
        "        'case_reference': case_ref,\n",
        "        'summary': summary,  # FULL summary - no truncation\n",
        "        'actual_tags': ', '.join(actual_tags_list),  # FIX: comma-separated string\n",
        "        'num_actual_tags': num_actual,\n",
        "        'top_20_predicted_tags': ' | '.join([f\"{tag}({prob:.3f})\" for tag, prob in zip(top_tags, top_probs)]),\n",
        "        'num_correct_in_top20': num_correct,\n",
        "        'precision@20': round(num_correct / 20, 4),\n",
        "        'recall@20': round(num_correct / num_actual, 4) if num_actual > 0 else 0\n",
        "    })\n",
        "\n",
        "val_top20_df = pd.DataFrame(val_top20_rows)\n",
        "val_top20_df.to_csv('saved_data/validation2_top20_predictions.csv', index=False)\n",
        "\n",
        "print(f\"  Validation set: {len(val_top20_df)} complaints\")\n",
        "print(f\"  Avg Precision@20: {val_top20_df['precision@20'].mean():.4f}\")\n",
        "print(f\"  Avg Recall@20:    {val_top20_df['recall@20'].mean():.4f}\")\n",
        "print(f\"  ✅ Saved: saved_data/validation_top20_predictions.csv\")\n",
        "\n",
        "# ======================================================================\n",
        "# TEST SET TOP-20\n",
        "# ======================================================================\n",
        "print(\"\\n📊 Processing TEST set...\")\n",
        "test_top20_rows = []\n",
        "\n",
        "for i in range(len(df_te)):\n",
        "    case_ref = df_te.iloc[i]['case_reference']\n",
        "    summary = df_te.iloc[i]['summary']  # FULL summary\n",
        "    \n",
        "    # FIX: Get actual tags as proper list\n",
        "    actual_tags_list = df_te.iloc[i]['tags_parsed']\n",
        "    if isinstance(actual_tags_list, str):\n",
        "        actual_tags_list = parse_tags(actual_tags_list)\n",
        "    \n",
        "    # Get probabilities for all tags\n",
        "    probs = test_probs[i]\n",
        "    \n",
        "    # Get top-20 by probability\n",
        "    top_indices = probs.argsort()[-top_k:][::-1]\n",
        "    top_tags = [valid_tags[j] for j in top_indices]\n",
        "    top_probs = [round(float(probs[j]), 4) for j in top_indices]\n",
        "    \n",
        "    # Check which are correct\n",
        "    num_correct = sum([tag in actual_tags_list for tag in top_tags])\n",
        "    num_actual = len(actual_tags_list)\n",
        "    \n",
        "    test_top20_rows.append({\n",
        "        'case_reference': case_ref,\n",
        "        'summary': summary,  # FULL summary - no truncation\n",
        "        'actual_tags': ', '.join(actual_tags_list),  # FIX: comma-separated string\n",
        "        'num_actual_tags': num_actual,\n",
        "        'top_20_predicted_tags': ' | '.join([f\"{tag}({prob:.3f})\" for tag, prob in zip(top_tags, top_probs)]),\n",
        "        'num_correct_in_top20': num_correct,\n",
        "        'precision@20': round(num_correct / 20, 4),\n",
        "        'recall@20': round(num_correct / num_actual, 4) if num_actual > 0 else 0\n",
        "    })\n",
        "\n",
        "test_top20_df = pd.DataFrame(test_top20_rows)\n",
        "test_top20_df.to_csv('saved_data/test_top202_predictions.csv', index=False)\n",
        "\n",
        "print(f\"  Test set: {len(test_top20_df)} complaints\")\n",
        "print(f\"  Avg Precision@20: {test_top20_df['precision@20'].mean():.4f}\")\n",
        "print(f\"  Avg Recall@20:    {test_top20_df['recall@20'].mean():.4f}\")\n",
        "print(f\"  ✅ Saved: saved_data/test_top20_predictions.csv\")\n",
        "\n",
        "# ======================================================================\n",
        "# SUMMARY\n",
        "# ======================================================================\n",
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"  SUMMARY - TOP-20 PREDICTIONS\")\n",
        "print(\"=\" * 70)\n",
        "print(f\"  Validation set: {len(val_top20_df):,} complaints\")\n",
        "print(f\"    - Avg Precision@20: {val_top20_df['precision@20'].mean():.4f}\")\n",
        "print(f\"    - Avg Recall@20:    {val_top20_df['recall@20'].mean():.4f}\")\n",
        "print(f\"    - Perfect recall:   {(val_top20_df['recall@20'] == 1.0).sum()} ({(val_top20_df['recall@20'] == 1.0).mean()*100:.1f}%)\")\n",
        "print()\n",
        "print(f\"  Test set: {len(test_top20_df):,} complaints\")\n",
        "print(f\"    - Avg Precision@20: {test_top20_df['precision@20'].mean():.4f}\")\n",
        "print(f\"    - Avg Recall@20:    {test_top20_df['recall@20'].mean():.4f}\")\n",
        "print(f\"    - Perfect recall:   {(test_top20_df['recall@20'] == 1.0).sum()} ({(test_top20_df['recall@20'] == 1.0).mean()*100:.1f}%)\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "# Show sample from test set\n",
        "print(\"\\n  Sample from TEST set (first 5 rows):\")\n",
        "display(test_top20_df[['case_reference', 'actual_tags', 'num_actual_tags', \n",
        "                        'num_correct_in_top20', 'precision@20', 'recall@20']].head())"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1779160566238
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# VALIDATION SET\n",
        "lgb_preds_val = lgb_mega.predict(X_val_mega)\n",
        "val_macro = f1_score(y_val, lgb_preds_val, average='macro', zero_division=0)\n",
        "val_micro = f1_score(y_val, lgb_preds_val, average='micro', zero_division=0)\n",
        "\n",
        "print(f\"  Val Macro F1: {val_macro:.4f}\")\n",
        "print(f\"  Val Micro F1: {val_micro:.4f}\")\n",
        "\n",
        "# TEST SET\n",
        "lgb_preds_test = lgb_mega.predict(X_te_mega)\n",
        "test_macro = f1_score(y_te, lgb_preds_test, average='macro', zero_division=0)\n",
        "test_micro = f1_score(y_te, lgb_preds_test, average='micro', zero_division=0)\n",
        "\n",
        "print(f\"  Test Macro F1: {test_macro:.4f}\")\n",
        "print(f\"  Test Micro F1: {test_micro:.4f}\")"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1779160566429
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Display comparison table (add this after test evaluation)\n",
        "comparison_df = pd.DataFrame({\n",
        "    'Dataset': ['Validation', 'Test'],\n",
        "    'Macro F1': [f'{val_macro:.4f}', f'{test_macro:.4f}'],\n",
        "    'Micro F1': [f'{val_micro:.4f}', f'{test_micro:.4f}']\n",
        "})\n",
        "\n",
        "print(\"\\n\" + \"=\"*50)\n",
        "print(\"  F1 SCORES COMPARISON\")\n",
        "print(\"=\"*50)\n",
        "print(comparison_df.to_string(index=False))\n",
        "print(\"=\"*50)\n",
        "print(f\"\\nMacro F1: Equal weight to all tags (main metric)\")\n",
        "print(f\"Micro F1: Weighted by tag frequency\")"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1779160566548
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"\\nEvaluating on training set...\")\n",
        "\n",
        "lgb_probs_train = np.vstack([\n",
        "    est.predict_proba(X_tr_mega)[:, 1] \n",
        "    for est in lgb_mega.estimators_\n",
        "]).T\n",
        "\n",
        "# Default decision threshold (0.5)\n",
        "lgb_preds_train = (lgb_probs_train >= 0.5).astype(int)\n",
        "\n",
        "train_macro = f1_score(y_tr, lgb_preds_train, average='macro', zero_division=0)\n",
        "train_micro = f1_score(y_tr, lgb_preds_train, average='micro', zero_division=0)\n",
        "\n",
        "print(f\"  Train Macro F1: {train_macro:.4f}\")\n",
        "print(f\"  Train Micro F1: {train_micro:.4f}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nEvaluating on training set...\n  Train Macro F1: 0.9786\n  Train Micro F1: 0.9999\n"
        }
      ],
      "execution_count": 33,
      "metadata": {
        "gather": {
          "logged": 1778714788826
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "overfit_df = pd.DataFrame([\n",
        "    {\"split\": \"Train\", \"macro_f1\": train_macro, \"micro_f1\": train_micro},\n",
        "    {\"split\": \"Validation\", \"macro_f1\": val_macro, \"micro_f1\": val_micro},\n",
        "    {\"split\": \"Test\", \"macro_f1\": test_macro, \"micro_f1\": test_micro},\n",
        "])\n",
        "\n",
        "print(\"\\nOverfitting diagnostics:\")\n",
        "display(overfit_df)"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1779160566654
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "\n",
        "- Train macro: 0.978\n",
        "- Val macro:   0.879\n",
        "- Test macro:  0.917\n"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "df_hidden=pd.read_csv(\"sampled_100_complaints_by_tier2.csv\")"
      ],
      "outputs": [],
      "execution_count": 35,
      "metadata": {
        "gather": {
          "logged": 1778714812772
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"=\"*70)\n",
        "print(\"  OVERFITTING ANALYSIS - LightGBM Model\")\n",
        "print(\"=\"*70)\n",
        "\n",
        "# 1. Get predictions on ALL THREE splits\n",
        "print(\"\\nGenerating predictions on all splits...\")\n",
        "\n",
        "# Training set predictions\n",
        "lgb_preds_train = lgb_mega.predict(X_tr_mega)\n",
        "\n",
        "# You already have these:\n",
        "# lgb_preds_val = lgb_mega.predict(X_val_mega)\n",
        "# lgb_preds_test = lgb_mega.predict(X_te_mega)\n",
        "\n",
        "# 2. Calculate F1 scores for all splits\n",
        "from sklearn.metrics import f1_score, precision_score, recall_score\n",
        "\n",
        "# Training metrics\n",
        "train_macro = f1_score(y_tr, lgb_preds_train, average='macro', zero_division=0)\n",
        "train_micro = f1_score(y_tr, lgb_preds_train, average='micro', zero_division=0)\n",
        "train_precision = precision_score(y_tr, lgb_preds_train, average='macro', zero_division=0)\n",
        "train_recall = recall_score(y_tr, lgb_preds_train, average='macro', zero_division=0)\n",
        "\n",
        "# Validation metrics (recalculate to ensure consistency)\n",
        "val_macro = f1_score(y_val, lgb_preds_val, average='macro', zero_division=0)\n",
        "val_micro = f1_score(y_val, lgb_preds_val, average='micro', zero_division=0)\n",
        "val_precision = precision_score(y_val, lgb_preds_val, average='macro', zero_division=0)\n",
        "val_recall = recall_score(y_val, lgb_preds_val, average='macro', zero_division=0)\n",
        "\n",
        "# Test metrics\n",
        "test_macro = f1_score(y_te, lgb_preds_test, average='macro', zero_division=0)\n",
        "test_micro = f1_score(y_te, lgb_preds_test, average='micro', zero_division=0)\n",
        "test_precision = precision_score(y_te, lgb_preds_test, average='macro', zero_division=0)\n",
        "test_recall = recall_score(y_te, lgb_preds_test, average='macro', zero_division=0)\n",
        "\n",
        "# 3. Display comparison table\n",
        "print(\"\\n\" + \"=\"*70)\n",
        "print(\"  PERFORMANCE COMPARISON (OVERFITTING CHECK)\")\n",
        "print(\"=\"*70)\n",
        "\n",
        "comparison_df = pd.DataFrame({\n",
        "    'Dataset': ['Training', 'Validation', 'Test'],\n",
        "    'Size': [len(y_tr), len(y_val), len(y_te)],\n",
        "    'Macro F1': [f'{train_macro:.4f}', f'{val_macro:.4f}', f'{test_macro:.4f}'],\n",
        "    'Micro F1': [f'{train_micro:.4f}', f'{val_micro:.4f}', f'{test_micro:.4f}'],\n",
        "    'Precision': [f'{train_precision:.4f}', f'{val_precision:.4f}', f'{test_precision:.4f}'],\n",
        "    'Recall': [f'{train_recall:.4f}', f'{val_recall:.4f}', f'{test_recall:.4f}'],\n",
        "    'Gap from Train': [\n",
        "        '---',\n",
        "        f'{train_macro - val_macro:+.4f}',\n",
        "        f'{train_macro - test_macro:+.4f}'\n",
        "    ]\n",
        "})\n",
        "\n",
        "print(comparison_df.to_string(index=False))\n",
        "\n",
        "# 4. Overfitting diagnosis\n",
        "macro_gap_val = train_macro - val_macro\n",
        "macro_gap_test = train_macro - test_macro\n",
        "\n",
        "print(\"\\n\" + \"=\"*70)\n",
        "print(\"  OVERFITTING DIAGNOSIS\")\n",
        "print(\"=\"*70)\n",
        "\n",
        "if macro_gap_val > 0.15 or macro_gap_test > 0.15:\n",
        "    print(\"⚠️  SEVERE OVERFITTING DETECTED\")\n",
        "    print(f\"   Train-Val gap: {macro_gap_val:.4f}\")\n",
        "    print(f\"   Train-Test gap: {macro_gap_test:.4f}\")\n",
        "    print(\"\\n   🔴 Model memorizing training data!\")\n",
        "    print(\"\\n   Recommendations:\")\n",
        "    print(\"   • Reduce max_depth (currently 6 → try 4)\")\n",
        "    print(\"   • Increase min_child_samples\")\n",
        "    print(\"   • Reduce feature_fraction further (currently 0.7 → try 0.5)\")\n",
        "    print(\"   • Increase regularization (alpha, lambda)\")\n",
        "    print(\"   • Remove noisy/low-quality training samples\")\n",
        "    \n",
        "elif macro_gap_val > 0.08 or macro_gap_test > 0.08:\n",
        "    print(\"⚠️  MODERATE OVERFITTING\")\n",
        "    print(f\"   Train-Val gap: {macro_gap_val:.4f}\")\n",
        "    print(f\"   Train-Test gap: {macro_gap_test:.4f}\")\n",
        "    print(\"\\n   🟡 Some overfitting present\")\n",
        "    print(\"\\n   Recommendations:\")\n",
        "    print(\"   • Slight regularization increase\")\n",
        "    print(\"   • Feature selection to reduce 20,868 features\")\n",
        "    print(\"   • Cross-validation to tune hyperparameters\")\n",
        "    \n",
        "elif macro_gap_val > 0.03 or macro_gap_test > 0.03:\n",
        "    print(\"✅ HEALTHY GENERALIZATION\")\n",
        "    print(f\"   Train-Val gap: {macro_gap_val:.4f}\")\n",
        "    print(f\"   Train-Test gap: {macro_gap_test:.4f}\")\n",
        "    print(\"\\n   🟢 Good fit with acceptable generalization gap\")\n",
        "    print(\"   Model generalizes well to unseen data\")\n",
        "    \n",
        "else:\n",
        "    print(\"🤔 POTENTIAL UNDERFITTING\")\n",
        "    print(f\"   Train-Val gap: {macro_gap_val:.4f}\")\n",
        "    print(f\"   Train-Test gap: {macro_gap_test:.4f}\")\n",
        "    print(\"\\n   Model not learning enough from training data\")\n",
        "    print(\"   Consider:\")\n",
        "    print(\"   • Increase n_estimators (currently 300)\")\n",
        "    print(\"   • Increase max_depth\")\n",
        "    print(\"   • Lower learning_rate and train longer\")\n",
        "\n",
        "# 5. Per-tag overfitting analysis\n",
        "print(\"\\n\" + \"=\"*70)\n",
        "print(\"  PER-TAG OVERFITTING (Top 15 Tags by Support)\")\n",
        "print(\"=\"*70)\n",
        "\n",
        "tag_comparison = []\n",
        "for i, tag in enumerate(valid_tags[:15]):  # Top 15 tags\n",
        "    train_f1 = f1_score(y_tr[:, i], lgb_preds_train[:, i], zero_division=0)\n",
        "    val_f1 = f1_score(y_val[:, i], lgb_preds_val[:, i], zero_division=0)\n",
        "    test_f1 = f1_score(y_te[:, i], lgb_preds_test[:, i], zero_division=0)\n",
        "    gap = train_f1 - test_f1\n",
        "    support = y_te[:, i].sum()\n",
        "    \n",
        "    tag_comparison.append({\n",
        "        'Tag': tag,\n",
        "        'Support': int(support),\n",
        "        'Train F1': f'{train_f1:.3f}',\n",
        "        'Val F1': f'{val_f1:.3f}',\n",
        "        'Test F1': f'{test_f1:.3f}',\n",
        "        'Gap': f'{gap:+.3f}',\n",
        "        'Status': '⚠️' if gap > 0.2 else '✓'\n",
        "    })\n",
        "\n",
        "tag_comparison_df = pd.DataFrame(tag_comparison)\n",
        "print(tag_comparison_df.to_string(index=False))\n",
        "\n",
        "# 6. Check for perfect predictions (suspicious)\n",
        "train_perfect = (lgb_preds_train == y_tr).all(axis=1).sum()\n",
        "val_perfect = (lgb_preds_val == y_val).all(axis=1).sum()\n",
        "test_perfect = (lgb_preds_test == y_te).all(axis=1).sum()\n",
        "\n",
        "print(\"\\n\" + \"=\"*70)\n",
        "print(\"  PERFECT PREDICTION ANALYSIS\")\n",
        "print(\"=\"*70)\n",
        "print(f\"Perfect matches (all tags correct):\")\n",
        "print(f\"  Training:   {train_perfect}/{len(y_tr)} ({train_perfect/len(y_tr)*100:.1f}%)\")\n",
        "print(f\"  Validation: {val_perfect}/{len(y_val)} ({val_perfect/len(y_val)*100:.1f}%)\")\n",
        "print(f\"  Test:       {test_perfect}/{len(y_te)} ({test_perfect/len(y_te)*100:.1f}%)\")\n",
        "\n",
        "if train_perfect / len(y_tr) > 0.80:\n",
        "    print(\"\\n⚠️  Warning: >80% perfect on training set suggests overfitting\")\n",
        "\n",
        "# 7. Prediction distribution analysis\n",
        "print(\"\\n\" + \"=\"*70)\n",
        "print(\"  PREDICTION DISTRIBUTION\")\n",
        "print(\"=\"*70)\n",
        "\n",
        "train_preds_per_sample = lgb_preds_train.sum(axis=1)\n",
        "val_preds_per_sample = lgb_preds_val.sum(axis=1)\n",
        "test_preds_per_sample = lgb_preds_test.sum(axis=1)\n",
        "\n",
        "print(f\"Average predictions per sample:\")\n",
        "print(f\"  Training:   {train_preds_per_sample.mean():.2f} ± {train_preds_per_sample.std():.2f}\")\n",
        "print(f\"  Validation: {val_preds_per_sample.mean():.2f} ± {val_preds_per_sample.std():.2f}\")\n",
        "print(f\"  Test:       {test_preds_per_sample.mean():.2f} ± {test_preds_per_sample.std():.2f}\")\n",
        "\n",
        "if abs(train_preds_per_sample.mean() - test_preds_per_sample.mean()) > 1.0:\n",
        "    print(\"\\n  Large difference in avg predictions/sample between train and test\")\n",
        "\n",
        "print(\"\\n\" + \"=\"*70)\n",
        "print(\"  SUMMARY\")\n",
        "print(\"=\"*70)\n",
        "print(f\"Your macro scores:\")\n",
        "print(f\"  Train: {train_macro:.4f}\")\n",
        "print(f\"  Val:   {val_macro:.4f}\")\n",
        "print(f\"  Test:  {test_macro:.4f}\")\n",
        "print(f\"\\nIf all three are similarly high (>0.85), your model is likely working well!\")\n",
        "print(f\"If train >> val/test, you have overfitting.\")\n",
        "print(\"=\"*70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "======================================================================\n  OVERFITTING ANALYSIS - LightGBM Model\n======================================================================\n\nGenerating predictions on all splits...\n\n======================================================================\n  PERFORMANCE COMPARISON (OVERFITTING CHECK)\n======================================================================\n   Dataset  Size Macro F1 Micro F1 Precision Recall Gap from Train\n  Training  2987   0.9786   0.9999    0.9785 0.9787            ---\nValidation   341   0.8785   0.9936    0.8760 0.8818        +0.1001\n      Test   341   0.9148   0.9910    0.9092 0.9232        +0.0638\n\n======================================================================\n  OVERFITTING DIAGNOSIS\n======================================================================\n⚠️  MODERATE OVERFITTING\n   Train-Val gap: 0.1001\n   Train-Test gap: 0.0638\n\n   🟡 Some overfitting present\n\n   Recommendations:\n   • Slight regularization increase\n   • Feature selection to reduce 20,868 features\n   • Cross-validation to tune hyperparameters\n\n======================================================================\n  PER-TAG OVERFITTING (Top 15 Tags by Support)\n======================================================================\n                                      Tag  Support Train F1 Val F1 Test F1    Gap Status\n                                3rd party        3    1.000  1.000   1.000 +0.000      ✓\n                            Access denied       11    1.000  1.000   1.000 +0.000      ✓\n         Barring/suspension/disconnection       12    1.000  1.000   1.000 +0.000      ✓\n                Bill unclear/not received       16    1.000  1.000   1.000 +0.000      ✓\n                            Business loss       11    1.000  1.000   1.000 +0.000      ✓\n                             By 3rd party       14    1.000  1.000   1.000 +0.000      ✓\n                              By consumer        2    1.000  1.000   1.000 +0.000      ✓\n                              By provider       11    1.000  1.000   1.000 +0.000      ✓\n Can't access account or data - technical        4    1.000  1.000   0.727 +0.273     ⚠️\nCannot access account or data - technical        9    1.000  0.889   0.824 +0.176      ✓\n                        Changing provider        2    1.000  1.000   1.000 +0.000      ✓\n                  Connection/reconnection        5    1.000  1.000   1.000 +0.000      ✓\n                              Cooling off        7    1.000  1.000   1.000 +0.000      ✓\n                    Credit default report       10    1.000  1.000   1.000 +0.000      ✓\n               Customer Service Guarantee        5    1.000  1.000   1.000 +0.000      ✓\n\n======================================================================\n  PERFECT PREDICTION ANALYSIS\n======================================================================\nPerfect matches (all tags correct):\n  Training:   2986/2987 (100.0%)\n  Validation: 331/341 (97.1%)\n  Test:       329/341 (96.5%)\n\n⚠️  Warning: >80% perfect on training set suggests overfitting\n\n======================================================================\n  PREDICTION DISTRIBUTION\n======================================================================\nAverage predictions per sample:\n  Training:   2.44 ± 1.51\n  Validation: 2.52 ± 1.60\n  Test:       2.46 ± 1.36\n\n======================================================================\n  SUMMARY\n======================================================================\nYour macro scores:\n  Train: 0.9786\n  Val:   0.8785\n  Test:  0.9148\n\nIf all three are similarly high (>0.85), your model is likely working well!\nIf train >> val/test, you have overfitting.\n======================================================================\n"
        }
      ],
      "execution_count": 36,
      "metadata": {
        "gather": {
          "logged": 1778714833553
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "# TAG DISTRIBUTION ANALYSIS - Diagnose Overfitting Issues\n",
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import json\n",
        "import matplotlib.pyplot as plt\n",
        "import seaborn as sns\n",
        "from pathlib import Path\n",
        "\n",
        "DATA_DIR = Path(\"saved_data\")\n",
        "RESULTS_DIR = DATA_DIR / \"results\"\n",
        "\n",
        "print(\"=\" * 80)\n",
        "print(\"  TAG DISTRIBUTION ANALYSIS\")\n",
        "print(\"=\" * 80)\n",
        "\n",
        "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "# PART 1: Load Data Splits\n",
        "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "\n",
        "print(\"\\n[1/5] Loading data splits...\")\n",
        "\n",
        "# Load dataframes\n",
        "df_tr = pd.read_csv(DATA_DIR / 'train_split_cleaned.csv')\n",
        "df_val = pd.read_csv(DATA_DIR / 'val_split_cleaned.csv')\n",
        "df_te = pd.read_csv(DATA_DIR / 'test_split_cleaned.csv')\n",
        "\n",
        "# Load label matrices\n",
        "y_tr = np.load(DATA_DIR / 'y_tr_cleaned.npy')\n",
        "y_val = np.load(DATA_DIR / 'y_val_cleaned.npy')\n",
        "y_te = np.load(DATA_DIR / 'y_te_cleaned.npy')\n",
        "\n",
        "# Load tag names\n",
        "with open(DATA_DIR / 'valid_tags_cleaned.json', 'r') as f:\n",
        "    valid_tags = np.array(json.load(f))\n",
        "\n",
        "print(f\"  ✓ Train: {len(df_tr):,} samples, {y_tr.shape[1]} tags\")\n",
        "print(f\"  ✓ Val:   {len(df_val):,} samples\")\n",
        "print(f\"  ✓ Test:  {len(df_te):,} samples\")\n",
        "\n",
        "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "# PART 2: Analyze Tag Distribution BEFORE Training\n",
        "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "\n",
        "print(\"\\n[2/5] Analyzing tag distribution across splits...\")\n",
        "\n",
        "# Count occurrences per tag\n",
        "train_counts = y_tr.sum(axis=0)\n",
        "val_counts = y_val.sum(axis=0)\n",
        "test_counts = y_te.sum(axis=0)\n",
        "total_counts = train_counts + val_counts + test_counts\n",
        "\n",
        "# Create distribution dataframe\n",
        "dist_df = pd.DataFrame({\n",
        "    'tag': valid_tags,\n",
        "    'train': train_counts,\n",
        "    'val': val_counts,\n",
        "    'test': test_counts,\n",
        "    'total': total_counts,\n",
        "    'train_pct': (train_counts / train_counts.sum() * 100).round(2),\n",
        "    'val_pct': (val_counts / val_counts.sum() * 100).round(2),\n",
        "    'test_pct': (test_counts / test_counts.sum() * 100).round(2),\n",
        "})\n",
        "\n",
        "# Calculate distribution metrics\n",
        "dist_df['train_ratio'] = (dist_df['train'] / dist_df['total'] * 100).round(1)\n",
        "dist_df['val_ratio'] = (dist_df['val'] / dist_df['total'] * 100).round(1)\n",
        "dist_df['test_ratio'] = (dist_df['test'] / dist_df['total'] * 100).round(1)\n",
        "\n",
        "# Flag imbalanced tags (train ratio should be ~80%, val/test ~10% each)\n",
        "dist_df['imbalanced'] = (\n",
        "    (dist_df['train_ratio'] < 70) | (dist_df['train_ratio'] > 90) |\n",
        "    (dist_df['val_ratio'] < 5) | (dist_df['val_ratio'] > 15) |\n",
        "    (dist_df['test_ratio'] < 5) | (dist_df['test_ratio'] > 15)\n",
        ")\n",
        "\n",
        "# Sort by total count\n",
        "dist_df = dist_df.sort_values('total', ascending=False).reset_index(drop=True)\n",
        "\n",
        "# Save full distribution\n",
        "dist_df.to_csv(RESULTS_DIR / 'tag_distribution_analysis.csv', index=False)\n",
        "print(f\"  ✓ Saved: {RESULTS_DIR / 'tag_distribution_analysis.csv'}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "================================================================================\n  TAG DISTRIBUTION ANALYSIS\n================================================================================\n\n[1/5] Loading data splits...\n  ✓ Train: 2,727 samples, 94 tags\n  ✓ Val:   341 samples\n  ✓ Test:  341 samples\n\n[2/5] Analyzing tag distribution across splits...\n  ✓ Saved: saved_data/results/tag_distribution_analysis.csv\n"
        }
      ],
      "execution_count": 13,
      "metadata": {
        "gather": {
          "logged": 1778729937709
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "print(\"\\n[3/5] Analyzing prediction distributions...\")\n",
        "\n",
        "# Load predictions if they exist\n",
        "pred_files = {\n",
        "    'test_pred': RESULTS_DIR / 'lightgbm_tfidf_fasttext_sentence_transformers_results.csv',\n",
        "    'test_top20': 'saved_data/test_top20_predictions.csv'\n",
        "}\n",
        "\n",
        "for name, path in pred_files.items():\n",
        "    if Path(path).exists():\n",
        "        print(f\"  ✓ Found: {path}\")\n",
        "    else:\n",
        "        print(f\"  ⚠ Missing: {path}\")\n",
        "\n",
        "# Analyze per-tag results if available\n",
        "results_file = RESULTS_DIR / 'lightgbm_tfidf_fasttext_sentence_transformers_results.csv'\n",
        "if results_file.exists():\n",
        "    results_df = pd.read_csv(results_file)\n",
        "    \n",
        "    print(\"\\n📊 MODEL PERFORMANCE BY TAG:\")\n",
        "    print(\"\\n  Top 10 Best F1 Scores:\")\n",
        "    print(results_df.nlargest(10, 'f1')[['tag', 'precision', 'recall', 'f1', 'support']].to_string(index=False))\n",
        "    \n",
        "    print(\"\\n  Bottom 10 Worst F1 Scores:\")\n",
        "    print(results_df.nsmallest(10, 'f1')[['tag', 'precision', 'recall', 'f1', 'support']].to_string(index=False))\n",
        "    \n",
        "    # Merge with distribution data\n",
        "    comparison_df = dist_df.merge(\n",
        "        results_df[['tag', 'precision', 'recall', 'f1', 'support']], \n",
        "        on='tag', \n",
        "        how='left'\n",
        "    )\n",
        "    \n",
        "    # Identify patterns\n",
        "    low_f1_rare = comparison_df[(comparison_df['f1'] < 0.3) & (comparison_df['total'] < 10)]\n",
        "    low_f1_common = comparison_df[(comparison_df['f1'] < 0.3) & (comparison_df['total'] >= 20)]\n",
        "    \n",
        "    print(f\"\\n⚠️  Performance Issues:\")\n",
        "    print(f\"  Rare tags with low F1 (< 0.3):   {len(low_f1_rare)}\")\n",
        "    print(f\"  Common tags with low F1 (< 0.3): {len(low_f1_common)}\")\n",
        "    \n",
        "    if len(low_f1_common) > 0:\n",
        "        print(\"\\n❌ CONCERNING: Common tags performing poorly:\")\n",
        "        print(low_f1_common[['tag', 'total', 'train', 'test', 'f1', 'precision', 'recall']].to_string(index=False))\n",
        "    \n",
        "    comparison_df.to_csv(RESULTS_DIR / 'distribution_vs_performance.csv', index=False)\n",
        "    print(f\"\\n  ✓ Saved: {RESULTS_DIR / 'distribution_vs_performance.csv'}\")\n",
        "\n",
        "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "# PART 5: Analyze Inference Data (if available)\n",
        "# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n",
        "\n",
        "print(\"\\n[4/5] Analyzing inference data distribution...\")\n",
        "\n",
        "# Check for inference/external data files\n",
        "inference_files = list(Path('.').glob('*inference*.csv')) + list(Path('.').glob('*extract*.csv'))\n",
        "\n",
        "if len(inference_files) > 0:\n",
        "    print(f\"  Found {len(inference_files)} potential inference files:\")\n",
        "    for f in inference_files:\n",
        "        print(f\"    - {f}\")\n",
        "    \n",
        "    # Load operations_dashboard_extract.csv if it exists\n",
        "    if Path('operations_dashboard_extract.csv').exists():\n",
        "        print(\"\\n  Analyzing operations_dashboard_extract.csv...\")\n",
        "        df_inf = pd.read_csv('operations_dashboard_extract.csv')\n",
        "        print(f\"    Samples: {len(df_inf)}\")\n",
        "        print(f\"    Columns: {list(df_inf.columns)}\")\n",
        "        \n",
        "        # Check if it has tag columns\n",
        "        if 'tier_2' in df_inf.columns or 'tier_2_cleaned' in df_inf.columns:\n",
        "            tag_col = 'tier_2_cleaned' if 'tier_2_cleaned' in df_inf.columns else 'tier_2'\n",
        "            \n",
        "            # Parse tags\n",
        "            def parse_tags(val):\n",
        "                if isinstance(val, list): return [t.strip() for t in val if str(t).strip()]\n",
        "                if isinstance(val, str):\n",
        "                    val = val.strip()\n",
        "                    if val.startswith('['):\n",
        "                        try: return [t.strip() for t in eval(val) if str(t).strip()]\n",
        "                        except: pass\n",
        "                    return [t.strip() for t in val.split(',') if t.strip()]\n",
        "                return []\n",
        "            \n",
        "            df_inf['tags_list'] = df_inf[tag_col].apply(parse_tags)\n",
        "            df_inf = df_inf[df_inf['tags_list'].apply(len) > 0]\n",
        "            \n",
        "            # Count inference tag distribution\n",
        "            from collections import Counter\n",
        "            inf_tag_counts = Counter()\n",
        "            for tags in df_inf['tags_list']:\n",
        "                inf_tag_counts.update(tags)\n",
        "            \n",
        "            inf_dist = pd.DataFrame([\n",
        "                {'tag': tag, 'inference_count': count} \n",
        "                for tag, count in inf_tag_counts.most_common()\n",
        "            ])\n",
        "            \n",
        "            # Merge with training distribution\n",
        "            coverage_df = dist_df.merge(inf_dist, on='tag', how='outer', indicator=True)\n",
        "            coverage_df['inference_count'] = coverage_df['inference_count'].fillna(0).astype(int)\n",
        "            \n",
        "            # Tags in inference but not in training\n",
        "            unseen_tags = coverage_df[coverage_df['_merge'] == 'right_only']\n",
        "            missing_coverage = coverage_df[\n",
        "                (coverage_df['_merge'] == 'left_only') & \n",
        "                (coverage_df['inference_count'] == 0)\n",
        "            ]\n",
        "            \n",
        "            print(f\"\\n📊 INFERENCE DATA ANALYSIS:\")\n",
        "            print(f\"  Total inference samples:      {len(df_inf)}\")\n",
        "            print(f\"  Unique tags in inference:     {len(inf_dist)}\")\n",
        "            print(f\"  Tags in inference NOT trained: {len(unseen_tags)}\")\n",
        "            print(f\"  Avg tags/sample (inference):  {df_inf['tags_list'].apply(len).mean():.2f}\")\n",
        "            \n",
        "            if len(unseen_tags) > 0:\n",
        "                print(f\"\\n❌ CRITICAL: Tags in inference data but NOT in training:\")\n",
        "                print(unseen_tags[['tag', 'inference_count']].to_string(index=False))\n",
        "            \n",
        "            # Top tags in inference\n",
        "            print(f\"\\n📋 Top 15 Tags in Inference Data:\")\n",
        "            inf_top = coverage_df.nlargest(15, 'inference_count')[\n",
        "                ['tag', 'train', 'test', 'inference_count', 'total']\n",
        "            ]\n",
        "            print(inf_top.to_string(index=False))\n",
        "            \n",
        "            coverage_df.to_csv(RESULTS_DIR / 'inference_coverage_analysis.csv', index=False)\n",
        "            print(f\"\\n  ✓ Saved: {RESULTS_DIR / 'inference_coverage_analysis.csv'}\")\n",
        "        else:\n",
        "            print(\"    ⚠ No tag column found in inference file\")\n",
        "else:\n",
        "    print(\"  No inference files found\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\n[3/5] Analyzing prediction distributions...\n  ✓ Found: saved_data/results/lightgbm_tfidf_fasttext_sentence_transformers_results.csv\n  ✓ Found: saved_data/test_top20_predictions.csv\n\n📊 MODEL PERFORMANCE BY TAG:\n\n  Top 10 Best F1 Scores:\n                             tag  precision  recall  f1  support\n           Variation by provider        1.0     1.0 1.0       12\n                       3rd party        1.0     1.0 1.0        3\n                   Access denied        1.0     1.0 1.0       11\nBarring/suspension/disconnection        1.0     1.0 1.0       12\n       Bill unclear/not received        1.0     1.0 1.0       16\n                   Business loss        1.0     1.0 1.0       11\n Silent number/directory listing        1.0     1.0 1.0        5\n                 Slow data speed        1.0     1.0 1.0       10\n                       Sold debt        1.0     1.0 1.0        9\n    Statute barred debt/bankrupt        1.0     1.0 1.0        1\n\n  Bottom 10 Worst F1 Scores:\n                                      tag  precision  recall     f1  support\n             Resolution agreed but not me     0.0000  0.0000 0.0000        0\n                      Premature objection     0.0000  0.0000 0.0000        1\n      Mishandling of business information     0.0000  0.0000 0.0000        0\n                    Information inaccurat     0.0000  0.0000 0.0000        0\n       General telecommunications enquiry     0.0000  0.0000 0.0000        0\n              Excess call/sms/mms charges     0.0000  0.0000 0.0000        1\n                         Defective notice     0.0000  0.0000 0.0000        0\n Can't access account or data - technical     0.5714  1.0000 0.7273        4\n                    No notice of activity     0.6667  1.0000 0.8000        2\nCannot access account or data - technical     0.8750  0.7778 0.8235        9\n\n⚠️  Performance Issues:\n  Rare tags with low F1 (< 0.3):   7\n  Common tags with low F1 (< 0.3): 0\n\n  ✓ Saved: saved_data/results/distribution_vs_performance.csv\n\n[4/5] Analyzing inference data distribution...\n  No inference files found\n"
        }
      ],
      "execution_count": 14,
      "metadata": {
        "gather": {
          "logged": 1778730329502
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "def get_fasttext_embedding(ft_model, text, dim=100):\n",
        "    \"\"\"\n",
        "    Convert text to FastText embedding by averaging word vectors.\n",
        "    \n",
        "    Args:\n",
        "        ft_model: Trained Gensim FastText model\n",
        "        text: Input text string\n",
        "        dim: Embedding dimension (default 100)\n",
        "    \n",
        "    Returns:\n",
        "        numpy array of shape (dim,)\n",
        "    \"\"\"\n",
        "    from nltk.tokenize import word_tokenize\n",
        "    import numpy as np\n",
        "    \n",
        "    # Tokenize text\n",
        "    tokens = word_tokenize(str(text).lower())\n",
        "    \n",
        "    # Get vectors for tokens that exist in the model\n",
        "    vectors = [ft_model.wv[word] for word in tokens if word in ft_model.wv]\n",
        "    \n",
        "    # Return average or zero vector\n",
        "    if len(vectors) == 0:\n",
        "        return np.zeros(dim)\n",
        "    else:\n",
        "        return np.mean(vectors, axis=0)"
      ],
      "outputs": [],
      "execution_count": 129,
      "metadata": {
        "gather": {
          "logged": 1778572840526
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ══════════════════════════════════════════════════════════════════\n",
        "# INFERENCE ON NEW COMPLAINTS (MATCHING 20,868 FEATURES)\n",
        "# ══════════════════════════════════════════════════════════════════\n",
        "\n",
        "import joblib\n",
        "from scipy.sparse import hstack, csr_matrix\n",
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "print(\"Loading model components...\")\n",
        "lgb_mega = joblib.load('saved_models/lgb_mega_model.pkl')\n",
        "tfidf = joblib.load('saved_models/tfidf_vectorizer.pkl')\n",
        "ft_model = joblib.load('saved_models/fasttext_model.pkl')\n",
        "valid_tags = np.load(\n",
        "    'saved_models/valid_tags.npy',\n",
        "    allow_pickle=True\n",
        ")\n",
        "\n",
        "# Load new complaints\n",
        "df_hidden = pd.read_csv(\"sampled_100_complaints_by_tier2.csv\")\n",
        "\n",
        "print(f\"\\n{'='*70}\")\n",
        "print(f\"  INFERENCE ON {len(df_hidden)} COMPLAINTS\")\n",
        "print(f\"{'='*70}\")\n",
        "\n",
        "# 1. TF-IDF\n",
        "X_inf_tfidf = tfidf.transform(df_hidden['summary'].fillna(''))\n",
        "print(f\"✓ TF-IDF: {X_inf_tfidf.shape}\")\n",
        "\n",
        "# 2. FastText\n",
        "def get_fasttext_embedding(ft_model, text, dim=100):\n",
        "    from nltk.tokenize import word_tokenize\n",
        "    tokens = word_tokenize(str(text).lower())\n",
        "    vectors = [ft_model.wv[word] for word in tokens if word in ft_model.wv]\n",
        "    return np.mean(vectors, axis=0) if len(vectors) > 0 else np.zeros(dim)\n",
        "\n",
        "X_inf_ft = np.vstack([\n",
        "    get_fasttext_embedding(ft_model, text) \n",
        "    for text in df_hidden['summary'].fillna('')\n",
        "])\n",
        "X_inf_ft_sparse = csr_matrix(X_inf_ft)\n",
        "print(f\"✓ FastText: {X_inf_ft_sparse.shape}\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Loading model components...\n\n======================================================================\n  INFERENCE ON 100 COMPLAINTS\n======================================================================\n✓ TF-IDF: (100, 20000)\n✓ FastText: (100, 100)\n"
        }
      ],
      "execution_count": 15,
      "metadata": {
        "gather": {
          "logged": 1778732565707
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "df_hidden = pd.read_csv(\"sampled_100_complaints_by_tier2.csv\").head(100)\n"
      ],
      "outputs": [],
      "execution_count": 16,
      "metadata": {
        "gather": {
          "logged": 1778732566229
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ══════════════════════════════════════════════════════════════════\n",
        "# INFERENCE ON 100 NEW COMPLAINTS (NO RETRAINING!)\n",
        "# ══════════════════════════════════════════════════════════════════\n",
        "\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import pickle\n",
        "from scipy.sparse import hstack, csr_matrix\n",
        "from sentence_transformers import SentenceTransformer\n",
        "from sklearn.metrics import f1_score\n",
        "import json\n",
        "\n",
        "print(\"=\"*70)\n",
        "print(\"  TESTING TRAINED MODEL ON 100 NEW COMPLAINTS\")\n",
        "print(\"=\"*70)\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 1: Load ALREADY TRAINED model and feature extractors\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n1. Loading trained model and feature extractors...\")\n",
        "\n",
        "# Load the trained model (NO RETRAINING!)\n",
        "import joblib\n",
        "import json\n",
        "import numpy as np\n",
        "from sentence_transformers import SentenceTransformer\n",
        "\n",
        "print(\"\\n1. Loading trained model and feature extractors...\")\n",
        "\n",
        "# ✅ Load LightGBM model\n",
        "lgb_model = joblib.load('saved_models/lgb_mega_model.pkl')\n",
        "\n",
        "# ✅ Load TF-IDF vectorizer\n",
        "tfidf = joblib.load('saved_models/tfidf_vectorizer.pkl')\n",
        "\n",
        "# ✅ Load FastText model\n",
        "ft_model = joblib.load('saved_models/fasttext_model.pkl')\n",
        "\n",
        "# ✅ Load valid tags\n",
        "with open('saved_data/valid_tags_cleaned.json', 'r') as f:\n",
        "    valid_tags = np.array(json.load(f))\n",
        "\n",
        "# ✅ Load sentence transformer\n",
        "st_model = SentenceTransformer('all-mpnet-base-v2')\n",
        "\n",
        "print(f\"✓ Loaded trained model: {len(valid_tags)} tags\")\n",
        "\n",
        "df_test = pd.read_csv('sampled_100_complaints_by_tier2.csv')\n",
        "\n",
        "\n",
        "n_features_expected = lgb_model.estimators_[0].n_features_in_\n",
        "print(f\"✓ Loaded trained model: {len(valid_tags)} tags\")\n",
        "print(f\"  Model expects: {n_features_expected:,} features\")\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 2: Load the 100 NEW test complaints\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n2. Loading 100 new complaints...\")\n",
        "df_test = pd.read_csv('sampled_100_complaints_by_tier2.csv')\n",
        "\n",
        "# Parse actual tags (for evaluation only)\n",
        "def parse_tags(val):\n",
        "    if isinstance(val, str):\n",
        "        return [t.strip() for t in val.split('|') if t.strip()]\n",
        "    return []\n",
        "\n",
        "df_test['actual_tags_list'] = df_test['tier_2'].apply(parse_tags)\n",
        "\n",
        "print(f\"✓ Loaded {len(df_test)} complaints\")\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 3: Build text SAME AS TRAINING (Service + Summary, NO tag descriptions)\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n3. Building text features (Service + Summary)...\")\n",
        "\n",
        "def build_inference_text(row):\n",
        "    \"\"\"Build text matching training format, but WITHOUT tag descriptions.\"\"\"\n",
        "    parts = []\n",
        "    \n",
        "    # Add Service if available\n",
        "    service = str(row.get('Service', '')).strip()\n",
        "    if service and service.lower() not in ('nan', 'none', ''):\n",
        "        parts.append(f\"Service: {service}\")\n",
        "    \n",
        "    # Add Summary (main complaint text)\n",
        "    summary = str(row.get('summary', '')).strip()\n",
        "    if summary and summary.lower() not in ('nan', 'none', ''):\n",
        "        parts.append(f\"Complaint: {summary}\")\n",
        "    \n",
        "    # NOTE: We do NOT add 'Context' (tag descriptions) during inference!\n",
        "    \n",
        "    return ' [SEP] '.join(parts)\n",
        "\n",
        "# Generate text for all test samples\n",
        "test_texts = [build_inference_text(row) for _, row in df_test.iterrows()]\n",
        "\n",
        "print(f\"  Sample text (first 200 chars):\")\n",
        "print(f\"  {test_texts[0][:200]}...\")\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 4: Generate ALL THREE feature types\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n4. Generating features (TF-IDF + FastText + Sentence Transformers)...\")\n",
        "\n",
        "# 4a. TF-IDF features (transform only!)\n",
        "print(\"   [1/3] TF-IDF from full text...\")\n",
        "X_test_tfidf = tfidf.transform(test_texts)\n",
        "print(f\"        Shape: {X_test_tfidf.shape}\")\n",
        "\n",
        "# 4b. FastText embeddings from full text\n",
        "print(\"   [2/3] FastText from full text...\")\n",
        "def get_fasttext_embedding(text, ft_model, dim=100):\n",
        "    tokens = word_tokenize(str(text).lower())\n",
        "    vectors = [ft_model.wv[word] for word in tokens if word in ft_model.wv]\n",
        "    return np.mean(vectors, axis=0) if len(vectors) > 0 else np.zeros(dim)\n",
        "\n",
        "X_test_ft = np.vstack([\n",
        "    get_fasttext_embedding(text, ft_model) \n",
        "    for text in test_texts\n",
        "])\n",
        "print(f\"        Shape: {X_test_ft.shape}\")\n",
        "\n",
        "# 4c. Sentence Transformer embeddings from SUMMARY ONLY\n",
        "print(\"   [3/3] Sentence Transformer from summary only...\")\n",
        "test_summaries = [str(row['summary']) for _, row in df_test.iterrows()]\n",
        "\n",
        "X_test_st = st_model.encode(\n",
        "    test_summaries,\n",
        "    show_progress_bar=True,\n",
        "    normalize_embeddings=True\n",
        ")\n",
        "print(f\"        Shape: {X_test_st.shape}\")\n",
        "\n",
        "# Combine ALL THREE features\n",
        "X_test = hstack([\n",
        "    X_test_tfidf, \n",
        "    csr_matrix(X_test_ft),\n",
        "    csr_matrix(X_test_st)\n",
        "])\n",
        "\n",
        "print(f\"\\n✓ Combined features: {X_test.shape}\")\n",
        "print(f\"  Breakdown:\")\n",
        "print(f\"    - TF-IDF:              {X_test_tfidf.shape[1]:,}\")\n",
        "print(f\"    - FastText:            {X_test_ft.shape[1]:,}\")\n",
        "print(f\"    - Sentence Transformer: {X_test_st.shape[1]:,}\")\n",
        "print(f\"    - TOTAL:               {X_test.shape[1]:,}\")\n",
        "\n",
        "if X_test.shape[1] != n_features_expected:\n",
        "    print(f\"\\n⚠️  WARNING: Feature mismatch!\")\n",
        "    print(f\"    Expected: {n_features_expected:,}\")\n",
        "    print(f\"    Got:      {X_test.shape[1]:,}\")\n",
        "else:\n",
        "    print(f\"\\n✅ Feature dimensions match! ({X_test.shape[1]:,} = {n_features_expected:,})\")\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 5: Generate predictions\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n5. Generating predictions...\")\n",
        "\n",
        "# Get probabilities\n",
        "proba_list = []\n",
        "for estimator in lgb_model.estimators_:\n",
        "    prob = estimator.predict_proba(X_test)[:, 1]\n",
        "    proba_list.append(prob)\n",
        "\n",
        "proba = np.column_stack(proba_list)\n",
        "\n",
        "print(f\"\\n   Probability stats:\")\n",
        "print(f\"     Min:    {proba.min():.6f}\")\n",
        "print(f\"     Max:    {proba.max():.6f}\")\n",
        "print(f\"     Mean:   {proba.mean():.6f}\")\n",
        "print(f\"     Median: {np.median(proba):.6f}\")\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 6: Find optimal threshold from validation set\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n6. Finding optimal threshold...\")\n",
        "\n",
        "# Load validation data\n",
        "y_val = np.load('saved_data/y_val_cleaned.npy')\n",
        "X_val_combined = load_npz('saved_data/X_val_combined.npz')\n",
        "\n",
        "# Get validation probabilities\n",
        "val_proba_list = []\n",
        "for estimator in lgb_model.estimators_:\n",
        "    val_prob = estimator.predict_proba(X_val_combined)[:, 1]\n",
        "    val_proba_list.append(val_prob)\n",
        "val_proba = np.column_stack(val_proba_list)\n",
        "\n",
        "# Search for best threshold\n",
        "best_threshold = 0.5\n",
        "best_f1 = 0\n",
        "\n",
        "print(\"\\n   Threshold search:\")\n",
        "for thresh in np.arange(0.05, 0.8, 0.05):\n",
        "    val_preds = (val_proba >= thresh).astype(int)\n",
        "    f1 = f1_score(y_val, val_preds, average='macro', zero_division=0)\n",
        "    if thresh in [0.1, 0.2, 0.3, 0.4, 0.5]:\n",
        "        print(f\"     {thresh:.2f}: F1 = {f1:.4f}\")\n",
        "    if f1 > best_f1:\n",
        "        best_f1 = f1\n",
        "        best_threshold = thresh\n",
        "\n",
        "print(f\"\\n   ✅ Best threshold: {best_threshold:.2f} (Val F1: {best_f1:.4f})\")\n",
        "\n",
        "# Apply optimal threshold\n",
        "predictions = (proba >= best_threshold).astype(int)\n",
        "\n",
        "print(f\"\\n   Predictions with threshold={best_threshold}:\")\n",
        "print(f\"     Avg predictions/sample: {predictions.sum(axis=1).mean():.2f}\")\n",
        "print(f\"     Samples with 0 preds:   {(predictions.sum(axis=1) == 0).sum()}\")\n",
        "print(f\"     Samples with 1+ preds:  {(predictions.sum(axis=1) > 0).sum()}\")\n",
        "\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "# STEP 7: Evaluate and save results\n",
        "# ──────────────────────────────────────────────────────────────────\n",
        "\n",
        "print(\"\\n7. Evaluating predictions...\")\n",
        "\n",
        "# Build ground truth matrix\n",
        "y_true = np.zeros((len(df_test), len(valid_tags)))\n",
        "for i, tags in enumerate(df_test['actual_tags_list']):\n",
        "    for tag in tags:\n",
        "        if tag in valid_tags:\n",
        "            idx = np.where(valid_tags == tag)[0][0]\n",
        "            y_true[i, idx] = 1\n",
        "\n",
        "# Calculate metrics\n",
        "macro_f1 = f1_score(y_true, predictions, average='macro', zero_division=0)\n",
        "micro_f1 = f1_score(y_true, predictions, average='micro', zero_division=0)\n",
        "\n",
        "print(f\"\\n{'='*70}\")\n",
        "print(f\"  RESULTS ON 100 TEST COMPLAINTS\")\n",
        "print(f\"{'='*70}\")\n",
        "print(f\"  Threshold: {best_threshold:.2f}\")\n",
        "print(f\"  Macro F1:  {macro_f1:.4f}\")\n",
        "print(f\"  Micro F1:  {micro_f1:.4f}\")\n",
        "print(f\"{'='*70}\")\n",
        "\n",
        "# Create detailed results\n",
        "results = []\n",
        "for i in range(len(df_test)):\n",
        "    actual_tags = df_test.iloc[i]['actual_tags_list']\n",
        "    \n",
        "    # Predicted tags\n",
        "    pred_indices = np.where(predictions[i] == 1)[0]\n",
        "    pred_tags = [valid_tags[j] for j in pred_indices]\n",
        "    \n",
        "    # Top-5 predictions\n",
        "    top5_indices = np.argsort(proba[i])[::-1][:5]\n",
        "    top5_tags = [valid_tags[j] for j in top5_indices]\n",
        "    top5_probs = [proba[i, j] for j in top5_indices]\n",
        "    \n",
        "    # Metrics\n",
        "    tp = len(set(pred_tags) & set(actual_tags))\n",
        "    fp = len(set(pred_tags) - set(actual_tags))\n",
        "    fn = len(set(actual_tags) - set(pred_tags))\n",
        "    \n",
        "    precision = tp / (tp + fp) if (tp + fp) > 0 else 0\n",
        "    recall = tp / (tp + fn) if (tp + fn) > 0 else 0\n",
        "    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) > 0 else 0\n",
        "    \n",
        "    results.append({\n",
        "        'case_reference': df_test.iloc[i]['case_reference'],\n",
        "        'summary': str(df_test.iloc[i]['summary'])[:100] + '...',\n",
        "        'actual_tags': ' | '.join(actual_tags),\n",
        "        'predicted_tags': ' | '.join(pred_tags) if pred_tags else 'NONE',\n",
        "        'num_actual': len(actual_tags),\n",
        "        'num_predicted': len(pred_tags),\n",
        "        'f1': round(f1, 3),\n",
        "        'precision': round(precision, 3),\n",
        "        'recall': round(recall, 3),\n",
        "        'top5': ' | '.join([f\"{t}({p:.3f})\" for t, p in zip(top5_tags, top5_probs)])\n",
        "    })\n",
        "\n",
        "results_df = pd.DataFrame(results)\n",
        "\n",
        "# Save\n",
        "results_df.to_csv('saved_data/100_complaints_test_results_FIXED.csv', index=False)\n",
        "print(f\"\\n✓ Saved: saved_data/100_complaints_test_results_FIXED.csv\")\n",
        "\n",
        "# Display samples\n",
        "print(f\"\\n📊 Sample Predictions (first 10):\")\n",
        "for idx in range(min(10, len(results_df))):\n",
        "    row = results_df.iloc[idx]\n",
        "    print(f\"\\n[{idx+1}] {row['case_reference']}\")\n",
        "    print(f\"    Actual:    {row['actual_tags'][:80]}\")\n",
        "    print(f\"    Predicted: {row['predicted_tags'][:80]}\")\n",
        "    print(f\"    F1={row['f1']:.3f} | P={row['precision']:.3f} | R={row['recall']:.3f}\")\n",
        "\n",
        "print(f\"\\n{'='*70}\")\n",
        "print(\"✅ INFERENCE COMPLETE!\")\n",
        "print(f\"{'='*70}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "======================================================================\n  TESTING TRAINED MODEL ON 100 NEW COMPLAINTS\n======================================================================\n\n1. Loading trained model and feature extractors...\n\n1. Loading trained model and feature extractors...\n        Shape: (100, 768)\n\n✓ Combined features: (100, 20868)\n  Breakdown:\n    - TF-IDF:              20,000\n    - FastText:            100\n    - Sentence Transformer: 768\n    - TOTAL:               20,868\n\n✅ Feature dimensions match! (20,868 = 20,868)\n\n5. Generating predictions...\n\n   Probability stats:\n     Min:    0.000000\n     Max:    0.033077\n     Mean:   0.000449\n     Median: 0.000449\n\n6. Finding optimal threshold...\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "Batches: 100%|██████████| 4/4 [00:33<00:00,  8.26s/it]\n"
        },
        {
          "output_type": "error",
          "ename": "FileNotFoundError",
          "evalue": "[Errno 2] No such file or directory: 'saved_data/X_val_combined.npz'",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mFileNotFoundError\u001b[0m                         Traceback (most recent call last)",
            "Cell \u001b[0;32mIn[46], line 187\u001b[0m\n\u001b[1;32m    185\u001b[0m \u001b[38;5;66;03m# Load validation data\u001b[39;00m\n\u001b[1;32m    186\u001b[0m y_val \u001b[38;5;241m=\u001b[39m np\u001b[38;5;241m.\u001b[39mload(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124msaved_data/y_val_cleaned.npy\u001b[39m\u001b[38;5;124m'\u001b[39m)\n\u001b[0;32m--> 187\u001b[0m X_val_combined \u001b[38;5;241m=\u001b[39m \u001b[43mload_npz\u001b[49m\u001b[43m(\u001b[49m\u001b[38;5;124;43m'\u001b[39;49m\u001b[38;5;124;43msaved_data/X_val_combined.npz\u001b[39;49m\u001b[38;5;124;43m'\u001b[39;49m\u001b[43m)\u001b[49m\n\u001b[1;32m    189\u001b[0m \u001b[38;5;66;03m# Get validation probabilities\u001b[39;00m\n\u001b[1;32m    190\u001b[0m val_proba_list \u001b[38;5;241m=\u001b[39m []\n",
            "File \u001b[0;32m/anaconda/envs/azureml_py38/lib/python3.10/site-packages/scipy/sparse/_matrix_io.py:125\u001b[0m, in \u001b[0;36mload_npz\u001b[0;34m(file)\u001b[0m\n\u001b[1;32m     76\u001b[0m \u001b[38;5;28;01mdef\u001b[39;00m\u001b[38;5;250m \u001b[39m\u001b[38;5;21mload_npz\u001b[39m(file):\n\u001b[1;32m     77\u001b[0m \u001b[38;5;250m    \u001b[39m\u001b[38;5;124;03m\"\"\" Load a sparse matrix from a file using ``.npz`` format.\u001b[39;00m\n\u001b[1;32m     78\u001b[0m \n\u001b[1;32m     79\u001b[0m \u001b[38;5;124;03m    Parameters\u001b[39;00m\n\u001b[0;32m   (...)\u001b[0m\n\u001b[1;32m    122\u001b[0m \u001b[38;5;124;03m           [4, 0, 0]], dtype=int64)\u001b[39;00m\n\u001b[1;32m    123\u001b[0m \u001b[38;5;124;03m    \"\"\"\u001b[39;00m\n\u001b[0;32m--> 125\u001b[0m     \u001b[38;5;28;01mwith\u001b[39;00m \u001b[43mnp\u001b[49m\u001b[38;5;241;43m.\u001b[39;49m\u001b[43mload\u001b[49m\u001b[43m(\u001b[49m\u001b[43mfile\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[38;5;241;43m*\u001b[39;49m\u001b[43mPICKLE_KWARGS\u001b[49m\u001b[43m)\u001b[49m \u001b[38;5;28;01mas\u001b[39;00m loaded:\n\u001b[1;32m    126\u001b[0m         \u001b[38;5;28;01mtry\u001b[39;00m:\n\u001b[1;32m    127\u001b[0m             matrix_format \u001b[38;5;241m=\u001b[39m loaded[\u001b[38;5;124m'\u001b[39m\u001b[38;5;124mformat\u001b[39m\u001b[38;5;124m'\u001b[39m]\n",
            "File \u001b[0;32m/anaconda/envs/azureml_py38/lib/python3.10/site-packages/numpy/lib/npyio.py:427\u001b[0m, in \u001b[0;36mload\u001b[0;34m(file, mmap_mode, allow_pickle, fix_imports, encoding, max_header_size)\u001b[0m\n\u001b[1;32m    425\u001b[0m     own_fid \u001b[38;5;241m=\u001b[39m \u001b[38;5;28;01mFalse\u001b[39;00m\n\u001b[1;32m    426\u001b[0m \u001b[38;5;28;01melse\u001b[39;00m:\n\u001b[0;32m--> 427\u001b[0m     fid \u001b[38;5;241m=\u001b[39m stack\u001b[38;5;241m.\u001b[39menter_context(\u001b[38;5;28;43mopen\u001b[39;49m\u001b[43m(\u001b[49m\u001b[43mos_fspath\u001b[49m\u001b[43m(\u001b[49m\u001b[43mfile\u001b[49m\u001b[43m)\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;124;43m\"\u001b[39;49m\u001b[38;5;124;43mrb\u001b[39;49m\u001b[38;5;124;43m\"\u001b[39;49m\u001b[43m)\u001b[49m)\n\u001b[1;32m    428\u001b[0m     own_fid \u001b[38;5;241m=\u001b[39m \u001b[38;5;28;01mTrue\u001b[39;00m\n\u001b[1;32m    430\u001b[0m \u001b[38;5;66;03m# Code to distinguish from NumPy binary files and pickles.\u001b[39;00m\n",
            "\u001b[0;31mFileNotFoundError\u001b[0m: [Errno 2] No such file or directory: 'saved_data/X_val_combined.npz'"
          ]
        }
      ],
      "execution_count": 46,
      "metadata": {
        "gather": {
          "logged": 1778736540616
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "# FIXED INFERENCE WITH OPTIMAL THRESHOLD\n",
        "# ══════════════════════════════════════════════════════════════════════════════\n",
        "\n",
        "def predict_with_threshold(model, X, threshold=0.3, per_tag_thresholds=None):\n",
        "    \"\"\"\n",
        "    Predict using probability threshold instead of default 0.5\n",
        "    \n",
        "    Args:\n",
        "        model: Trained OneVsRestClassifier\n",
        "        X: Feature matrix\n",
        "        threshold: Global threshold (default 0.3)\n",
        "        per_tag_thresholds: Dict of {tag_index: threshold} for per-tag thresholds\n",
        "    \n",
        "    Returns:\n",
        "        Binary predictions (n_samples, n_tags)\n",
        "    \"\"\"\n",
        "    # Get probabilities from each binary classifier\n",
        "    probs_list = []\n",
        "    for estimator in model.estimators_:\n",
        "        prob = estimator.predict_proba(X)[:, 1]  # Probability of class 1\n",
        "        probs_list.append(prob)\n",
        "    \n",
        "    probs = np.column_stack(probs_list)\n",
        "    \n",
        "    # Apply thresholds\n",
        "    if per_tag_thresholds is not None:\n",
        "        # Apply per-tag thresholds\n",
        "        preds = np.zeros_like(probs)\n",
        "        for tag_idx, tag_thresh in per_tag_thresholds.items():\n",
        "            preds[:, tag_idx] = (probs[:, tag_idx] >= tag_thresh).astype(int)\n",
        "    else:\n",
        "        # Apply global threshold\n",
        "        preds = (probs >= threshold).astype(int)\n",
        "    \n",
        "    return preds, probs\n",
        "\n",
        "\n",
        "# Example usage on your inference data:\n",
        "# Assuming you have X_inference already prepared\n",
        "\n",
        "# Option 1: Use global threshold (simple)\n",
        "preds, probs = predict_with_threshold(lgb_mega, X_inference, threshold=0.3)\n",
        "\n",
        "# Option 2: Use per-tag thresholds (better)\n",
        "tag_thresh_df = pd.read_csv('saved_data/optimal_tag_thresholds.csv')\n",
        "per_tag_thresholds = {\n",
        "    i: row['optimal_threshold'] \n",
        "    for i, row in tag_thresh_df.iterrows()\n",
        "}\n",
        "preds, probs = predict_with_threshold(lgb_mega, X_inference, per_tag_thresholds=per_tag_thresholds)\n",
        "\n",
        "# Convert predictions to tag names\n",
        "predicted_tags = []\n",
        "for i in range(len(preds)):\n",
        "    tags = [valid_tags[j] for j in np.where(preds[i] == 1)[0]]\n",
        "    predicted_tags.append(tags if len(tags) > 0 else ['No tags predicted'])\n",
        "\n",
        "print(f\"Predictions with adjusted threshold:\")\n",
        "print(f\"  Avg predictions per sample: {preds.sum(axis=1).mean():.2f}\")\n",
        "print(f\"  Samples with 0 predictions: {(preds.sum(axis=1) == 0).sum()}\")"
      ],
      "outputs": [
        {
          "output_type": "error",
          "ename": "NameError",
          "evalue": "name 'X_inference' is not defined",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mNameError\u001b[0m                                 Traceback (most recent call last)",
            "Cell \u001b[0;32mIn[12], line 43\u001b[0m\n\u001b[1;32m     36\u001b[0m     \u001b[38;5;28;01mreturn\u001b[39;00m preds, probs\n\u001b[1;32m     39\u001b[0m \u001b[38;5;66;03m# Example usage on your inference data:\u001b[39;00m\n\u001b[1;32m     40\u001b[0m \u001b[38;5;66;03m# Assuming you have X_inference already prepared\u001b[39;00m\n\u001b[1;32m     41\u001b[0m \n\u001b[1;32m     42\u001b[0m \u001b[38;5;66;03m# Option 1: Use global threshold (simple)\u001b[39;00m\n\u001b[0;32m---> 43\u001b[0m preds, probs \u001b[38;5;241m=\u001b[39m predict_with_threshold(lgb_mega, \u001b[43mX_inference\u001b[49m, threshold\u001b[38;5;241m=\u001b[39m\u001b[38;5;241m0.3\u001b[39m)\n\u001b[1;32m     45\u001b[0m \u001b[38;5;66;03m# Option 2: Use per-tag thresholds (better)\u001b[39;00m\n\u001b[1;32m     46\u001b[0m tag_thresh_df \u001b[38;5;241m=\u001b[39m pd\u001b[38;5;241m.\u001b[39mread_csv(\u001b[38;5;124m'\u001b[39m\u001b[38;5;124msaved_data/optimal_tag_thresholds.csv\u001b[39m\u001b[38;5;124m'\u001b[39m)\n",
            "\u001b[0;31mNameError\u001b[0m: name 'X_inference' is not defined"
          ]
        }
      ],
      "execution_count": 12,
      "metadata": {
        "gather": {
          "logged": 1778729712685
        }
      }
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [],
      "execution_count": 104,
      "metadata": {
        "gather": {
          "logged": 1778570352414
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# # Get probability predictions (IMPORTANT: use predict_proba, not predict)\n",
        "# print(\"\\nGenerating probability predictions...\")\n",
        "# lgb_probs_val = np.vstack([\n",
        "#     est.predict_proba(X_val_mega)[:, 1] \n",
        "#     for est in lgb_mega.estimators_\n",
        "# ]).T\n",
        "\n",
        "# lgb_probs_test = np.vstack([\n",
        "#     est.predict_proba(X_te_mega)[:, 1] \n",
        "#     for est in lgb_mega.estimators_\n",
        "# ]).T"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/lightgbm/basic.py:1238: UserWarning: Converting data to scipy sparse matrix.\n  _log_warning(\"Converting data to scipy sparse matrix.\")\n"
        }
      ],
      "execution_count": 105,
      "metadata": {
        "gather": {
          "logged": 1778570361442
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# TOP_K = 20\n",
        "\n",
        "# df_top20_test = generate_topk_predictions(\n",
        "#     probs=lgb_probs_test,\n",
        "#     # y_true=y_te,a\n",
        "#     df_test=df_test,\n",
        "#     valid_tags=valid_tags,\n",
        "#     model_name=\"LightGBM (TF-IDF + FastText + ST)\",\n",
        "#     k=TOP_K\n",
        "# )\n",
        "\n",
        "# print(df_top20_test.head(3))\n",
        "# print(f\"\\nGenerated top-{TOP_K} predictions for {len(df_top20_test)} test samples\")"
      ],
      "outputs": [
        {
          "output_type": "error",
          "ename": "NameError",
          "evalue": "name 'df_test' is not defined",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mNameError\u001b[0m                                 Traceback (most recent call last)",
            "Cell \u001b[0;32mIn[106], line 6\u001b[0m\n\u001b[1;32m      1\u001b[0m TOP_K \u001b[38;5;241m=\u001b[39m \u001b[38;5;241m20\u001b[39m\n\u001b[1;32m      3\u001b[0m df_top20_test \u001b[38;5;241m=\u001b[39m generate_topk_predictions(\n\u001b[1;32m      4\u001b[0m     probs\u001b[38;5;241m=\u001b[39mlgb_probs_test,\n\u001b[1;32m      5\u001b[0m     y_true\u001b[38;5;241m=\u001b[39my_te,\n\u001b[0;32m----> 6\u001b[0m     df_test\u001b[38;5;241m=\u001b[39m\u001b[43mdf_test\u001b[49m,\n\u001b[1;32m      7\u001b[0m     valid_tags\u001b[38;5;241m=\u001b[39mvalid_tags,\n\u001b[1;32m      8\u001b[0m     model_name\u001b[38;5;241m=\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mLightGBM (TF-IDF + FastText + ST)\u001b[39m\u001b[38;5;124m\"\u001b[39m,\n\u001b[1;32m      9\u001b[0m     k\u001b[38;5;241m=\u001b[39mTOP_K\n\u001b[1;32m     10\u001b[0m )\n\u001b[1;32m     12\u001b[0m \u001b[38;5;28mprint\u001b[39m(df_top20_test\u001b[38;5;241m.\u001b[39mhead(\u001b[38;5;241m3\u001b[39m))\n\u001b[1;32m     13\u001b[0m \u001b[38;5;28mprint\u001b[39m(\u001b[38;5;124mf\u001b[39m\u001b[38;5;124m\"\u001b[39m\u001b[38;5;130;01m\\n\u001b[39;00m\u001b[38;5;124mGenerated top-\u001b[39m\u001b[38;5;132;01m{\u001b[39;00mTOP_K\u001b[38;5;132;01m}\u001b[39;00m\u001b[38;5;124m predictions for \u001b[39m\u001b[38;5;132;01m{\u001b[39;00m\u001b[38;5;28mlen\u001b[39m(df_top20_test)\u001b[38;5;132;01m}\u001b[39;00m\u001b[38;5;124m test samples\u001b[39m\u001b[38;5;124m\"\u001b[39m)\n",
            "\u001b[0;31mNameError\u001b[0m: name 'df_test' is not defined"
          ]
        }
      ],
      "execution_count": 106,
      "metadata": {
        "gather": {
          "logged": 1778570372051
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"COMBINING ALL FEATURES\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "from scipy.sparse import hstack, csr_matrix\n",
        "from scipy.sparse import save_npz, load_npz\n",
        "# Convert advanced features to sparse format\n",
        "X_tr_advanced_sparse = csr_matrix(X_tr_advanced)\n",
        "X_val_advanced_sparse = csr_matrix(X_val_advanced)\n",
        "X_te_advanced_sparse = csr_matrix(X_te_advanced)\n",
        "\n",
        "# Combine: TF-IDF + FastText + Advanced Features\n",
        "X_tr_super_combined = hstack([X_tr_combined, X_tr_advanced_sparse])\n",
        "X_val_super_combined = hstack([X_val_combined, X_val_advanced_sparse])\n",
        "X_te_super_combined = hstack([X_te_combined, X_te_advanced_sparse])\n",
        "\n",
        "print(f\"\\nFeature breakdown:\")\n",
        "print(f\"  TF-IDF:           {X_tr_tfidf.shape[1]:,} features\")\n",
        "print(f\"  FastText:         100 features\")\n",
        "print(f\"  Advanced:         {X_tr_advanced.shape[1]} features\")\n",
        "print(f\"  ─────────────────────────────────────\")\n",
        "print(f\"  Total Combined:   {X_tr_super_combined.shape[1]:,} features\")\n",
        "\n",
        "print(f\"\\nFinal shapes:\")\n",
        "print(f\"  Train: {X_tr_super_combined.shape}\")\n",
        "print(f\"  Val:   {X_val_super_combined.shape}\")\n",
        "print(f\"  Test:  {X_te_super_combined.shape}\")\n",
        "\n",
        "# Save combined features\n",
        "save_npz(DATA_DIR / 'X_tr_super_combined.npz', X_tr_super_combined)\n",
        "save_npz(DATA_DIR / 'X_val_super_combined.npz', X_val_super_combined)\n",
        "save_npz(DATA_DIR / 'X_te_super_combined.npz', X_te_super_combined)\n",
        "\n",
        "print(f\"\\n✓ Combined features saved to {DATA_DIR}/\")\n",
        "print(\"\\n\" + \"=\" * 70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\n======================================================================\nCOMBINING ALL FEATURES\n======================================================================\n\nFeature breakdown:\n  TF-IDF:           20,000 features\n  FastText:         100 features\n  Advanced:         62 features\n  ─────────────────────────────────────\n  Total Combined:   20,162 features\n\nFinal shapes:\n  Train: (2987, 20162)\n  Val:   (341, 20162)\n  Test:  (341, 20162)\n\n✓ Combined features saved to saved_data/\n\n======================================================================\n"
        }
      ],
      "execution_count": 48,
      "metadata": {
        "gather": {
          "logged": 1778561039471
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# # In your Phase 5 LightGBM training, replace:\n",
        "# # X_tr_combined → X_tr_super_combined\n",
        "# # X_te_combined → X_te_super_combined\n",
        "\n",
        "# print(\"\\nPHASE 5: Train LightGBM with SUPER COMBINED Features\")\n",
        "# print(\"=\" * 70)\n",
        "\n",
        "# lgb_super_path = MODELS_DIR / 'lgb_super_combined_model.pkl'\n",
        "\n",
        "# if lgb_super_path.exists():\n",
        "#     print(f\"  ✓ Loading existing model from {lgb_super_path}\")\n",
        "#     with open(lgb_super_path, 'rb') as f:\n",
        "#         lgb_super = pickle.load(f)\n",
        "# else:\n",
        "#     print(\"  ✗ Training new model with ALL features...\")\n",
        "    \n",
        "#     lgb_super = OneVsRestClassifier(\n",
        "#         lgb.LGBMClassifier(\n",
        "#             n_estimators=400,        # Increased for more features\n",
        "#             max_depth=7,             # Increased depth\n",
        "#             learning_rate=0.08,      # Slightly lower\n",
        "#             subsample=0.8,\n",
        "#             colsample_bytree=0.7,    # Lower to prevent overfitting\n",
        "#             class_weight='balanced',\n",
        "#             random_state=42,\n",
        "#             n_jobs=-1,\n",
        "#             verbose=-1\n",
        "#         ),\n",
        "#         n_jobs=1\n",
        "#     )\n",
        "    \n",
        "#     print(f\"  Training on {X_tr_super_combined.shape[1]:,} features...\")\n",
        "#     lgb_super.fit(X_tr_super_combined, y_tr)\n",
        "    \n",
        "#     with open(lgb_super_path, 'wb') as f:\n",
        "#         pickle.dump(lgb_super, f)\n",
        "    \n",
        "#     lgb_super_preds = lgb_super.predict(X_te_super_combined)\n",
        "    \n",
        "#     macro_f1 = f1_score(y_te, lgb_super_preds, average='macro', zero_division=0)\n",
        "#     micro_f1 = f1_score(y_te, lgb_super_preds, average='micro', zero_division=0)\n",
        "    \n",
        "#     print(f\"\\n  Test Results:\")\n",
        "#     print(f\"    Macro F1: {macro_f1:.4f}\")\n",
        "#     print(f\"    Micro F1: {micro_f1:.4f}\")\n",
        "    \n",
        "#     save_per_tag_results(y_te, lgb_super_preds, valid_tags, \"lightgbm_super_combined\")\n",
        "    \n",
        "#     print(\"  ✓ Model saved and evaluated\")\n",
        "\n",
        "# print(\"=\" * 70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nPHASE 5: Train LightGBM with SUPER COMBINED Features\n======================================================================\n  ✗ Training new model with ALL features...\n  Training on 20,162 features...\n\n  Test Results:\n    Macro F1: 0.9157\n    Micro F1: 0.9910\n  Saved: saved_data/results/lightgbm_super_combined_results.csv\n  ✓ Model saved and evaluated\n======================================================================\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 39 is present in all training examples.\n  warnings.warn(\n/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 65 is present in all training examples.\n  warnings.warn(\n/anaconda/envs/azureml_py38/lib/python3.10/site-packages/lightgbm/basic.py:1238: UserWarning: Converting data to scipy sparse matrix.\n  _log_warning(\"Converting data to scipy sparse matrix.\")\n"
        }
      ],
      "execution_count": 37,
      "metadata": {
        "gather": {
          "logged": 1778550860116
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"len(proba_list):\", len(proba_list))\n",
        "print(\"y_te.shape[1]:\", y_te.shape[1])\n",
        "print(\"len(valid_tags):\", len(valid_tags))"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "len(proba_list): 341\ny_te.shape[1]: 94\nlen(valid_tags): 94\n"
        }
      ],
      "execution_count": 55,
      "metadata": {
        "gather": {
          "logged": 1778561657827
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "proba = lgb_super.predict_proba(X_te_super_combined)\n",
        "\n",
        "print(type(proba))\n",
        "print(\"proba shape:\", np.array(proba).shape)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "<class 'numpy.ndarray'>\nproba shape: (341, 94)\n"
        }
      ],
      "execution_count": 56,
      "metadata": {
        "gather": {
          "logged": 1778561701810
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "proba = lgb_super.predict_proba(X_te_super_combined)\n",
        "\n",
        "# Handle both OvR styles safely\n",
        "if isinstance(proba, list):\n",
        "    # List of (n_samples, 2)\n",
        "    lgb_probs = np.vstack([p[:, 1] for p in proba]).T\n",
        "else:\n",
        "    # Already (n_samples, n_labels)\n",
        "    lgb_probs = proba\n",
        "\n",
        "# Align labels defensively (if ever needed)\n",
        "n_labels = lgb_probs.shape[1]\n",
        "y_te = y_te[:, :n_labels]\n",
        "valid_tags = valid_tags[:n_labels]\n",
        "\n",
        "# Final check\n",
        "assert lgb_probs.shape == y_te.shape"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/lightgbm/basic.py:1238: UserWarning: Converting data to scipy sparse matrix.\n  _log_warning(\"Converting data to scipy sparse matrix.\")\n"
        }
      ],
      "execution_count": 61,
      "metadata": {
        "gather": {
          "logged": 1778561843610
        }
      }
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [
        {
          "output_type": "error",
          "ename": "IndexError",
          "evalue": "too many indices for array: array is 1-dimensional, but 2 were indexed",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mIndexError\u001b[0m                                Traceback (most recent call last)",
            "Cell \u001b[0;32mIn[57], line 4\u001b[0m\n\u001b[1;32m      1\u001b[0m proba_list \u001b[38;5;241m=\u001b[39m lgb_super\u001b[38;5;241m.\u001b[39mpredict_proba(X_te_super_combined)\n\u001b[1;32m      3\u001b[0m \u001b[38;5;66;03m# Convert to (n_samples, n_labels)\u001b[39;00m\n\u001b[0;32m----> 4\u001b[0m lgb_probs \u001b[38;5;241m=\u001b[39m np\u001b[38;5;241m.\u001b[39mvstack([p[:, \u001b[38;5;241m1\u001b[39m] \u001b[38;5;28;01mfor\u001b[39;00m p \u001b[38;5;129;01min\u001b[39;00m proba_list])\u001b[38;5;241m.\u001b[39mT\n\u001b[1;32m      6\u001b[0m \u001b[38;5;28mprint\u001b[39m(\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mProbability matrix shape:\u001b[39m\u001b[38;5;124m\"\u001b[39m, lgb_probs\u001b[38;5;241m.\u001b[39mshape)\n\u001b[1;32m      7\u001b[0m \u001b[38;5;28;01massert\u001b[39;00m lgb_probs\u001b[38;5;241m.\u001b[39mshape \u001b[38;5;241m==\u001b[39m y_te\u001b[38;5;241m.\u001b[39mshape\n",
            "Cell \u001b[0;32mIn[57], line 4\u001b[0m, in \u001b[0;36m<listcomp>\u001b[0;34m(.0)\u001b[0m\n\u001b[1;32m      1\u001b[0m proba_list \u001b[38;5;241m=\u001b[39m lgb_super\u001b[38;5;241m.\u001b[39mpredict_proba(X_te_super_combined)\n\u001b[1;32m      3\u001b[0m \u001b[38;5;66;03m# Convert to (n_samples, n_labels)\u001b[39;00m\n\u001b[0;32m----> 4\u001b[0m lgb_probs \u001b[38;5;241m=\u001b[39m np\u001b[38;5;241m.\u001b[39mvstack([\u001b[43mp\u001b[49m\u001b[43m[\u001b[49m\u001b[43m:\u001b[49m\u001b[43m,\u001b[49m\u001b[43m \u001b[49m\u001b[38;5;241;43m1\u001b[39;49m\u001b[43m]\u001b[49m \u001b[38;5;28;01mfor\u001b[39;00m p \u001b[38;5;129;01min\u001b[39;00m proba_list])\u001b[38;5;241m.\u001b[39mT\n\u001b[1;32m      6\u001b[0m \u001b[38;5;28mprint\u001b[39m(\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mProbability matrix shape:\u001b[39m\u001b[38;5;124m\"\u001b[39m, lgb_probs\u001b[38;5;241m.\u001b[39mshape)\n\u001b[1;32m      7\u001b[0m \u001b[38;5;28;01massert\u001b[39;00m lgb_probs\u001b[38;5;241m.\u001b[39mshape \u001b[38;5;241m==\u001b[39m y_te\u001b[38;5;241m.\u001b[39mshape\n",
            "\u001b[0;31mIndexError\u001b[0m: too many indices for array: array is 1-dimensional, but 2 were indexed"
          ]
        }
      ],
      "execution_count": 57,
      "metadata": {
        "gather": {
          "logged": 1778561729998
        },
        "jupyter": {
          "outputs_hidden": true
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "lgb_topk = generate_topk_predictions(\n",
        "    probs=lgb_probs,\n",
        "    y_true=y_te,\n",
        "    df_test=df_te,\n",
        "    valid_tags=valid_tags,\n",
        "    model_name=\"LightGBM_SUPER\",\n",
        "    k=10\n",
        ")\n",
        "\n",
        "lgb_topk.to_csv(\n",
        "    RESULTS_DIR / \"lightgbm_super_top10_predictions.csv\",\n",
        "    index=False\n",
        ")\n",
        "\n",
        "print(\"✓ LightGBM Top‑K results extracted and saved\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✓ LightGBM Top‑K results extracted and saved\n"
        }
      ],
      "execution_count": 62,
      "metadata": {
        "gather": {
          "logged": 1778561849250
        }
      }
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "markdown",
      "source": [
        "#### TESTING MODEL RESULTS ON RANDOM SAMPLE 100\n"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# import joblib\n",
        "# import pickle\n",
        "# import numpy as np\n",
        "# from gensim.models import FastText\n",
        "# from scipy.sparse import hstack\n",
        "\n",
        "# # Load model\n",
        "# lgb_super = joblib.load(\"saved_models/lgb_super_combined_model.pkl\")\n",
        "\n",
        "# # Load TF‑IDF\n",
        "# tfidf = joblib.load(\"lgb_tfidf_fasttext_ovr.joblib\")\n",
        "\n",
        "# # Load FastText\n",
        "# ft_model = FastText.load(\"fasttext.model\")\n",
        "\n",
        "# # Load advanced feature scaler\n",
        "# with open(\"saved_data/advanced_features_scaler.pkl\", \"rb\") as f:\n",
        "#     adv_scaler = pickle.load(f)\n",
        "\n",
        "# print(\"✅ All artifacts loaded\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✅ All artifacts loaded\n"
        }
      ],
      "execution_count": 67,
      "metadata": {
        "gather": {
          "logged": 1778562091812
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# import joblib\n",
        "\n",
        "# tfidf = joblib.load(\"tfidf_vectorizer.joblib\")\n",
        "\n",
        "# print(type(tfidf))\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "<class 'sklearn.feature_extraction.text.TfidfVectorizer'>\n"
        }
      ],
      "execution_count": 73,
      "metadata": {
        "gather": {
          "logged": 1778562402183
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# df_new=pd.read_csv(\"sampled_100_complaints_by_tier2.csv\")"
      ],
      "outputs": [],
      "execution_count": 68,
      "metadata": {
        "gather": {
          "logged": 1778562145004
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# new_texts = [build_text(row) for _, row in df_new.iterrows()]"
      ],
      "outputs": [],
      "execution_count": 69,
      "metadata": {
        "gather": {
          "logged": 1778562159912
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# X_new_tfidf = tfidf.transform(new_texts)\n",
        "\n",
        "# print(\"TF‑IDF shape:\", X_new_tfidf.shape)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "TF‑IDF shape: (100, 20000)\n"
        }
      ],
      "execution_count": 74,
      "metadata": {
        "gather": {
          "logged": 1778562406089
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# # Build text\n",
        "# new_texts = [build_text(row) for _, row in df_new.iterrows()]\n",
        "\n",
        "# # TF‑IDF\n",
        "# X_new_tfidf = tfidf.transform(new_texts)\n",
        "\n",
        "# # FastText\n",
        "# X_new_ft = np.vstack([\n",
        "#     doc_to_fasttext_vector(text, ft_model)\n",
        "#     for text in new_texts\n",
        "# ])\n",
        "\n",
        "# # Advanced\n",
        "# X_new_adv = adv_scaler.transform(extract_advanced_features(df_new))\n",
        "\n",
        "# # SUPER COMBINE\n",
        "# X_new_super = hstack([X_new_tfidf, X_new_ft, X_new_adv])\n",
        "\n",
        "# print(\"✅ Final feature shape:\", X_new_super.shape)\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✅ Final feature shape: (100, 20162)\n"
        }
      ],
      "execution_count": 75,
      "metadata": {
        "gather": {
          "logged": 1778562437695
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# proba = lgb_super.predict_proba(X_new_super)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/lightgbm/basic.py:1238: UserWarning: Converting data to scipy sparse matrix.\n  _log_warning(\"Converting data to scipy sparse matrix.\")\n"
        }
      ],
      "execution_count": 76,
      "metadata": {
        "gather": {
          "logged": 1778562453911
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# print(lgb_probs.shape)\n",
        "# print(len(valid_tags))"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "(341, 94)\n94\n"
        }
      ],
      "execution_count": 77,
      "metadata": {
        "gather": {
          "logged": 1778562501837
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# import numpy as np\n",
        "# import pandas as pd\n",
        "\n",
        "# def generate_topk_predictions_by_case(\n",
        "#     probs,\n",
        "#     df_cases,\n",
        "#     tag_names,\n",
        "#     k=15,\n",
        "#     case_id_col=\"case_reference\",\n",
        "#     actual_col=\"tier_2\"   # <-- CHANGE if your column name differs\n",
        "# ):\n",
        "#     \"\"\"\n",
        "#     Generate Top-K predicted tags per case WITH actual Tier-2 labels.\n",
        "#     \"\"\"\n",
        "#     rows = []\n",
        "\n",
        "#     for i in range(len(df_cases)):\n",
        "#         # ----- ACTUAL TAGS -----\n",
        "#         actual = df_cases.iloc[i].get(actual_col, [])\n",
        "#         if pd.isna(actual):\n",
        "#             actual = []\n",
        "#         elif isinstance(actual, str):\n",
        "#             actual = [actual]\n",
        "\n",
        "#         # ----- TOP-K PREDICTIONS -----\n",
        "#         top_idx = np.argsort(probs[i])[::-1][:k]\n",
        "#         top_tags = [tag_names[j] for j in top_idx]\n",
        "#         top_probs = [float(probs[i, j]) for j in top_idx]\n",
        "\n",
        "#         row = {\n",
        "#             \"case_reference\": df_cases.iloc[i].get(case_id_col, f\"case_{i}\"),\n",
        "#             \"summary\": df_cases.iloc[i].get(\"summary\", \"\"),\n",
        "#             \"actual_tier_2\": \", \".join(actual),\n",
        "#             f\"top_{k}_tags\": \", \".join(top_tags),\n",
        "#             f\"top_{k}_probabilities\": \", \".join(\n",
        "#                 [f\"{p:.4f}\" for p in top_probs]\n",
        "#             ),\n",
        "#         }\n",
        "\n",
        "#         # Save ranked tags individually\n",
        "#         for rank, (tag, prob) in enumerate(zip(top_tags, top_probs), start=1):\n",
        "#             row[f\"rank_{rank}_tag\"] = tag\n",
        "#             row[f\"rank_{rank}_prob\"] = round(prob, 4)\n",
        "#             row[f\"rank_{rank}_is_correct\"] = tag in actual\n",
        "\n",
        "#         rows.append(row)\n",
        "\n",
        "#     return pd.DataFrame(rows)\n"
      ],
      "outputs": [],
      "execution_count": 81,
      "metadata": {
        "gather": {
          "logged": 1778562683003
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# top15_predictions = generate_topk_predictions_by_case(\n",
        "#     probs=lgb_probs,     # (100, n_labels)\n",
        "#     df_cases=df_new,     # 100 complaints\n",
        "#     tag_names=valid_tags,\n",
        "#     k=15,\n",
        "#     case_id_col=\"case_reference\"   # change if your ID column differs\n",
        "# )"
      ],
      "outputs": [],
      "execution_count": 82,
      "metadata": {
        "gather": {
          "logged": 1778562685119
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# output_file = \"lightgbm_top15_predictions_by_case.csv\"\n",
        "# top15_predictions.to_csv(output_file, index=False)\n",
        "\n",
        "# print(f\" Top‑15 predictions saved to {output_file}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": " Top‑15 predictions saved to lightgbm_top15_predictions_by_case.csv\n"
        }
      ],
      "execution_count": 83,
      "metadata": {
        "gather": {
          "logged": 1778562686985
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# df_new.columns"
      ],
      "outputs": [
        {
          "output_type": "execute_result",
          "execution_count": 88,
          "data": {
            "text/plain": "Index(['case_reference', 'summary', 'tier_2'], dtype='object')"
          },
          "metadata": {}
        }
      ],
      "execution_count": 88,
      "metadata": {
        "gather": {
          "logged": 1778564162908
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# import pickle\n",
        "# import numpy as np\n",
        "\n",
        "# with open(MODELS_DIR / \"lgb_super_combined_model.pkl\", \"rb\") as f:\n",
        "#     lgb_super = pickle.load(f)\n",
        "\n",
        "# print(\"✓ LightGBM model loaded\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✓ LightGBM model loaded\n"
        }
      ],
      "execution_count": 6,
      "metadata": {
        "gather": {
          "logged": 1778559776874
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# combined_path = DATA_DIR / \"/advanced_features.npz\"\n",
        "\n",
        "# if combined_path.exists():\n",
        "#     loaded = np.load(combined_path, allow_pickle=True)\n",
        "#     X_tr_super_combined = loaded[\"X_tr_advanced\"]\n",
        "#     X_val_super_combined = loaded[\"X_val_advanced\"]\n",
        "#     X_te_super_combined = loaded[\"X_te_advanced\"]\n",
        "\n",
        "#     print(\"✓ Loaded combined features from disk\")\n",
        "#     print(\"Test shape:\", X_te_super_combined.shape)"
      ],
      "outputs": [],
      "execution_count": 9,
      "metadata": {
        "gather": {
          "logged": 1778559920521
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# import joblib\n",
        "\n",
        "# tfidf = joblib.load(\"tfidf_vectorizer.joblib\")\n",
        "\n",
        "# print(\"✅ TF‑IDF vectorizer loaded\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✅ TF‑IDF vectorizer loaded\n"
        }
      ],
      "execution_count": 16,
      "metadata": {
        "gather": {
          "logged": 1778560198522
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# import numpy as np\n",
        "\n",
        "# combined_path = DATA_DIR / \"advanced_features.npz\"\n",
        "\n",
        "# if combined_path.exists():\n",
        "#     loaded = np.load(combined_path, allow_pickle=True)\n",
        "    \n",
        "#     X_tr_super_combined = loaded[\"X_tr_advanced\"]\n",
        "#     X_val_super_combined = loaded[\"X_val_advanced\"]\n",
        "#     X_te_super_combined = loaded[\"X_te_advanced\"]\n",
        "\n",
        "#     print(\"✓ Loaded combined features from disk\")\n",
        "#     print(\"Train shape:\", X_tr_super_combined.shape)\n",
        "#     print(\"Val shape:  \", X_val_super_combined.shape)\n",
        "#     print(\"Test shape: \", X_te_super_combined.shape)\n",
        "# else:\n",
        "#     print(\"❌ Combined feature file not found:\", combined_path)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✓ Loaded combined features from disk\nTrain shape: (2987, 62)\nVal shape:   (341, 62)\nTest shape:  (341, 62)\n"
        }
      ],
      "execution_count": 19,
      "metadata": {
        "gather": {
          "logged": 1778560396693
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "assert X_te_super_combined is not None\n"
      ],
      "outputs": [],
      "execution_count": 20,
      "metadata": {
        "gather": {
          "logged": 1778560404740
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# # ══════════════════════════════════════════════════════════════════════════════\n",
        "# # Calculate Micro & Macro Metrics for LightGBM Predictions\n",
        "# # ══════════════════════════════════════════════════════════════════════════════\n",
        "\n",
        "# import pandas as pd\n",
        "# import numpy as np\n",
        "# from sklearn.metrics import precision_score, recall_score, f1_score\n",
        "# from sklearn.metrics import classification_report, hamming_loss, accuracy_score\n",
        "# from sklearn.preprocessing import MultiLabelBinarizer\n",
        "\n",
        "# # ── Load predictions ──────────────────────────────────────────────────────────\n",
        "# df = pd.read_csv('lightgbm_top15_predictions_by_case.csv')\n",
        "\n",
        "# print(f\"Loaded {len(df):,} predictions\\n\")\n",
        "\n",
        "# # ── Parse actual and predicted labels ─────────────────────────────────────────\n",
        "# def parse_labels(val):\n",
        "#     if pd.isna(val) or str(val).strip() == '':\n",
        "#         return []\n",
        "#     if isinstance(val, list):\n",
        "#         return [t.strip() for t in val if str(t).strip()]\n",
        "#     return [t.strip() for t in str(val).split(',') if t.strip()]\n",
        "\n",
        "# df['actual_labels'] = df['actual_tier_2'].apply(parse_labels)\n",
        "# df['predicted_labels'] = df['top_15_tags'].apply(parse_labels)\n",
        "\n",
        "# # ── Get all unique tags ───────────────────────────────────────────────────────\n",
        "# all_tags = set()\n",
        "# for labels in df['actual_labels']:\n",
        "#     all_tags.update(labels)\n",
        "# for labels in df['predicted_labels']:\n",
        "#     all_tags.update(labels)\n",
        "\n",
        "# all_tags = sorted(list(all_tags))\n",
        "# print(f\"Total unique tags: {len(all_tags)}\\n\")\n",
        "\n",
        "# # ── Binarize labels ───────────────────────────────────────────────────────────\n",
        "# mlb = MultiLabelBinarizer(classes=all_tags)\n",
        "# y_true = mlb.fit_transform(df['actual_labels'])\n",
        "# y_pred = mlb.transform(df['predicted_labels'])\n",
        "\n",
        "# print(f\"y_true shape: {y_true.shape}\")\n",
        "# print(f\"y_pred shape: {y_pred.shape}\\n\")\n",
        "\n",
        "# # ══════════════════════════════════════════════════════════════════════════════\n",
        "# # Calculate Metrics\n",
        "# # ══════════════════════════════════════════════════════════════════════════════\n",
        "\n",
        "# print(\"=\"*70)\n",
        "# print(\"MULTI-LABEL CLASSIFICATION METRICS\")\n",
        "# print(\"=\"*70)\n",
        "\n",
        "# # ── Micro-averaged metrics (aggregate all labels) ─────────────────────────────\n",
        "# micro_precision = precision_score(y_true, y_pred, average='micro', zero_division=0)\n",
        "# micro_recall = recall_score(y_true, y_pred, average='micro', zero_division=0)\n",
        "# micro_f1 = f1_score(y_true, y_pred, average='micro', zero_division=0)\n",
        "\n",
        "# print(\"\\nMICRO-AVERAGED METRICS (aggregate all labels):\")\n",
        "# print(f\"  Precision: {micro_precision:.4f}  ({micro_precision*100:.2f}%)\")\n",
        "# print(f\"  Recall:    {micro_recall:.4f}  ({micro_recall*100:.2f}%)\")\n",
        "# print(f\"  F1 Score:  {micro_f1:.4f}  ({micro_f1*100:.2f}%)\")\n",
        "\n",
        "# # ── Macro-averaged metrics (average of per-tag metrics) ───────────────────────\n",
        "# macro_precision = precision_score(y_true, y_pred, average='macro', zero_division=0)\n",
        "# macro_recall = recall_score(y_true, y_pred, average='macro', zero_division=0)\n",
        "# macro_f1 = f1_score(y_true, y_pred, average='macro', zero_division=0)\n",
        "\n",
        "# print(\"\\nMACRO-AVERAGED METRICS (average per-tag performance):\")\n",
        "# print(f\"  Precision: {macro_precision:.4f}  ({macro_precision*100:.2f}%)\")\n",
        "# print(f\"  Recall:    {macro_recall:.4f}  ({macro_recall*100:.2f}%)\")\n",
        "# print(f\"  F1 Score:  {macro_f1:.4f}  ({macro_f1*100:.2f}%)\")\n",
        "\n",
        "# # ── Weighted-averaged metrics (weighted by tag support) ───────────────────────\n",
        "# weighted_precision = precision_score(y_true, y_pred, average='weighted', zero_division=0)\n",
        "# weighted_recall = recall_score(y_true, y_pred, average='weighted', zero_division=0)\n",
        "# weighted_f1 = f1_score(y_true, y_pred, average='weighted', zero_division=0)\n",
        "\n",
        "# print(\"\\nWEIGHTED-AVERAGED METRICS (weighted by tag frequency):\")\n",
        "# print(f\"  Precision: {weighted_precision:.4f}  ({weighted_precision*100:.2f}%)\")\n",
        "# print(f\"  Recall:    {weighted_recall:.4f}  ({weighted_recall*100:.2f}%)\")\n",
        "# print(f\"  F1 Score:  {weighted_f1:.4f}  ({weighted_f1*100:.2f}%)\")\n",
        "\n",
        "# # ── Samples-averaged metrics (average per-complaint) ──────────────────────────\n",
        "# samples_precision = precision_score(y_true, y_pred, average='samples', zero_division=0)\n",
        "# samples_recall = recall_score(y_true, y_pred, average='samples', zero_division=0)\n",
        "# samples_f1 = f1_score(y_true, y_pred, average='samples', zero_division=0)\n",
        "\n",
        "# print(\"\\nSAMPLES-AVERAGED METRICS (average per-complaint):\")\n",
        "# print(f\"  Precision: {samples_precision:.4f}  ({samples_precision*100:.2f}%)\")\n",
        "# print(f\"  Recall:    {samples_recall:.4f}  ({samples_recall*100:.2f}%)\")\n",
        "# print(f\"  F1 Score:  {samples_f1:.4f}  ({samples_f1*100:.2f}%)\")\n",
        "\n",
        "# # ── Additional metrics ────────────────────────────────────────────────────────\n",
        "# hamming = hamming_loss(y_true, y_pred)\n",
        "# subset_accuracy = accuracy_score(y_true, y_pred)\n",
        "\n",
        "# print(\"\\nADDITIONAL METRICS:\")\n",
        "# print(f\"  Hamming Loss:     {hamming:.4f}  (lower is better)\")\n",
        "# print(f\"  Subset Accuracy:  {subset_accuracy:.4f}  ({subset_accuracy*100:.2f}%) — exact match\")\n",
        "\n",
        "# # ── Per-tag metrics ───────────────────────────────────────────────────────────\n",
        "# print(\"\\n\" + \"=\"*70)\n",
        "# print(\"PER-TAG PERFORMANCE (sorted by F1 score)\")\n",
        "# print(\"=\"*70)\n",
        "\n",
        "# per_tag_metrics = []\n",
        "# for i, tag in enumerate(all_tags):\n",
        "#     y_true_tag = y_true[:, i]\n",
        "#     y_pred_tag = y_pred[:, i]\n",
        "    \n",
        "#     support = int(y_true_tag.sum())\n",
        "#     if support == 0:\n",
        "#         continue  # Skip tags not in actual labels\n",
        "    \n",
        "#     precision = precision_score(y_true_tag, y_pred_tag, zero_division=0)\n",
        "#     recall = recall_score(y_true_tag, y_pred_tag, zero_division=0)\n",
        "#     f1 = f1_score(y_true_tag, y_pred_tag, zero_division=0)\n",
        "    \n",
        "#     per_tag_metrics.append({\n",
        "#         'tag': tag,\n",
        "#         'support': support,\n",
        "#         'precision': round(precision, 4),\n",
        "#         'recall': round(recall, 4),\n",
        "#         'f1_score': round(f1, 4)\n",
        "#     })\n",
        "\n",
        "# per_tag_df = pd.DataFrame(per_tag_metrics).sort_values('f1_score', ascending=False)\n",
        "# per_tag_df.to_csv('per_tag_performance.csv', index=False)\n",
        "\n",
        "# print(f\"\\nTop 20 tags by F1 score:\")\n",
        "# print(per_tag_df.head(20).to_string(index=False))\n",
        "\n",
        "# print(f\"\\nBottom 20 tags by F1 score:\")\n",
        "# print(per_tag_df.tail(20).to_string(index=False))\n",
        "\n",
        "# print(f\"\\n✓ Saved: per_tag_performance.csv\")\n",
        "\n",
        "# # ── Summary by tag frequency ──────────────────────────────────────────────────\n",
        "# print(\"\\n\" + \"=\"*70)\n",
        "# print(\"PERFORMANCE BY TAG FREQUENCY\")\n",
        "# print(\"=\"*70)\n",
        "\n",
        "# per_tag_df['frequency_tier'] = pd.cut(\n",
        "#     per_tag_df['support'], \n",
        "#     bins=[0, 30, 150, float('inf')], \n",
        "#     labels=['RARE (<30)', 'MEDIUM (30-149)', 'DOMINANT (≥150)']\n",
        "# )\n",
        "\n",
        "# freq_summary = per_tag_df.groupby('frequency_tier').agg({\n",
        "#     'tag': 'count',\n",
        "#     'precision': 'mean',\n",
        "#     'recall': 'mean',\n",
        "#     'f1_score': 'mean',\n",
        "#     'support': 'sum'\n",
        "# }).round(4)\n",
        "\n",
        "# freq_summary.columns = ['tag_count', 'avg_precision', 'avg_recall', 'avg_f1', 'total_labels']\n",
        "# print(freq_summary)\n",
        "\n",
        "# # ── Save comprehensive summary ────────────────────────────────────────────────\n",
        "# summary_df = pd.DataFrame({\n",
        "#     'metric': [\n",
        "#         'Micro Precision', 'Micro Recall', 'Micro F1',\n",
        "#         'Macro Precision', 'Macro Recall', 'Macro F1',\n",
        "#         'Weighted Precision', 'Weighted Recall', 'Weighted F1',\n",
        "#         'Samples Precision', 'Samples Recall', 'Samples F1',\n",
        "#         'Hamming Loss', 'Subset Accuracy'\n",
        "#     ],\n",
        "#     'value': [\n",
        "#         micro_precision, micro_recall, micro_f1,\n",
        "#         macro_precision, macro_recall, macro_f1,\n",
        "#         weighted_precision, weighted_recall, weighted_f1,\n",
        "#         samples_precision, samples_recall, samples_f1,\n",
        "#         hamming, subset_accuracy\n",
        "#     ]\n",
        "# })\n",
        "\n",
        "# summary_df['percentage'] = (summary_df['value'] * 100).round(2)\n",
        "# summary_df.to_csv('evaluation_summary.csv', index=False)\n",
        "\n",
        "# print(f\"\\n✓ Saved: evaluation_summary.csv\")\n",
        "\n",
        "# # ── Key insights ──────────────────────────────────────────────────────────────\n",
        "# print(\"\\n\" + \"=\"*70)\n",
        "# print(\"KEY INSIGHTS\")\n",
        "# print(\"=\"*70)\n",
        "# print(f\"• Micro F1 ({micro_f1:.2%}) shows overall label-level performance\")\n",
        "# print(f\"• Macro F1 ({macro_f1:.2%}) shows average per-tag performance (treats all tags equally)\")\n",
        "# print(f\"• Weighted F1 ({weighted_f1:.2%}) accounts for tag imbalance\")\n",
        "# print(f\"• Samples F1 ({samples_f1:.2%}) shows per-complaint accuracy\")\n",
        "# print(f\"• Subset Accuracy ({subset_accuracy:.2%}) = exact match rate (all tags correct)\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Loaded 100 predictions\n\nTotal unique tags: 188\n\ny_true shape: (100, 188)\ny_pred shape: (100, 188)\n\n======================================================================\nMULTI-LABEL CLASSIFICATION METRICS\n======================================================================\n\nMICRO-AVERAGED METRICS (aggregate all labels):\n  Precision: 0.0000  (0.00%)\n  Recall:    0.0000  (0.00%)\n  F1 Score:  0.0000  (0.00%)\n\nMACRO-AVERAGED METRICS (average per-tag performance):\n  Precision: 0.0000  (0.00%)\n  Recall:    0.0000  (0.00%)\n  F1 Score:  0.0000  (0.00%)\n\nWEIGHTED-AVERAGED METRICS (weighted by tag frequency):\n  Precision: 0.0000  (0.00%)\n  Recall:    0.0000  (0.00%)\n  F1 Score:  0.0000  (0.00%)\n\nSAMPLES-AVERAGED METRICS (average per-complaint):\n  Precision: 0.0000  (0.00%)\n  Recall:    0.0000  (0.00%)\n  F1 Score:  0.0000  (0.00%)\n\nADDITIONAL METRICS:\n  Hamming Loss:     0.0856  (lower is better)\n  Subset Accuracy:  0.0000  (0.00%) — exact match\n\n======================================================================\nPER-TAG PERFORMANCE (sorted by F1 score)\n======================================================================\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/tmp/ipykernel_3102/270411684.py:149: FutureWarning: The default of observed=False is deprecated and will be changed to True in a future version of pandas. Pass observed=False to retain current behavior or observed=True to adopt the future default and silence this warning.\n  freq_summary = per_tag_df.groupby('frequency_tier').agg({\n"
        }
      ],
      "execution_count": 96,
      "metadata": {
        "gather": {
          "logged": 1778564544870
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import torch\n",
        "import torch.nn as nn\n",
        "\n",
        "class HybridMLP(nn.Module):\n",
        "    def __init__(self, input_dim, num_labels):\n",
        "        super().__init__()\n",
        "        self.net = nn.Sequential(\n",
        "            nn.Linear(input_dim, 50),   # matches paper\n",
        "            nn.ReLU(),\n",
        "            nn.Dropout(0.3),\n",
        "            nn.Linear(50, num_labels),\n",
        "            nn.Sigmoid()\n",
        "        )\n",
        "\n",
        "    def forward(self, x):\n",
        "        return self.net(x)\n",
        "model = HybridMLP(\n",
        "    input_dim=X_tr_combined.shape[1],\n",
        "    num_labels=y_tr.shape[1]\n",
        ")\n",
        "\n",
        "criterion = nn.BCELoss()  # multi-label\n",
        "optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)\n",
        "Xtr = torch.FloatTensor(X_tr_combined.toarray())\n",
        "ytr = torch.FloatTensor(y_tr)\n",
        "\n",
        "Xval = torch.FloatTensor(X_val_combined.toarray())\n",
        "yval = torch.FloatTensor(y_val)\n",
        "for epoch in range(20):\n",
        "    model.train()\n",
        "    optimizer.zero_grad()\n",
        "\n",
        "    out = model(Xtr)\n",
        "    loss = criterion(out, ytr)\n",
        "    loss.backward()\n",
        "    optimizer.step()\n",
        "\n",
        "    model.eval()\n",
        "    with torch.no_grad():\n",
        "        val_loss = criterion(model(Xval), yval)\n",
        "\n",
        "    print(f\"Epoch {epoch+1:02d} | Train Loss {loss:.4f} | Val Loss {val_loss:.4f}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Epoch 01 | Train Loss 0.6890 | Val Loss 0.6856\nEpoch 02 | Train Loss 0.6856 | Val Loss 0.6818\nEpoch 03 | Train Loss 0.6818 | Val Loss 0.6773\nEpoch 04 | Train Loss 0.6773 | Val Loss 0.6721\nEpoch 05 | Train Loss 0.6721 | Val Loss 0.6661\nEpoch 06 | Train Loss 0.6663 | Val Loss 0.6595\nEpoch 07 | Train Loss 0.6598 | Val Loss 0.6522\nEpoch 08 | Train Loss 0.6525 | Val Loss 0.6441\nEpoch 09 | Train Loss 0.6445 | Val Loss 0.6353\nEpoch 10 | Train Loss 0.6358 | Val Loss 0.6258\nEpoch 11 | Train Loss 0.6263 | Val Loss 0.6155\nEpoch 12 | Train Loss 0.6163 | Val Loss 0.6045\nEpoch 13 | Train Loss 0.6057 | Val Loss 0.5929\nEpoch 14 | Train Loss 0.5944 | Val Loss 0.5806\nEpoch 15 | Train Loss 0.5819 | Val Loss 0.5676\nEpoch 16 | Train Loss 0.5696 | Val Loss 0.5540\nEpoch 17 | Train Loss 0.5559 | Val Loss 0.5399\nEpoch 18 | Train Loss 0.5420 | Val Loss 0.5253\nEpoch 19 | Train Loss 0.5281 | Val Loss 0.5101\nEpoch 20 | Train Loss 0.5137 | Val Loss 0.4946\n"
        }
      ],
      "execution_count": 37,
      "metadata": {
        "gather": {
          "logged": 1778137635922
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "model.eval()\n",
        "\n",
        "with torch.no_grad():\n",
        "    mlp_probs = model(torch.FloatTensor(X_te_combined.toarray())).cpu().numpy()\n",
        "\n",
        "mlp_probs.shape == (n_samples, n_tags)\n",
        "THRESHOLD = 0.5\n",
        "mlp_preds = (mlp_probs >= THRESHOLD).astype(int)\n",
        "\n",
        "save_per_tag_results(y_te, mlp_preds, valid_tags, \"hybrid_mlp\")\n",
        "per_tag_df = pd.read_csv(\n",
        "    \"saved_data/results/hybrid_mlp_results2.csv\"\n",
        ")\n",
        "\n",
        "per_tag_metrics = (\n",
        "    per_tag_df\n",
        "    .set_index(\"tag\")[[\"precision\", \"recall\", \"f1\"]]\n",
        "    .to_dict(orient=\"index\")\n",
        ")\n",
        "\n",
        "rows = []\n",
        "\n",
        "for i in range(y_te.shape[0]):\n",
        "\n",
        "    # Actual tags\n",
        "    actual_tags = [\n",
        "        valid_tags[j] for j in np.where(y_te[i] == 1)[0]\n",
        "    ]\n",
        "\n",
        "    probs = mlp_probs[i]\n",
        "\n",
        "    # Top‑5 predictions\n",
        "    top5_idx = probs.argsort()[-5:][::-1]\n",
        "    top5_tags = [valid_tags[j] for j in top5_idx]\n",
        "    top5_probs = [probs[j] for j in top5_idx]\n",
        "\n",
        "    # Metrics for those tags\n",
        "    top5_metrics = [\n",
        "        per_tag_metrics.get(tag, {\"f1\": 0, \"precision\": 0, \"recall\": 0})\n",
        "        for tag in top5_tags\n",
        "    ]\n",
        "\n",
        "    rows.append({\n",
        "        \"case_reference\": (\n",
        "            df_te.iloc[i][\"case_reference\"]\n",
        "            if \"case_reference\" in df_te.columns else i\n",
        "        ),\n",
        "        \"actual_tier_2\": \", \".join(actual_tags),\n",
        "        \"top5_predicted_tier_2\": \", \".join(top5_tags),\n",
        "        \"top5_confidence\": \", \".join([f\"{p:.3f}\" for p in top5_probs]),\n",
        "        \"top5_f1\": \", \".join([f\"{m['f1']:.3f}\" for m in top5_metrics]),\n",
        "        \"top5_precision\": \", \".join([f\"{m['precision']:.3f}\" for m in top5_metrics]),\n",
        "        \"top5_recall\": \", \".join([f\"{m['recall']:.3f}\" for m in top5_metrics]),\n",
        "    })\n",
        "\n",
        "results_df_mlp = pd.DataFrame(rows)\n",
        "\n",
        "display(results_df_mlp.head(20))\n",
        "\n",
        "results_df_mlp.to_csv(\n",
        "    \"saved_data/results/complaint_predictions_with_metrics_hybrid_mlp2.csv\",\n",
        "    index=False\n",
        ")\n",
        "\n",
        "print(\n",
        "    \"Saved: saved_data/results/\"\n",
        "    \"complaint_predictions_with_metrics_hybrid_mlp2.csv\"\n",
        ")"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "from scipy.sparse import csr_matrix\n",
        "\n",
        "X_tr_combined  = hstack([X_tr_tfidf, X_tr_ft]).tocsr()\n",
        "X_val_combined = hstack([X_val_tfidf, X_val_ft]).tocsr()\n",
        "X_te_combined  = hstack([X_te_tfidf,  X_te_ft]).tocsr()"
      ],
      "outputs": [],
      "execution_count": 18,
      "metadata": {
        "gather": {
          "logged": 1778496979649
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(type(X_tr_combined))\n",
        "print(X_tr_combined.getformat())\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "<class 'scipy.sparse._csr.csr_matrix'>\ncsr\n"
        }
      ],
      "execution_count": 19,
      "metadata": {
        "gather": {
          "logged": 1778496979984
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "I got a warning that label x is present everywhere i am double checking to void overfitting"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import numpy as np\n",
        "\n",
        "n_samples = y_tr.shape[0]\n",
        "label_sums = y_tr.sum(axis=0)\n",
        "\n",
        "always_on_idx = np.where(label_sums == n_samples)[0]\n",
        "never_on_idx  = np.where(label_sums == 0)[0]\n",
        "\n",
        "print(\"Labels present in ALL training samples:\")\n",
        "print([valid_tags[i] for i in always_on_idx])\n",
        "\n",
        "print(\"\\nLabels present in ZERO training samples:\")\n",
        "print([valid_tags[i] for i in never_on_idx])"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Labels present in ALL training samples:\n[]\n\nLabels present in ZERO training samples:\n['Premature objection']\n"
        }
      ],
      "execution_count": 20,
      "metadata": {
        "gather": {
          "logged": 1778496980357
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# ── BLOCK 9B: Baseline Comparison — OvR XGBoost & LightGBM ──────────────\n",
        "\n",
        "from sklearn.feature_extraction.text import TfidfVectorizer\n",
        "from sklearn.multiclass import OneVsRestClassifier\n",
        "from sklearn.metrics import f1_score, classification_report\n",
        "import xgboost as xgb\n",
        "import lightgbm as lgb\n",
        "import pandas as pd\n",
        "import numpy as np\n",
        "import os\n",
        "\n",
        "# ── Create output folder ──────────────────────────────────────────────────\n",
        "os.makedirs('saved_data/results', exist_ok=True)\n",
        "\n",
        "RANDOM_SEED = 42\n",
        "# ── Helper: save per-tag F1 report to CSV ────────────────────────────────\n",
        "def save_per_tag_results(y_true, y_pred, tag_names, model_name):\n",
        "    \"\"\"Saves per-tag precision, recall, F1, support to CSV.\"\"\"\n",
        "    rows = []\n",
        "    for i, tag in enumerate(tag_names):\n",
        "        tp = int(((y_true[:, i] == 1) & (y_pred[:, i] == 1)).sum())\n",
        "        fp = int(((y_true[:, i] == 0) & (y_pred[:, i] == 1)).sum())\n",
        "        fn = int(((y_true[:, i] == 1) & (y_pred[:, i] == 0)).sum())\n",
        "        support = int(y_true[:, i].sum())\n",
        "        prec   = tp / (tp + fp) if (tp + fp) > 0 else 0.0\n",
        "        rec    = tp / (tp + fn) if (tp + fn) > 0 else 0.0\n",
        "        f1     = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0\n",
        "        rows.append({\n",
        "            'tag':       tag,\n",
        "            'precision': round(prec, 4),\n",
        "            'recall':    round(rec, 4),\n",
        "            'f1':        round(f1, 4),\n",
        "            'support':   support,\n",
        "            'model':     model_name\n",
        "        })\n",
        "    df_out = pd.DataFrame(rows).sort_values('f1', ascending=False)\n",
        "    path = f'saved_data/results/{model_name.lower().replace(\" \", \"_\")}_results2.csv'\n",
        "    df_out.to_csv(path, index=False)\n",
        "    print(f\"  Saved: {path}\")\n",
        "    return df_out\n",
        "\n",
        "\n",
        "# ── Helper: compute summary metrics ──────────────────────────────────────\n",
        "def get_summary(y_true, y_pred, model_name):\n",
        "    return {\n",
        "        'model':      model_name,\n",
        "        'macro_f1':   round(f1_score(y_true, y_pred, average='macro',    zero_division=0), 4),\n",
        "        'micro_f1':   round(f1_score(y_true, y_pred, average='micro',    zero_division=0), 4),\n",
        "        'weighted_f1':round(f1_score(y_true, y_pred, average='weighted', zero_division=0), 4),\n",
        "        'samples_f1': round(f1_score(y_true, y_pred, average='samples',  zero_division=0), 4),\n",
        "    }\n"
      ],
      "outputs": [],
      "execution_count": 32,
      "metadata": {
        "gather": {
          "logged": 1778475641302
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "from scipy.sparse import csr_matrix\n",
        "\n",
        "print(\"\\nTraining OvR LightGBM (TF-IDF + FastText)...\")\n",
        "\n",
        "# ✅ defensive conversion (even if already CSR)\n",
        "X_tr_combined = csr_matrix(X_tr_combined)\n",
        "X_te_combined = csr_matrix(X_te_combined)\n",
        "\n",
        "lgb_hybrid = OneVsRestClassifier(\n",
        "    lgb.LGBMClassifier(\n",
        "        objective= 'binary',\n",
        "        metric= 'binary_logloss',\n",
        "        n_estimators=300,\n",
        "        num_leaves=31,\n",
        "        feature_fraction=0.7,\n",
        "        bagging_fraction=0.8,\n",
        "        bagging_freq=5,\n",
        "        min_data_in_leaf=20,\n",
        "        lambda_l1=0.5,\n",
        "        lambda_l2=1.0,\n",
        "        max_depth=6,\n",
        "        learning_rate=0.05,#0.1\n",
        "        subsample=0.8,\n",
        "        colsample_bytree=0.8,\n",
        "        class_weight='balanced',\n",
        "        random_state=RANDOM_SEED,\n",
        "        n_jobs=-1,\n",
        "        verbose=-1\n",
        "    ),\n",
        "    n_jobs=1 \n",
        ")\n",
        "\n",
        "lgb_hybrid.fit(X_tr_combined, y_tr)\n",
        "lgb_preds_hybrid = lgb_hybrid.predict(X_te_combined)\n",
        "\n",
        "save_per_tag_results(\n",
        "    y_te, lgb_preds_hybrid, valid_tags,\n",
        "    \"lightgbm_tfidf_fasttext\"\n",
        ")\n",
        "\n",
        "summary_rows.append(\n",
        "    get_summary(y_te, lgb_preds_hybrid, \"OvR LightGBM (TF-IDF + FastText)\")\n",
        ")\n",
        "\n",
        "print(f\"  Hybrid Macro F1: {summary_rows[-1]['macro_f1']}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nTraining OvR LightGBM (TF-IDF + FastText)...\n  Saved: saved_data/results/lightgbm_tfidf_fasttext_results2.csv\n  Hybrid Macro F1: 0.5975\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 5 is present in all training examples.\n  warnings.warn(\n/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 46 is present in all training examples.\n  warnings.warn(\n/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 136 is present in all training examples.\n  warnings.warn(\n/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 144 is present in all training examples.\n  warnings.warn(\n"
        }
      ],
      "execution_count": 33,
      "metadata": {
        "gather": {
          "logged": 1778478673282
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "summary_rows.append(\n",
        "    get_summary(y_te, lgb_preds_hybrid, \"OvR LightGBM (TF-IDF + FastText)\")\n",
        ")\n",
        "\n",
        "print(f\"  Hybrid Macro F1: {summary_rows[-1]['macro_f1']}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "  Hybrid Macro F1: 0.5975\n"
        }
      ],
      "execution_count": 35,
      "metadata": {
        "gather": {
          "logged": 1778483472040
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"\\nTraining OvR LightGBM (TF-IDF baseline)...\")\n",
        "\n",
        "lgb_tfidf = OneVsRestClassifier(\n",
        "    lgb.LGBMClassifier(\n",
        "        n_estimators=300,\n",
        "        max_depth=6,\n",
        "        learning_rate=0.1,\n",
        "        subsample=0.8,\n",
        "        colsample_bytree=0.8,\n",
        "        class_weight='balanced',\n",
        "        random_state=RANDOM_SEED,\n",
        "        n_jobs=-1,\n",
        "        verbose=-1\n",
        "    ),\n",
        "    n_jobs=1  # ✅ important for stability\n",
        ")\n",
        "\n",
        "lgb_tfidf.fit(X_tr_tfidf, y_tr)\n",
        "lgb_preds_tfidf = lgb_tfidf.predict(X_te_tfidf)\n",
        "\n",
        "save_per_tag_results(\n",
        "    y_te, lgb_preds_tfidf, valid_tags,\n",
        "    \"lightgbm_tfidf\"\n",
        ")\n",
        "\n",
        "summary_rows.append(\n",
        "    get_summary(y_te, lgb_preds_tfidf, \"OvR LightGBM (TF-IDF)\")\n",
        ")\n",
        "\n",
        "print(f\"  TF-IDF Macro F1: {summary_rows[-1]['macro_f1']}\")\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nTraining OvR LightGBM (TF-IDF baseline)...\n  Saved: saved_data/results/lightgbm_tfidf_results2.csv\n  TF-IDF Macro F1: 0.5916\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "/anaconda/envs/azureml_py38/lib/python3.10/site-packages/sklearn/multiclass.py:87: UserWarning: Label not 5 is present in all training examples.\n  warnings.warn(\n"
        }
      ],
      "execution_count": 34,
      "metadata": {
        "gather": {
          "logged": 1778483471777
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "summary_rows.append(\n",
        "    get_summary(y_te, lgb_preds_tfidf, \"OvR LightGBM (TF-IDF)\")\n",
        ")\n",
        "\n",
        "print(f\"  TF-IDF Macro F1: {summary_rows[-1]['macro_f1']}\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "  TF-IDF Macro F1: 0.5916\n"
        }
      ],
      "execution_count": 36,
      "metadata": {
        "gather": {
          "logged": 1778483472427
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "### SAVINGS RESULTS \n",
        "saved_data/results/\n",
        "\n",
        "├── lightgbm_tfidf_results.csv\n",
        "\n",
        "├── lightgbm_tfidf_fasttext_results.csv\n",
        "\n",
        "├── complaint_predictions_lightgbm_tfidf.csv\n",
        "\n",
        "├── complaint_predictions_lightgbm_tfidf_fasttext.csv\n",
        "\n",
        "└── complaint_predictions_lightgbm_all.csv"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "DATA_DIR = Path(\"saved_data\")\n",
        "MODELS_DIR = Path(\"saved_models\")\n",
        "RESULTS_DIR = DATA_DIR / \"results\""
      ],
      "outputs": [],
      "execution_count": 26,
      "metadata": {
        "gather": {
          "logged": 1778497437346
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(MODELS_DIR.exists())\n",
        "print(MODELS_DIR.resolve())\n",
        "\n"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "True\n/mnt/batch/tasks/shared/LS_root/mounts/clusters/mlc-analytics-dev-cpu-ky/code/Users/Kriti.Yadav/clean_lab_approachkriti_modelrun_onevsrest1/saved_models\n"
        }
      ],
      "execution_count": 27,
      "metadata": {
        "gather": {
          "logged": 1778497439973
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(MODELS_DIR.mkdir(parents=True, exist_ok=True))"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "None\n"
        }
      ],
      "execution_count": 24,
      "metadata": {
        "gather": {
          "logged": 1778497362046
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"\\nPHASE 4: Train DistilBERT Model\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "# Settings\n",
        "# IMPROVED SETTINGS\n",
        "MODEL_NAME = 'distilbert-base-uncased'\n",
        "DEVICE = torch.device('cuda' if torch.cuda.is_available() else 'cpu')\n",
        "EPOCHS = 15              # ← Increased from 5\n",
        "BATCH_SIZE = 32          # ← Increased from 16  \n",
        "MAX_LEN = 512            # ← Increased from 256\n",
        "LR = 1e-5                # ← Reduced from 2e-5\n",
        "EARLY_STOP_PAT = 5       # ← Increased from 3\n",
        "\n",
        "print(f\"Device: {DEVICE}\")\n",
        "print(f\"Model: {MODEL_NAME}\")\n",
        "print(f\"Settings: Batch={BATCH_SIZE} | MaxLen={MAX_LEN} | LR={LR} | Epochs={EPOCHS}\")\n",
        "\n",
        "# Model architecture\n",
        "class ComplaintTagger(nn.Module):\n",
        "    def __init__(self, num_labels):\n",
        "        super().__init__()\n",
        "        self.bert = AutoModel.from_pretrained(MODEL_NAME)\n",
        "        self.dropout = nn.Dropout(0.3)\n",
        "        self.classifier = nn.Linear(self.bert.config.hidden_size, num_labels)\n",
        "    \n",
        "    def forward(self, input_ids, attention_mask):\n",
        "        out = self.bert(input_ids=input_ids, attention_mask=attention_mask)\n",
        "        pooled = self.dropout(out.last_hidden_state[:, 0, :])  # [CLS] token\n",
        "        return self.classifier(pooled)\n",
        "\n",
        "# Asymmetric Loss for imbalanced multi-label\n",
        "class AsymmetricLoss(nn.Module):\n",
        "    def __init__(self, gamma_neg=4, gamma_pos=1, clip=0.05):\n",
        "        super().__init__()\n",
        "        self.gn, self.gp, self.clip = gamma_neg, gamma_pos, clip\n",
        "    \n",
        "    def forward(self, logits, targets):\n",
        "        p = torch.sigmoid(logits)\n",
        "        pn = (1 - p + self.clip).clamp(max=1)\n",
        "        return (-(targets * torch.log(p.clamp(1e-8)) * (1-p)**self.gp +\n",
        "                (1-targets) * torch.log(pn.clamp(1e-8)) * p**self.gn)).mean()\n",
        "\n",
        "print(\"✓ Model classes defined\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "\nPHASE 4: Train DistilBERT Model\n======================================================================\nDevice: cpu\nModel: distilbert-base-uncased\nSettings: Batch=32 | MaxLen=512 | LR=1e-05 | Epochs=15\n✓ Model classes defined\n"
        }
      ],
      "execution_count": 41,
      "metadata": {
        "gather": {
          "logged": 1778508089777
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Dataset class\n",
        "from transformers import AutoTokenizer\n",
        "tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)\n",
        "\n",
        "class ComplaintDataset(Dataset):\n",
        "    def __init__(self, df_rows, labels):\n",
        "        self.df = df_rows.reset_index(drop=True)\n",
        "        self.labels = labels\n",
        "    \n",
        "    def __len__(self):\n",
        "        return len(self.df)\n",
        "    \n",
        "    def __getitem__(self, idx):\n",
        "        row = self.df.iloc[idx]\n",
        "        # Build text from available columns\n",
        "        parts = []\n",
        "        for label, col in [('Service', 'Service'),\n",
        "                           ('Complaint', 'summary'),\n",
        "                           ('Context', 'tier2_description_example_cleaned')]:\n",
        "            val = str(row.get(col, '')).strip()\n",
        "            if val and val.lower() not in ('nan', 'none', ''):\n",
        "                parts.append(f\"{label}: {val}\")\n",
        "        text = ' [SEP] '.join(parts)\n",
        "        \n",
        "        enc = tokenizer(text, max_length=MAX_LEN, padding='max_length',\n",
        "                      truncation=True, return_tensors='pt')\n",
        "        lbl = torch.tensor(self.labels[idx], dtype=torch.float32)\n",
        "        \n",
        "        return {\n",
        "            'input_ids': enc['input_ids'].squeeze(),\n",
        "            'attention_mask': enc['attention_mask'].squeeze(),\n",
        "            'labels': lbl\n",
        "        }\n",
        "\n",
        "# Create dataloaders\n",
        "train_dataset = ComplaintDataset(df_tr, y_tr)\n",
        "val_dataset = ComplaintDataset(df_val, y_val)\n",
        "test_dataset = ComplaintDataset(df_te, y_te)\n",
        "\n",
        "train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True)\n",
        "val_loader = DataLoader(val_dataset, batch_size=BATCH_SIZE)\n",
        "test_loader = DataLoader(test_dataset, batch_size=BATCH_SIZE)\n",
        "\n",
        "print(f\"✓ DataLoaders ready\")\n",
        "print(f\"  Train: {len(train_loader)} batches\")\n",
        "print(f\"  Val:   {len(val_loader)} batches\")\n",
        "print(f\"  Test:  {len(test_loader)} batches\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✓ DataLoaders ready\n  Train: 92 batches\n  Val:   11 batches\n  Test:  11 batches\n"
        }
      ],
      "execution_count": 42,
      "metadata": {
        "gather": {
          "logged": 1778508095321
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Training function\n",
        "def train_epoch(model, loader, criterion, optimizer, scheduler):\n",
        "    model.train()\n",
        "    total_loss = 0\n",
        "    for batch in tqdm(loader, desc=\"  Training\", leave=False):\n",
        "        optimizer.zero_grad()\n",
        "        loss = criterion(\n",
        "            model(batch['input_ids'].to(DEVICE), \n",
        "                 batch['attention_mask'].to(DEVICE)),\n",
        "            batch['labels'].to(DEVICE)\n",
        "        )\n",
        "        loss.backward()\n",
        "        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)\n",
        "        optimizer.step()\n",
        "        scheduler.step()\n",
        "        total_loss += loss.item()\n",
        "    return total_loss / len(loader)\n",
        "\n",
        "# Evaluation function\n",
        "def eval_epoch(model, loader):\n",
        "    model.eval()\n",
        "    probs_all, labels_all = [], []\n",
        "    with torch.no_grad():\n",
        "        for batch in tqdm(loader, desc=\"  Evaluating\", leave=False):\n",
        "            probs = torch.sigmoid(\n",
        "                model(batch['input_ids'].to(DEVICE),\n",
        "                     batch['attention_mask'].to(DEVICE))\n",
        "            ).cpu().numpy()\n",
        "            probs_all.append(probs)\n",
        "            labels_all.append(batch['labels'].numpy())\n",
        "    return np.vstack(probs_all), np.vstack(labels_all)\n",
        "\n",
        "print(\"✓ Training functions defined\")"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✓ Training functions defined\n"
        }
      ],
      "execution_count": 43,
      "metadata": {
        "gather": {
          "logged": 1778508096067
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "DATA_DIR = Path(\"saved_data\")\n",
        "MODELS_DIR = Path(\"saved_data\")\n",
        "RESULTS_DIR = DATA_DIR / \"results\"\n"
      ],
      "outputs": [
        {
          "output_type": "error",
          "ename": "NameError",
          "evalue": "name 'Path' is not defined",
          "traceback": [
            "\u001b[0;31m---------------------------------------------------------------------------\u001b[0m",
            "\u001b[0;31mNameError\u001b[0m                                 Traceback (most recent call last)",
            "Cell \u001b[0;32mIn[2], line 1\u001b[0m\n\u001b[0;32m----> 1\u001b[0m DATA_DIR \u001b[38;5;241m=\u001b[39m \u001b[43mPath\u001b[49m(\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124msaved_data\u001b[39m\u001b[38;5;124m\"\u001b[39m)\n\u001b[1;32m      2\u001b[0m MODELS_DIR \u001b[38;5;241m=\u001b[39m Path(\u001b[38;5;124m\"\u001b[39m\u001b[38;5;124msaved_data\u001b[39m\u001b[38;5;124m\"\u001b[39m)\n\u001b[1;32m      3\u001b[0m RESULTS_DIR \u001b[38;5;241m=\u001b[39m DATA_DIR \u001b[38;5;241m/\u001b[39m \u001b[38;5;124m\"\u001b[39m\u001b[38;5;124mresults\u001b[39m\u001b[38;5;124m\"\u001b[39m\n",
            "\u001b[0;31mNameError\u001b[0m: name 'Path' is not defined"
          ]
        }
      ],
      "execution_count": 2,
      "metadata": {
        "gather": {
          "logged": 1778559543198
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "MODELS_DIR.mkdir(parents=True, exist_ok=True)"
      ],
      "outputs": [],
      "execution_count": 45,
      "metadata": {
        "gather": {
          "logged": 1778508099132
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Check if model already exists\n",
        "distilbert_model_path = MODELS_DIR / 'distilbert_best_model2.pth'\n",
        "\n",
        "if distilbert_model_path.exists():\n",
        "    print(f\"✓ Found existing model: {distilbert_model_path}\")\n",
        "    print(\"  Loading saved model...\")\n",
        "    model = ComplaintTagger(NUM_LABELS).to(DEVICE)\n",
        "    model.load_state_dict(torch.load(distilbert_model_path, map_location=DEVICE))\n",
        "    print(\"  ✓ Model loaded. Skipping training.\")\n",
        "    print(\"  (Delete the file to retrain)\")\n",
        "    \n",
        "else:\n",
        "    print(\"✗ Model not found. Training new DistilBERT model...\")\n",
        "    \n",
        "    # Initialize model, loss, optimizer\n",
        "    model = ComplaintTagger(NUM_LABELS).to(DEVICE)\n",
        "    criterion = AsymmetricLoss(gamma_neg=2, gamma_pos=1) \n",
        "    optimizer = AdamW(model.parameters(), lr=LR, weight_decay=0.01)\n",
        "    \n",
        "    from transformers import get_linear_schedule_with_warmup\n",
        "    total_steps = len(train_loader) * EPOCHS\n",
        "    scheduler = get_linear_schedule_with_warmup(\n",
        "        optimizer,\n",
        "        num_warmup_steps=max(1, total_steps // 10),\n",
        "        num_training_steps=total_steps\n",
        "    )\n",
        "    \n",
        "    total_params = sum(p.numel() for p in model.parameters())\n",
        "    print(f\"  Model parameters: {total_params:,}\")\n",
        "    \n",
        "    # Training loop\n",
        "    print(f\"\\n  Training for {EPOCHS} epochs...\")\n",
        "    best_f1 = 0.0\n",
        "    patience_counter = 0\n",
        "    history = []\n",
        "    \n",
        "    for epoch in range(EPOCHS):\n",
        "        print(f\"\\n  Epoch {epoch+1}/{EPOCHS}\")\n",
        "        \n",
        "        # Train\n",
        "        train_loss = train_epoch(model, train_loader, criterion, optimizer, scheduler)\n",
        "        \n",
        "        # Validate\n",
        "        val_probs, val_labels = eval_epoch(model, val_loader)\n",
        "        val_preds = (val_probs >= 0.5).astype(int)\n",
        "        val_true = (val_labels >= 0.5).astype(int)\n",
        "        \n",
        "        macro_f1 = f1_score(val_true, val_preds, average='macro', zero_division=0)\n",
        "        micro_f1 = f1_score(val_true, val_preds, average='micro', zero_division=0)\n",
        "        \n",
        "        print(f\"    Train Loss: {train_loss:.4f}\")\n",
        "        print(f\"    Val Macro F1: {macro_f1:.4f} | Val Micro F1: {micro_f1:.4f}\")\n",
        "        \n",
        "        history.append({\n",
        "            'epoch': epoch + 1,\n",
        "            'train_loss': round(train_loss, 4),\n",
        "            'val_macro_f1': round(macro_f1, 4),\n",
        "            'val_micro_f1': round(micro_f1, 4)\n",
        "        })\n",
        "        \n",
        "        # Save epoch checkpoint\n",
        "        epoch_path = MODELS_DIR / f'distilbert2_epoch_{epoch+1}.pth'\n",
        "        torch.save({\n",
        "            'epoch': epoch + 1,\n",
        "            'model_state': model.state_dict(),\n",
        "            'optimizer_state': optimizer.state_dict(),\n",
        "            'macro_f1': macro_f1\n",
        "        }, epoch_path)\n",
        "        \n",
        "        # Save best model\n",
        "        if macro_f1 > best_f1:\n",
        "            best_f1 = macro_f1\n",
        "            torch.save(model.state_dict(), distilbert_model_path)\n",
        "            print(f\"    ✓ Best model saved (Macro F1: {best_f1:.4f})\")\n",
        "            patience_counter = 0\n",
        "        else:\n",
        "            patience_counter += 1\n",
        "            if patience_counter >= EARLY_STOP_PAT:\n",
        "                print(f\"    Early stopping at epoch {epoch+1}\")\n",
        "                break\n",
        "    \n",
        "    # Save training history\n",
        "    pd.DataFrame(history).to_csv(RESULTS_DIR / 'distilbert_training_history2.csv', index=False)\n",
        "    print(f\"\\n  ✓ Training complete! Best Val Macro F1: {best_f1:.4f}\")\n",
        "    print(f\"  ✓ Model saved to {distilbert_model_path}\")\n",
        "\n",
        "print(\"\\n\" + \"=\" * 70)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "✗ Model not found. Training new DistilBERT model...\n  Model parameters: 66,431,321\n\n  Training for 15 epochs...\n\n  Epoch 1/15\n    Train Loss: 0.1188\n    Val Macro F1: 0.0000 | Val Micro F1: 0.0000\n    Train Loss: 0.0412\n    Val Macro F1: 0.0000 | Val Micro F1: 0.0000\n"
        },
        {
          "output_type": "stream",
          "name": "stderr",
          "text": "  Training:  39%|███▉      | 36/92 [37:45<59:07, 63.35s/it]  \r  Training:  73%|███████▎  | 67/92 [57:51<15:46, 37.86s/it]"
        }
      ],
      "execution_count": 49,
      "metadata": {
        "gather": {
          "logged": 1778541503044
        }
      }
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "def save_per_tag_results(y_true, y_pred, tag_names, model_name):\n",
        "    \"\"\"Save per-tag precision, recall, F1, support to CSV.\"\"\"\n",
        "    rows = []\n",
        "    for i, tag in enumerate(tag_names):\n",
        "        tp = int(((y_true[:, i] == 1) & (y_pred[:, i] == 1)).sum())\n",
        "        fp = int(((y_true[:, i] == 0) & (y_pred[:, i] == 1)).sum())\n",
        "        fn = int(((y_true[:, i] == 1) & (y_pred[:, i] == 0)).sum())\n",
        "        support = int(y_true[:, i].sum())\n",
        "        prec = tp / (tp + fp) if (tp + fp) > 0 else 0.0\n",
        "        rec = tp / (tp + fn) if (tp + fn) > 0 else 0.0\n",
        "        f1 = 2 * prec * rec / (prec + rec) if (prec + rec) > 0 else 0.0\n",
        "        rows.append({\n",
        "            'tag': tag,\n",
        "            'precision': round(prec, 4),\n",
        "            'recall': round(rec, 4),\n",
        "            'f1': round(f1, 4),\n",
        "            'support': support,\n",
        "            'model': model_name\n",
        "        })\n",
        "    df_out = pd.DataFrame(rows).sort_values('f1', ascending=False)\n",
        "    path = RESULTS_DIR / f\"{model_name.lower().replace(' ', '_')}_results.csv\"\n",
        "    df_out.to_csv(path, index=False)\n",
        "    print(f\"  Saved: {path}\")\n",
        "    return df_out"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1778541503076
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "print(\"\\nDistilBERT Test Evaluation\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "# Load best model\n",
        "model.load_state_dict(torch.load(distilbert_model_path, map_location=DEVICE))\n",
        "\n",
        "# Evaluate on test set\n",
        "test_probs, test_labels = eval_epoch(model, test_loader)\n",
        "test_preds = (test_probs >= 0.5).astype(int)\n",
        "test_true = (test_labels >= 0.5).astype(int)\n",
        "\n",
        "test_macro_f1 = f1_score(test_true, test_preds, average='macro', zero_division=0)\n",
        "test_micro_f1 = f1_score(test_true, test_preds, average='micro', zero_division=0)\n",
        "test_weighted_f1 = f1_score(test_true, test_preds, average='weighted', zero_division=0)\n",
        "\n",
        "print(f\"Test Results:\")\n",
        "print(f\"  Macro F1:    {test_macro_f1:.4f}\")\n",
        "print(f\"  Micro F1:    {test_micro_f1:.4f}\")\n",
        "print(f\"  Weighted F1: {test_weighted_f1:.4f}\")\n"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1778541503094
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "\n",
        "# # Save per-tag results\n",
        "# save_per_tag_results(test_true, test_preds, valid_tags, \"distilbert\")\n",
        "\n",
        "# # Save test predictions\n",
        "# test_pred_df = df_te[['case_reference']].copy()\n",
        "# for i, tag in enumerate(valid_tags):\n",
        "#     test_pred_df[f'pred_{tag}'] = test_preds[:, i]\n",
        "#     test_pred_df[f'prob_{tag}'] = test_probs[:, i].round(3)\n",
        "# test_pred_df.to_csv(RESULTS_DIR / 'distilbert_test_predictions.csv', index=False)\n",
        "\n",
        "# print(f\"\\n✓ Saved results:\")\n",
        "# print(f\"  - {RESULTS_DIR / 'distilbert_results.csv'}\")\n",
        "# print(f\"  - {RESULTS_DIR / 'distilbert_test_predictions.csv'}\")\n",
        "# print(\"=\" * 70)\n",
        "\n",
        "# # Store for comparison\n",
        "# distilbert_preds = test_preds\n",
        "# distilbert_probs = test_probs"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1778541503108
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "print(\"\\n\" + \"=\" * 70)\n",
        "print(\"DISTILBERT TOP-K PREDICTIONS ANALYSIS\")\n",
        "print(\"=\" * 70)\n",
        "\n",
        "def generate_topk_predictions(probs, y_true, df_test, valid_tags, model_name, k=10):\n",
        "    \"\"\"\n",
        "    Generate top-k predictions for each test case\n",
        "    \n",
        "    Parameters:\n",
        "    - probs: probability matrix (n_samples, n_tags)\n",
        "    - y_true: true label matrix (n_samples, n_tags)\n",
        "    - df_test: test dataframe with case_reference\n",
        "    - valid_tags: list of tag names\n",
        "    - model_name: name of the model\n",
        "    - k: number of top predictions to return\n",
        "    \n",
        "    Returns:\n",
        "    - DataFrame with top-k predictions and comparisons\n",
        "    \"\"\"\n",
        "    rows = []\n",
        "    \n",
        "    for i in range(len(df_test)):\n",
        "        # Get actual tags\n",
        "        actual_indices = np.where(y_true[i] == 1)[0]\n",
        "        actual_tags = [valid_tags[j] for j in actual_indices]\n",
        "        \n",
        "        # Get top-k predicted tags\n",
        "        top_indices = probs[i].argsort()[-k:][::-1]  # Top k indices\n",
        "        top_tags = [valid_tags[j] for j in top_indices]\n",
        "        top_probs = [probs[i][j] for j in top_indices]\n",
        "        \n",
        "        # Calculate matches\n",
        "        actual_set = set(actual_tags)\n",
        "        predicted_set = set(top_tags)\n",
        "        matches = actual_set & predicted_set\n",
        "        missed = actual_set - predicted_set\n",
        "        false_positives = predicted_set - actual_set\n",
        "        \n",
        "        # Calculate precision/recall for this case\n",
        "        if len(predicted_set) > 0:\n",
        "            precision = len(matches) / len(predicted_set)\n",
        "        else:\n",
        "            precision = 0.0\n",
        "        \n",
        "        if len(actual_set) > 0:\n",
        "            recall = len(matches) / len(actual_set)\n",
        "        else:\n",
        "            recall = 1.0 if len(predicted_set) == 0 else 0.0\n",
        "        \n",
        "        if precision + recall > 0:\n",
        "            f1 = 2 * precision * recall / (precision + recall)\n",
        "        else:\n",
        "            f1 = 0.0\n",
        "        \n",
        "        rows.append({\n",
        "            'case_reference': df_test.iloc[i].get('case_reference', f'case_{i}'),\n",
        "            # NEW (keeps full text):\n",
        "            'summary': df_test.iloc[i].get('summary', ''),\n",
        "            'actual_tags': ', '.join(sorted(actual_tags)),\n",
        "            'num_actual': len(actual_tags),\n",
        "            f'top_{k}_predicted': ', '.join(top_tags),\n",
        "            f'top_{k}_probabilities': ', '.join([f'{p:.3f}' for p in top_probs]),\n",
        "            'matched_tags': ', '.join(sorted(matches)) if matches else 'NONE',\n",
        "            'missed_tags': ', '.join(sorted(missed)) if missed else 'NONE',\n",
        "            'false_alarm_tags': ', '.join(sorted(false_positives)) if false_positives else 'NONE',\n",
        "            'num_matches': len(matches),\n",
        "            'precision': round(precision, 3),\n",
        "            'recall': round(recall, 3),\n",
        "            'f1': round(f1, 3),\n",
        "            'is_perfect_match': len(matches) == len(actual_set) and len(false_positives) == 0,\n",
        "            'model': model_name\n",
        "        })\n",
        "    \n",
        "    return pd.DataFrame(rows)\n",
        "\n",
        "# Generate top-10 predictions for DistilBERT\n",
        "print(\"\\nGenerating top-10 predictions for DistilBERT...\")\n",
        "\n",
        "distilbert_topk = generate_topk_predictions(\n",
        "    test_probs,      # From Cell 5 DistilBERT evaluation\n",
        "    y_te,            # True labels\n",
        "    df_te,           # Test dataframe\n",
        "    valid_tags,      # Tag names\n",
        "    \"DistilBERT\",\n",
        "    k=10\n",
        ")\n",
        "\n",
        "# Save results\n",
        "distilbert_topk.to_csv(RESULTS_DIR / 'distilbert_top10_predictions.csv', index=False)\n",
        "print(f\"✓ Saved: {RESULTS_DIR / 'distilbert_top10_predictions.csv'}\")\n",
        "\n",
        "# Show sample results\n",
        "print(f\"\\nSample results (first 5 cases):\")\n",
        "print(distilbert_topk[['case_reference', 'num_actual', 'num_matches', \n",
        "                       'precision', 'recall', 'f1', 'is_perfect_match']].head().to_string(index=False))\n",
        "\n",
        "# Quick statistics\n",
        "perfect_count = distilbert_topk['is_perfect_match'].sum()\n",
        "perfect_pct = (perfect_count / len(distilbert_topk)) * 100\n",
        "avg_f1 = distilbert_topk['f1'].mean()\n",
        "avg_precision = distilbert_topk['precision'].mean()\n",
        "avg_recall = distilbert_topk['recall'].mean()\n",
        "\n",
        "print(f\"\\nOverall Statistics:\")\n",
        "print(f\"  Perfect Matches: {perfect_count}/{len(distilbert_topk)} ({perfect_pct:.1f}%)\")\n",
        "print(f\"  Average F1:      {avg_f1:.4f}\")\n",
        "print(f\"  Average Precision: {avg_precision:.4f}\")\n",
        "print(f\"  Average Recall:    {avg_recall:.4f}\")\n",
        "\n",
        "print(\"\\n\" + \"=\" * 70)"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {
        "gather": {
          "logged": 1778541503124
        }
      }
    },
    {
      "cell_type": "markdown",
      "source": [
        "checking why the results are so bad with distilbert"
      ],
      "metadata": {
        "nteract": {
          "transient": {
            "deleting": false
          }
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Add after model initialization in Cell 1:\n",
        "model = ComplaintTagger(NUM_LABELS).to(DEVICE)\n",
        "\n",
        "# Verify layers are trainable\n",
        "print(f\"Total parameters: {sum(p.numel() for p in model.parameters()):,}\")\n",
        "print(f\"Trainable parameters: {sum(p.numel() for p in model.parameters() if p.requires_grad):,}\")\n",
        "# These two numbers should be equal"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Total parameters: 66,431,321\nTrainable parameters: 66,431,321\n"
        }
      ],
      "execution_count": 40,
      "metadata": {
        "gather": {
          "logged": 1778507954920
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "import numpy as np\n",
        "import pandas as pd\n",
        "\n",
        "def build_topk_summary(\n",
        "    probs,\n",
        "    y_true,\n",
        "    df_te,\n",
        "    valid_tags,\n",
        "    per_tag_metrics_path,\n",
        "    model_name,\n",
        "    k=5,\n",
        "    save_path=None\n",
        "):\n",
        "    \"\"\"\n",
        "    probs: np.ndarray (n_samples, n_tags)\n",
        "    y_true: np.ndarray (n_samples, n_tags)\n",
        "    \"\"\"\n",
        "\n",
        "    # Load per‑tag metrics (precision/recall/F1)\n",
        "    per_tag_df = pd.read_csv(per_tag_metrics_path)\n",
        "    per_tag_metrics = (\n",
        "        per_tag_df\n",
        "        .set_index(\"tag\")[[\"precision\", \"recall\", \"f1\"]]\n",
        "        .to_dict(orient=\"index\")\n",
        "    )\n",
        "\n",
        "    rows = []\n",
        "\n",
        "    for i in range(y_true.shape[0]):\n",
        "        # Actual tags for this complaint\n",
        "        actual_tags = [\n",
        "            valid_tags[j] for j in np.where(y_true[i] == 1)[0]\n",
        "        ]\n",
        "\n",
        "        p = probs[i]\n",
        "        topk_idx = p.argsort()[-k:][::-1]\n",
        "\n",
        "        topk_tags = [valid_tags[j] for j in topk_idx]\n",
        "        topk_probs = [p[j] for j in topk_idx]\n",
        "\n",
        "        topk_prec = []\n",
        "        topk_rec  = []\n",
        "        topk_f1   = []\n",
        "\n",
        "        for tag in topk_tags:\n",
        "            m = per_tag_metrics.get(tag, {\"precision\":0,\"recall\":0,\"f1\":0})\n",
        "            topk_prec.append(f\"{m['precision']:.3f}\")\n",
        "            topk_rec.append(f\"{m['recall']:.3f}\")\n",
        "            topk_f1.append(f\"{m['f1']:.3f}\")\n",
        "\n",
        "        rows.append({\n",
        "            \"case_reference\": df_te.iloc[i][\"case_reference\"],\n",
        "            \"actual_tier_2\": \", \".join(actual_tags),\n",
        "            \"top5_predicted_tier_2\": \", \".join(topk_tags),\n",
        "            \"top5_confidence\": \", \".join(f\"{x:.3f}\" for x in topk_probs),\n",
        "            \"top5_precision\": \", \".join(topk_prec),\n",
        "            \"top5_recall\": \", \".join(topk_rec),\n",
        "            \"top5_f1\": \", \".join(topk_f1),\n",
        "            \"model\": model_name\n",
        "        })\n",
        "\n",
        "    out_df = pd.DataFrame(rows)\n",
        "\n",
        "    if save_path:\n",
        "        out_df.to_csv(save_path, index=False)\n",
        "        print(f\"✅ Saved: {save_path}\")\n",
        "\n",
        "    return out_df"
      ],
      "outputs": [],
      "execution_count": 13,
      "metadata": {
        "gather": {
          "logged": 1778475071484
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "# Probabilities\n",
        "lgb_tfidf_probs = lgb_tfidf.predict_proba(X_te_tfidf)\n",
        "\n",
        "tfidf_summary_df = build_topk_summary(\n",
        "    probs=lgb_tfidf_probs,\n",
        "    y_true=y_te,\n",
        "    df_te=df_te,\n",
        "    valid_tags=valid_tags,\n",
        "    per_tag_metrics_path=\"saved_data/results/lightgbm_tfidf_results.csv\",\n",
        "    model_name=\"LightGBM_TFIDF\",\n",
        "    save_path=\"saved_data/results/complaint_predictions_lightgbm_tfidf.csv\"\n",
        ")\n",
        "\n",
        "display(tfidf_summary_df.head(10))"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "# Probabilities\n",
        "lgb_hybrid_probs = lgb_hybrid.predict_proba(X_te_combined)\n",
        "\n",
        "hybrid_summary_df = build_topk_summary(\n",
        "    probs=lgb_hybrid_probs,\n",
        "    y_true=y_te,\n",
        "    df_te=df_te,\n",
        "    valid_tags=valid_tags,\n",
        "    per_tag_metrics_path=\"saved_data/results/lightgbm_tfidf_fasttext_results.csv\",\n",
        "    model_name=\"LightGBM_TFIDF_FastText\",\n",
        "    save_path=\"saved_data/results/complaint_predictions_lightgbm_tfidf_fasttext.csv\"\n",
        ")\n",
        "\n",
        "display(hybrid_summary_df.head(10))"
      ],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    },
    {
      "cell_type": "code",
      "source": [
        "import pandas as pd\n",
        "import numpy as np\n",
        "from sklearn.metrics import f1_score, accuracy_score\n",
        "\n",
        "# Load predictions CSV\n",
        "pred_df = pd.read_csv(\n",
        "    \"saved_data/results/complaint_predictions_lightgbm_tfidf_fasttext.csv\"\n",
        ")\n",
        "\n",
        "# Load ground-truth labels\n",
        "y_true = np.load(\"saved_data/y_te_cleaned.npy\")\n",
        "\n",
        "# Infer tags from column names\n",
        "pred_cols = [c for c in pred_df.columns if c.startswith(\"pred_\")]\n",
        "valid_tags = [c.replace(\"pred_\", \"\") for c in pred_cols]\n",
        "\n",
        "# Extract predictions matrix\n",
        "y_pred = pred_df[pred_cols].values.astype(int)\n",
        "\n",
        "print(\"Shapes:\")\n",
        "print(\"y_true:\", y_true.shape)\n",
        "print(\"y_pred:\", y_pred.shape)"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "Shapes:\ny_true: (341, 89)\ny_pred: (341, 0)\n"
        }
      ],
      "execution_count": 1,
      "metadata": {
        "gather": {
          "logged": 1778236060041
        }
      }
    },
    {
      "cell_type": "code",
      "source": [
        "pred_df = pd.read_csv(\"saved_data/results/complaint_predictions_lightgbm_tfidf_fasttext.csv\")\n",
        "print(pred_df.columns.tolist())"
      ],
      "outputs": [
        {
          "output_type": "stream",
          "name": "stdout",
          "text": "['case_reference', 'actual_tier_2', 'top5_predicted_tier_2', 'top5_confidence', 'top5_precision', 'top5_recall', 'top5_f1', 'model']\n"
        }
      ],
      "execution_count": 4,
      "metadata": {
        "gather": {
          "logged": 1778236688060
        }
      }
    },
    {
      "cell_type": "code",
      "source": [],
      "outputs": [],
      "execution_count": null,
      "metadata": {}
    }
  ],
  "metadata": {
    "kernelspec": {
      "name": "python38-azureml",
      "language": "python",
      "display_name": "Python 3.10 - AzureML"
    },
    "language_info": {
      "name": "python",
      "version": "3.10.11",
      "mimetype": "text/x-python",
      "codemirror_mode": {
        "name": "ipython",
        "version": 3
      },
      "pygments_lexer": "ipython3",
      "nbconvert_exporter": "python",
      "file_extension": ".py"
    },
    "microsoft": {
      "ms_spell_check": {
        "ms_spell_check_language": "en"
      },
      "host": {
        "AzureML": {
          "notebookHasBeenCompleted": true
        }
      }
    },
    "kernel_info": {
      "name": "python38-azureml"
    },
    "nteract": {
      "version": "nteract-front-end@1.0.0"
    }
  },
  "nbformat": 4,
  "nbformat_minor": 2
}
