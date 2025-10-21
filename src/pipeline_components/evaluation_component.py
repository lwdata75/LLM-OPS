"""
Evaluation component using RAGAS metrics.
"""
from kfp.dsl import component, Input, Output, Dataset, Metrics
from typing import Dict, List


@component(
    base_image="cicirello/pyaction:3.11",
    packages_to_install=[
        "pandas==2.2.3",
        "ragas==0.2.6",
        "datasets==3.1.0",
        "gcsfs==2024.9.0",
        "google-cloud-storage==2.18.2",
        "nltk==3.9.1",
        "rouge-score==0.1.2",
    ],
)
def evaluation_component(
    predictions: Input[Dataset],
    evaluation_results: Output[Dataset],
    aggregated_metrics: Output[Metrics],
) -> Dict[str, float]:
    """Evaluate predictions using RAGAS metrics.
    
    Args:
        predictions: CSV file with predictions
        evaluation_results: Output path for per-sample evaluation results
        aggregated_metrics: Output path for aggregated metrics
        
    Returns:
        Dictionary with aggregated metric scores
    """
    import pandas as pd
    import json
    import logging
    from ragas.metrics import RougeScore, BleuScore
    from ragas import SingleTurnSample
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    # Load predictions
    logger.info(f"Loading predictions from {predictions.path}")
    df = pd.read_csv(predictions.path)
    logger.info(f"Loaded {len(df)} predictions")
    
    # Define metrics
    metrics_list = [
        RougeScore(),
        BleuScore(),
    ]
    
    logger.info(f"Computing metrics: {[m.__class__.__name__ for m in metrics_list]}")
    
    # Compute per-sample metrics
    per_sample_results = []
    
    for idx, row in df.iterrows():
        user_input = str(row["user_input"])
        response = str(row["extracted_response"])
        reference = str(row["reference"])
        
        # Create sample
        sample = SingleTurnSample(
            user_input=user_input,
            response=response,
            reference=reference,
        )
        
        # Compute metrics for this sample
        sample_metrics = {
            "user_input": user_input,
            "reference": reference,
            "response": response,
        }
        
        for metric in metrics_list:
            try:
                score = metric.single_turn_score(sample)
                sample_metrics[metric.__class__.__name__] = float(score)
            except Exception as e:
                logger.warning(f"Error computing {metric.__class__.__name__} for sample {idx}: {e}")
                sample_metrics[metric.__class__.__name__] = 0.0
        
        per_sample_results.append(sample_metrics)
        
        if (idx + 1) % 20 == 0:
            logger.info(f"Evaluated {idx + 1}/{len(df)} samples")
    
    # Save per-sample results
    results_df = pd.DataFrame(per_sample_results)
    results_df.to_csv(evaluation_results.path, index=False)
    logger.info(f"Saved per-sample results to {evaluation_results.path}")
    
    # Compute aggregated metrics
    metric_columns = [m.__class__.__name__ for m in metrics_list]
    aggregated = {}
    
    for metric_name in metric_columns:
        if metric_name in results_df.columns:
            mean_score = results_df[metric_name].mean()
            aggregated[metric_name] = float(mean_score)
            logger.info(f"{metric_name}: {mean_score:.4f}")
    
    # Calculate overall average
    aggregated["average_score"] = sum(aggregated.values()) / len(aggregated) if aggregated else 0.0
    
    # Log to Kubeflow
    for metric_name, score in aggregated.items():
        aggregated_metrics.log_metric(metric_name, score)
    
    logger.info(f"\nAggregated metrics: {aggregated}")
    
    return aggregated
