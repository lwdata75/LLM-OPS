"""
Quick Start Guide - Nutrition Assistant Pipeline
================================================

Your pipeline is now running on Vertex AI! 🚀

Pipeline Status: RUNNING ⏳

View Progress:
https://console.cloud.google.com/vertex-ai/pipelines/runs/nutrition-assistant-training-pipeline-20251021134705?project=aerobic-polygon-460910-v9

What's Happening Now:
--------------------

Step 1: Data Transformation (Running/Completed)
   - Converting 2,395 food items to conversational format
   - Splitting into train (80%) and test (20%) sets
   - Saving to GCS
   - Duration: ~5-10 minutes

Step 2: Fine-Tuning (Pending/Running)
   - Loading Phi-3-mini-4k-instruct model
   - Applying LoRA adapters
   - Training with GPU (NVIDIA T4)
   - Duration: ~45-90 minutes
   ⚠️ This is the longest step!

Step 3: Inference (Pending)
   - Loading fine-tuned model
   - Generating predictions on 100 test samples
   - Duration: ~10-15 minutes

Step 4: Evaluation (Pending)
   - Computing RAGAS metrics (Rouge, BLEU)
   - Generating evaluation reports
   - Duration: ~5 minutes

Total Expected Time: ~1.5 - 2 hours


Monitor Pipeline:
----------------

1. Check status in terminal:
   python scripts/check_pipeline_status.py

2. View in GCP Console:
   - Pipeline visualization with DAG
   - Real-time logs for each step
   - Resource utilization metrics

3. Check artifacts in GCS:
   gsutil ls gs://llmops_101_europ/pipeline_root/


After Pipeline Completes:
------------------------

✅ Your fine-tuned model will be saved in GCS
✅ Predictions CSV will be available
✅ Evaluation metrics will be logged
✅ TensorBoard logs for training curves

Access Results:
--------------

1. Fine-tuned model:
   gs://llmops_101_europ/pipeline_root/<job-id>/fine_tuned_model/

2. Predictions:
   gs://llmops_101_europ/pipeline_root/<job-id>/predictions/

3. Evaluation results:
   gs://llmops_101_europ/pipeline_root/<job-id>/evaluation_results/


Troubleshooting:
---------------

If pipeline fails:

1. Check logs in GCP Console (click on failed step)
2. Common issues:
   - GPU quota not approved → Request T4 quota increase
   - Out of memory → Reduce batch size in constants.py
   - Timeout → Increase max_steps or reduce epochs

3. Re-run pipeline:
   python scripts/pipeline_runner.py


Cost Estimation:
---------------

Approximate costs for this pipeline:
- Data transformation: < $0.10
- Fine-tuning (T4 GPU ~1.5 hrs): ~$0.50 - $1.00
- Inference (T4 GPU ~15 min): ~$0.10
- Evaluation: < $0.05
- Storage: < $0.01

Total: ~$1-2 per pipeline run


Next Steps:
----------

While waiting for the pipeline:

1. ☕ Take a break! Fine-tuning takes time.

2. 📊 Explore the GCP Console:
   - Watch the pipeline DAG visualization
   - Check resource utilization
   - View real-time logs

3. 📖 Review the code:
   - src/pipeline_components/ - Individual components
   - src/pipelines/ - Pipeline orchestration
   - src/constants.py - Configuration

4. 🔧 Plan improvements:
   - Experiment with hyperparameters
   - Add more evaluation metrics
   - Try different LoRA configurations


Questions?
---------

- Pipeline stuck? Check GPU quota
- Need to cancel? Use GCP Console "Cancel" button
- Want to re-run? Just run pipeline_runner.py again


Happy Training! 🎉
"""

if __name__ == "__main__":
    print(__doc__)
