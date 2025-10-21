# Pipeline Fix Summary - October 21, 2025

## 🔍 Issue Identified

The first pipeline run **FAILED** with the following error:

```
ValueError: text input must be of type `str` (single example), `List[str]` (batch or single pretokenized example) or `List[List[str]]` (batch of pretokenized examples).
```

### Root Cause

The **SFTTrainer** expected text strings for training, but we were passing a list of message dictionaries in the format:

```python
{
    "messages": [
        {"role": "user", "content": "What are the nutritional values for olive oil?"},
        {"role": "assistant", "content": "olive oil contains: Calories: 119 kcal, Fat: 13.5g"}
    ]
}
```

The trainer couldn't process this dictionary format and needed plain text strings instead.

## ✅ Fixes Applied

### 1. Data Transformation Component
**File**: `src/pipeline_components/data_transformation_component.py`

**Changed from:**
```python
dataset = Dataset.from_dict({"messages": [c["messages"] for c in conversations]})
```

**Changed to:**
```python
dataset = Dataset.from_dict({
    "messages": [c["messages"] for c in conversations],  # Keep for inference
    "text": [f"<|user|>\n{c['messages'][0]['content']}<|end|>\n<|assistant|>\n{c['messages'][1]['content']}<|end|>" for c in conversations]  # Add formatted text
})
```

Now the dataset includes both:
- `messages`: Original message format (for inference component)
- `text`: Formatted text strings with proper tokens (for SFTTrainer)

### 2. Fine-Tuning Component
**File**: `src/pipeline_components/fine_tuning_component.py`

**Multiple fixes:**

#### Fix A: Removed incompatible SFTConfig import
```python
# OLD
from trl import SFTTrainer, SFTConfig

# NEW
from trl import SFTTrainer
```

#### Fix B: Changed to TrainingArguments
```python
# OLD
sft_config = SFTConfig(...)

# NEW
training_args = TrainingArguments(...)
```

#### Fix C: Updated SFTTrainer to use text field
```python
# OLD
trainer = SFTTrainer(
    ...
    dataset_text_field="messages",  # Wrong - this is a dict
)

# NEW
trainer = SFTTrainer(
    ...
    dataset_text_field="text",  # Correct - this is a string
)
```

#### Fix D: Updated package versions for compatibility
```python
# OLD
base_image="pytorch/pytorch:2.5.0-cuda12.4-cudnn9-devel"
packages_to_install=[
    "transformers==4.46.0",  # Yanked version
    "datasets==3.1.0",
    "accelerate==1.1.1",
    "bitsandbytes==0.44.1",
    "trl==0.11.4",
]

# NEW
base_image="pytorch/pytorch:2.4.0-cuda12.1-cudnn9-devel"
packages_to_install=[
    "transformers==4.46.0",
    "datasets==3.0.0",  # More stable
    "accelerate==1.0.1",  # More stable
    "bitsandbytes==0.43.3",  # More stable
    "trl==0.10.1",  # Compatible with TrainingArguments
    "scipy",  # Added missing dependency
]
```

### 3. Inference Component
**File**: `src/pipeline_components/inference_component.py`

**Updated package versions to match fine-tuning component** for consistency.

## 📊 New Pipeline Status

**Pipeline ID**: `nutrition-assistant-training-pipeline-20251021140422`  
**Status**: ✅ RUNNING  
**Submitted**: October 21, 2025 14:04:22 UTC

**View in Console**:
https://console.cloud.google.com/vertex-ai/pipelines/runs/nutrition-assistant-training-pipeline-20251021140422?project=aerobic-polygon-460910-v9

## 🎯 Expected Behavior

The fixed pipeline should now:

1. ✅ **Data Transformation** (5-10 min)
   - Convert CSV to both message and text formats
   - Split 80/20 train/test

2. ✅ **Fine-Tuning** (45-90 min)
   - Load Phi-3 model
   - Apply LoRA adapters
   - Train on formatted text strings
   - Save model to GCS

3. ✅ **Inference** (10-15 min)
   - Use messages format for generation
   - Generate 100 predictions

4. ✅ **Evaluation** (5 min)
   - Compute Rouge and BLEU scores
   - Save metrics

## 🔧 Key Learnings

### 1. SFTTrainer Text Format Requirements
- **SFTTrainer** requires `dataset_text_field` to point to a column containing **strings**, not complex objects
- Proper format: `"<|user|>\nQuestion<|end|>\n<|assistant|>\nAnswer<|end|>"`

### 2. Package Version Compatibility
- Always use stable, non-yanked versions
- `trl==0.10.1` works better with `TrainingArguments`
- `trl==0.11.4` introduced `SFTConfig` which had issues

### 3. Dual Format Strategy
- Keep `messages` format for inference (easier to work with)
- Add `text` format for training (required by SFTTrainer)
- Both can coexist in the same dataset

## ✅ Verification Steps

To verify the fix is working:

```bash
# Check pipeline status
python scripts/check_pipeline_status.py

# View logs for new pipeline
python scripts/get_pipeline_logs.py
```

Expected output:
- Data transformation completes successfully
- Fine-tuning starts and runs without ValueError
- Training progresses through epochs
- Model saves to GCS

## 📝 Monitoring

Monitor the pipeline at:
https://console.cloud.google.com/vertex-ai/pipelines?project=aerobic-polygon-460910-v9

Look for:
- ✅ Green checkmarks on completed steps
- 📊 Training metrics in TensorBoard
- 📁 Artifacts in GCS bucket

---

**Fixed By**: AI Assistant  
**Date**: October 21, 2025  
**Time**: 14:04 UTC  
**Status**: Pipeline resubmitted and running
