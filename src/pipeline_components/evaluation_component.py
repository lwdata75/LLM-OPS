"""
Kubeflow component for evaluating model predictions using ragas metrics.

This component:
1. Takes predictions from the inference component
2. Computes ragas metrics (Rouge, BLEU, ExactMatch) per sample
3. Aggregates metrics into summary statistics
4. Outputs both per-sample and aggregated results
"""

from kfp import dsl
from kfp.dsl import (
    component, 
    Input,
    Output,
    Dataset,
    Metrics
)
from typing import List


@component(
    base_image="cicirello/pyaction:3.11",
    packages_to_install=[
        "pandas==2.3.3",
        "numpy==1.24.3", 
        "ragas==0.3.7",
        "rouge-score==0.1.2",
        "sacrebleu==2.4.3",
        "google-cloud-storage==2.10.0",
    ]
)
def evaluation_component(
    predictions: Input[Dataset],
    evaluation_results: Output[Dataset],
    aggregated_metrics: Output[Metrics]
):
    """
    Evaluate model predictions using ragas metrics.
    
    Args:
        predictions: Input dataset with predictions CSV file
        evaluation_results: Output dataset for per-sample metric scores CSV
        aggregated_metrics: Output metrics artifact for aggregated statistics
    """
    import pandas as pd
    import numpy as np
    import json
    from pathlib import Path
    from typing import Dict, List, Any
    import logging
    
    # Configure logging
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    try:
        # Import ragas components
        from ragas.metrics import (
            RougeScore,
            BleuScore, 
            ExactMatch,
        )
        from ragas import SingleTurnSample
        
        logger.info("✅ Successfully imported ragas components")
        
        # Define evaluation metrics
        EVALUATION_METRICS = [
            ExactMatch(),
            RougeScore(),
            BleuScore(),
        ]
        
        logger.info(f"🎯 Defined {len(EVALUATION_METRICS)} metrics for evaluation")
        
        def compute_metrics(row: pd.Series, metrics: List) -> Dict[str, float]:
            """
            Compute metrics for a single prediction row.
            
            Args:
                row: A pandas Series with columns 'user_input', 'reference', 'extracted_response'
                metrics: List of ragas metric objects
                
            Returns:
                Dictionary with metric names as keys and scores as values
            """
            try:
                # Create SingleTurnSample object
                sample = SingleTurnSample(
                    user_input=row['user_input'],
                    response=row['extracted_response'],
                    reference=row['reference']
                )
                
                logger.info(f"📝 Computing metrics for: '{row['user_input'][:50]}...'")
                
                # Compute each metric
                results = {}
                for metric in metrics:
                    try:
                        # Get metric name
                        metric_name = metric.__class__.__name__
                        
                        # Compute score
                        score = metric.single_turn_score(sample)
                        results[metric_name] = score
                        
                        logger.info(f"  ✅ {metric_name}: {score:.4f}")
                        
                    except Exception as e:
                        logger.error(f"  ❌ {metric.__class__.__name__} failed: {e}")
                        results[metric.__class__.__name__] = 0.0
                        
                return results
                
            except Exception as e:
                logger.error(f"❌ Error computing metrics: {e}")
                # Return default scores
                return {metric.__class__.__name__: 0.0 for metric in metrics}

        def aggregate_metrics(df_metrics: pd.DataFrame, metric_columns: List[str]) -> Dict[str, Dict[str, float]]:
            """
            Compute aggregated metrics from per-sample metrics DataFrame.
            
            Args:
                df_metrics: DataFrame with per-sample metric scores
                metric_columns: List of metric column names to aggregate
                
            Returns:
                Dictionary with aggregated statistics for each metric
            """
            aggregated = {}
            
            for metric in metric_columns:
                if metric in df_metrics.columns:
                    scores = df_metrics[metric]
                    
                    aggregated[metric] = {
                        'mean': float(scores.mean()),
                        'std': float(scores.std()),
                        'min': float(scores.min()),
                        'max': float(scores.max()),
                        'median': float(scores.median()),
                        'count': int(len(scores))
                    }
                else:
                    logger.warning(f"⚠️ Metric '{metric}' not found in DataFrame")
                    
            return aggregated
        
        # Load predictions data
        logger.info("📂 Loading predictions data...")
        df_predictions = pd.read_csv(predictions.path)
        
        logger.info(f"✅ Loaded {len(df_predictions)} predictions")
        logger.info(f"Columns: {list(df_predictions.columns)}")
        
        # Verify required columns
        required_cols = ['user_input', 'reference', 'extracted_response']
        missing_cols = [col for col in required_cols if col not in df_predictions.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        logger.info(f"✅ All required columns present: {required_cols}")
        
        # Process all predictions to compute per-sample metrics
        logger.info("🔄 Computing metrics for all predictions...")
        all_results = []
        
        for idx, row in df_predictions.iterrows():
            logger.info(f"📍 Processing sample {idx + 1}/{len(df_predictions)}")
            sample_results = compute_metrics(row, EVALUATION_METRICS)
            
            # Add row identifier and input data
            sample_results['sample_id'] = idx
            sample_results['user_input'] = row['user_input']
            sample_results['reference'] = row['reference']
            sample_results['extracted_response'] = row['extracted_response']
            
            all_results.append(sample_results)

        # Create DataFrame with per-sample results
        df_results = pd.DataFrame(all_results)
        logger.info(f"✅ Processed {len(df_results)} samples")
        
        # Save per-sample metrics
        df_results.to_csv(evaluation_results.path, index=False)
        logger.info(f"✅ Saved per-sample metrics to: {evaluation_results.path}")
        
        # Compute aggregated metrics
        metric_names = ['ExactMatch', 'RougeScore', 'BleuScore']
        aggregated_results = aggregate_metrics(df_results, metric_names)
        
        # Save aggregated metrics (for Kubeflow Metrics artifact)
        metrics_dict = {}
        for metric, stats in aggregated_results.items():
            for stat_name, value in stats.items():
                metrics_dict[f"{metric}_{stat_name}"] = value
        
        # Write to aggregated_metrics artifact
        with open(aggregated_metrics.path, 'w') as f:
            json.dump(metrics_dict, f, indent=2)
        
        logger.info(f"✅ Saved aggregated metrics to: {aggregated_metrics.path}")
        
        # Log summary
        logger.info("="*60)
        logger.info("🎯 EVALUATION SUMMARY")
        logger.info("="*60)
        logger.info(f"📊 Evaluated {len(df_results)} predictions using {len(EVALUATION_METRICS)} metrics")
        
        for metric, stats in aggregated_results.items():
            logger.info(f"🏆 {metric}: {stats['mean']:.4f} ± {stats['std']:.4f} (mean ± std)")
        
        logger.info("✅ Evaluation component completed successfully!")
        
    except Exception as e:
        logger.error(f"❌ Evaluation component failed: {e}")
        raise