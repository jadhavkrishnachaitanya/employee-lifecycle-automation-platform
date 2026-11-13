import argparse
import sys
import os
from backend.generator.data_generator import SyntheticDataGenerator
from backend.generator.exporter import export_dataset


def main():
    parser = argparse.ArgumentParser(
        description="YottaFlex Employee Lifecycle Synthetic Data Generator & Validation Engine"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=20261022,
        help="Deterministic random seed (default: 20261022)",
    )
    parser.add_argument(
        "--scale",
        type=str,
        choices=["starter", "full"],
        default="full",
        help="Dataset scale: starter (25 employees) or full (500 employees, 4000 tasks)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output directory path (defaults to data/starter or data/full)",
    )

    args = parser.parse_args()

    output_dir = args.output
    if not output_dir:
        output_dir = f"data/{args.scale}"

    print(f"================================================================")
    print(f" YottaFlex Deterministic Data Generator")
    print(f" Seed: {args.seed} | Scale: {args.scale} | Output: {output_dir}")
    print(f"================================================================")

    gen = SyntheticDataGenerator(seed=args.seed, scale=args.scale)
    print("Generating entity relational graph and injecting anomalies...")
    gen.generate_all()

    summary = gen.get_summary()
    print("\nGeneration Complete:")
    for k, v in summary.items():
        print(f"  - {k:25}: {v}")

    print(f"\nExporting dataset files to {output_dir}...")
    manifest = export_dataset(gen, output_dir)

    print("\nValidation & Evaluation Summary:")
    eval_metrics = manifest["evaluation_metrics"]
    print(f"  - True Positives (TP)     : {eval_metrics['true_positives']}")
    print(f"  - False Positives (FP)    : {eval_metrics['false_positives']}")
    print(f"  - False Negatives (FN)    : {eval_metrics['false_negatives']}")
    print(f"  - Precision               : {eval_metrics['precision']:.4f}")
    print(f"  - Recall                  : {eval_metrics['recall']:.4f}")
    print(f"  - F1 Score                : {eval_metrics['f1_score']:.4f}")

    print("\nManifest & Checksums generated successfully!")
    print(f"Done. Database ready at: {os.path.join(output_dir, 'orchestrator.db')}")


if __name__ == "__main__":
    main()
