"""
Evaluate camera pose estimation results.
Compares predicted poses against ground truth and outputs metrics to CSV.
"""

import argparse
import numpy as np
import yaml
import csv
from pathlib import Path
from scipy.spatial.transform import Rotation as R


def parse_pose_csv(pose_file):
    """
    Parse pose file with format: image_name qw qx qy qz tx ty tz

    Args:
        pose_file (str): Path to the pose file.

    Returns:
        dict: A dictionary mapping image names to 4x4 transformation matrices.
    """
    poses = {}

    with open(pose_file, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            parts = line.split()
            if len(parts) >= 8:
                name = parts[0]
                qw, qx, qy, qz = map(float, parts[1:5])
                tx, ty, tz = map(float, parts[5:8])

                r = R.from_quat([qx, qy, qz, qw])
                R_mat = r.as_matrix()
                tvec = np.array([tx, ty, tz]).reshape(3, 1)

                pose_matrix = np.eye(4)
                pose_matrix[:3, :3] = R_mat
                pose_matrix[:3, 3] = tvec.flatten()

                # Invert the pose to get camera-to-world
                poses[name] = pose_matrix

    return poses

def apply_coordinate_correction(poses, flip_y=False, flip_z=False):
    """
    Apply coordinate system correction to poses.
    
    Args:
        poses (dict): Dictionary of poses.
        flip_y (bool): Whether to flip Y axis.
        flip_z (bool): Whether to flip Z axis.
    
    Returns:
        dict: Corrected poses.
    """
    if not flip_y and not flip_z:
        return poses
    
    correction_matrix = np.eye(4)
    if flip_y:
        correction_matrix[1, 1] = -1
    if flip_z:
        correction_matrix[2, 2] = -1
    
    return {name: pose @ correction_matrix for name, pose in poses.items()}


def compute_pose_errors(gt_poses, pred_poses):
    """
    Compute translation and rotation errors.
    
    Args:
        gt_poses (list): List of ground truth 4x4 matrices.
        pred_poses (list): List of predicted 4x4 matrices.
    
    Returns:
        tuple: (trans_errors, rot_errors) as numpy arrays.
    """
    trans_errors = []
    rot_errors = []
    
    for gt, pred in zip(gt_poses, pred_poses):
        # Translation error
        trans_error = np.linalg.norm(gt[:3, 3] - pred[:3, 3])
        trans_errors.append(trans_error)
        
        # Rotation error
        R_gt = gt[:3, :3]
        R_pred = pred[:3, :3]
        R_diff = R_gt @ R_pred.T
        trace = np.clip((np.trace(R_diff) - 1) / 2, -1.0, 1.0)
        angle = np.arccos(trace)
        rot_error = np.degrees(angle)
        rot_errors.append(rot_error)
    
    return np.array(trans_errors), np.array(rot_errors)


def compute_metrics(trans_errors, rot_errors, thresholds):
    """
    Compute various error metrics.
    
    Args:
        trans_errors (np.array): Translation errors in meters.
        rot_errors (np.array): Rotation errors in degrees.
        thresholds (dict): Dictionary of threshold configurations.
    
    Returns:
        dict: Dictionary of computed metrics.
    """
    metrics = {
        'num_poses': len(trans_errors),
        'median_trans_error': np.median(trans_errors),
        'median_rot_error': np.median(rot_errors),
        'mean_trans_error': np.mean(trans_errors),
        'mean_rot_error': np.mean(rot_errors),
        'rmse_trans_error': np.sqrt(np.mean(trans_errors**2)),
        'rmse_rot_error': np.sqrt(np.mean(rot_errors**2)),
    }
    
    # Compute accuracy at various thresholds
    for thresh_name, thresh_vals in thresholds.items():
        trans_thresh = thresh_vals['translation']
        rot_thresh = thresh_vals['rotation']
        accuracy = np.sum((trans_errors < trans_thresh) & 
                         (rot_errors < rot_thresh)) / len(trans_errors) * 100
        metrics[f'accuracy_{thresh_name}'] = accuracy
    
    return metrics


def save_metrics_to_csv(metrics, experiment_name, output_file):
    """
    Save metrics to CSV file.
    
    Args:
        metrics (dict): Dictionary of metrics.
        experiment_name (str): Name of the experiment.
        output_file (str): Path to output CSV file.
    """
    output_path = Path(output_file)
    file_exists = output_path.exists()
    
    # Prepare row data
    row_data = {'experiment': experiment_name}
    row_data.update(metrics)
    
    # Write to CSV
    with open(output_file, 'a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=row_data.keys())
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(row_data)
    
    print(f"\nMetrics saved to: {output_file}")


def print_metrics(metrics, experiment_name):
    """Print metrics to console."""
    print("\n" + "="*70)
    print(f"EXPERIMENT: {experiment_name}")
    print("="*70)
    print(f"\nNumber of poses: {metrics['num_poses']}")
    print(f"\nTranslation Errors:")
    print(f"  Median: {metrics['median_trans_error']:.3f}m")
    print(f"  Mean:   {metrics['mean_trans_error']:.3f}m")
    print(f"  RMSE:   {metrics['rmse_trans_error']:.3f}m")
    print(f"\nRotation Errors:")
    print(f"  Median: {metrics['median_rot_error']:.3f}deg")
    print(f"  Mean:   {metrics['mean_rot_error']:.3f}deg")
    print(f"  RMSE:   {metrics['rmse_rot_error']:.3f}deg")
    print(f"\nAccuracy:")
    
    for key, value in metrics.items():
        if key.startswith('accuracy_'):
            thresh_name = key.replace('accuracy_', '')
            print(f"  {thresh_name}: {value:.2f}%")
    
    print("="*70 + "\n")


def main():
    parser = argparse.ArgumentParser(description='Evaluate pose estimation results')
    parser.add_argument('--config', required=True, help='Path to evaluation config YAML')
    
    args = parser.parse_args()
    
    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)
    
    # Get parameters from config
    pred_path = config['pred']
    gt_path = config['gt']
    experiment_name = config['experiment']
    output_file = config.get('output', 'results.csv')
    
    print(f"Evaluating experiment: {experiment_name}")
    print(f"Predicted poses: {pred_path}")
    print(f"Ground truth poses: {gt_path}")
    
    # Load poses
    print("\nLoading poses...")
    gt_pose_dict = parse_pose_csv(gt_path)
    pred_pose_dict = parse_pose_csv(pred_path)
    
    print(f"  Ground truth: {len(gt_pose_dict)} poses")
    print(f"  Predicted: {len(pred_pose_dict)} poses")
    
    # Apply coordinate corrections if specified
    correction_config = config.get('coordinate_correction', {})
    if correction_config.get('apply_to_gt', False):
        print("\nApplying coordinate correction to ground truth...")
        gt_pose_dict = apply_coordinate_correction(
            gt_pose_dict,
            flip_y=correction_config.get('flip_y', False),
            flip_z=correction_config.get('flip_z', False)
        )
    
    if correction_config.get('apply_to_pred', False):
        print("Applying coordinate correction to predictions...")
        pred_pose_dict = apply_coordinate_correction(
            pred_pose_dict,
            flip_y=correction_config.get('flip_y', False),
            flip_z=correction_config.get('flip_z', False)
        )
    
    # Align poses
    common_names = sorted(set(gt_pose_dict.keys()) & set(pred_pose_dict.keys()))
    
    if len(common_names) == 0:
        print("\nError: No common poses found between GT and predictions!")
        return
    
    missing_gt = len(gt_pose_dict) - len(common_names)
    missing_pred = len(pred_pose_dict) - len(common_names)
    
    if missing_gt > 0:
        print(f"\nWarning: {missing_gt} GT poses not found in predictions")
    if missing_pred > 0:
        print(f"Warning: {missing_pred} predicted poses not found in GT")
    
    aligned_gt = [gt_pose_dict[name] for name in common_names]
    aligned_pred = [pred_pose_dict[name] for name in common_names]
    
    # Compute errors
    print(f"\nComputing errors for {len(common_names)} poses...")
    trans_errors, rot_errors = compute_pose_errors(aligned_gt, aligned_pred)
    
    # Compute metrics
    thresholds = config.get('accuracy_thresholds', {
        'strict': {'translation': 0.5, 'rotation': 2.0},
        'moderate': {'translation': 2.0, 'rotation': 5.0},
        'coarse': {'translation': 5.0, 'rotation': 10.0},
    })
    
    metrics = compute_metrics(trans_errors, rot_errors, thresholds)
    
    # Print results
    print_metrics(metrics, experiment_name)
    
    # Save to CSV
    save_metrics_to_csv(metrics, experiment_name, output_file)


if __name__ == "__main__":
    main()