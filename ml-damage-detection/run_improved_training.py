"""
Run improved CNN training with fixed MobileNetV2 preprocessing.
Quick launcher with summary output.
"""
import os, sys
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "2"
sys.path.insert(0, os.path.dirname(__file__))

from train_cnn import run_training

if __name__ == "__main__":
    results = run_training()
    print("\n" + "="*55)
    print("  IMPROVED TRAINING COMPLETE")
    print("="*55)
    for k, v in results.items():
        if isinstance(v, dict) and "best_val_acc" in v:
            print(f"  {k:<32}: {v['best_val_acc']:.4f}")
