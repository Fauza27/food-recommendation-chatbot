#!/usr/bin/env python3
"""
Food Chatbot Dataset Pipeline Orchestrator.
Executes the ETL pipeline stages sequentially or individually.

Usage:
    python run_pipeline.py              # Run all steps
    python run_pipeline.py --step 1     # Run specific step only
    python run_pipeline.py --skip 1,2   # Skip specific steps
"""

import os
import sys
import subprocess
import argparse
from dotenv import load_dotenv

load_dotenv()

# PIPELINE STEPS

STEPS = {
    1: {
        "name": "Transkripsi Audio",
        "script": "pipeline/step1_transcribe.py",
        "description": "Mengubah audio menjadi text (Azure Speech Service)",
        "requires": ["AZURE_SPEECH_KEY", "AZURE_REGION"]
    },
    2: {
        "name": "Cleaning Transkripsi",
        "script": "pipeline/step2_clean.py",
        "description": "Memperbaiki typo dan kesalahan (GPT-4o-mini)",
        "requires": ["OPENAI_API_KEY"]
    },
    3: {
        "name": "Ekstraksi Informasi",
        "script": "pipeline/step3_extract.py",
        "description": "Mengekstrak data terstruktur (GPT-4o-mini)",
        "requires": ["OPENAI_API_KEY"]
    },
    4: {
        "name": "Pencarian Link Lokasi (GCP)",
        "script": "pipeline/step4_gcp_places.py",
        "description": "Mencari link lokasi dengan Google Maps Places API",
        "requires": ["GCP_MAPS_API_KEY"]
    }
}

# FUNCTIONS

def print_header():
    print("  RUN PIPELINE - Food Chatbot Dataset")

def check_credentials(step_num):
    """Check if required credentials are set"""
    step = STEPS[step_num]
    missing = []
    
    for env_var in step["requires"]:
        if not os.getenv(env_var):
            missing.append(env_var)
    
    if missing:
        print(f"[ERROR] Missing credentials for Step {step_num}:")
        for var in missing:
            print(f"   - {var}")
        return False
    
    return True

def run_step(step_num):
    """Run a specific pipeline step"""
    step = STEPS[step_num]
    
    print(f"\n{'='*80}")
    print(f"STEP {step_num}: {step['name']}")
    print(f"{'='*80}")
    print(f"Description: {step['description']}")
    print(f"Script: {step['script']}")
    
    # Check credentials
    if not check_credentials(step_num):
        print(f"[WARNING] Skipping Step {step_num} due to missing credentials")
        print("   Set environment variables and try again")
        return False
    
    # Check if script exists
    if not os.path.exists(step['script']):
        print(f"[ERROR] Script not found: {step['script']}")
        return False
    
    # Run script
    print(f"Running: python {step['script']}")
    
    try:
        result = subprocess.run(
            [sys.executable, step['script']],
            check=True
        )
        
        print(f"[SUCCESS] Step {step_num} completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Step {step_num} failed with error code {e.returncode}")
        return False
    except KeyboardInterrupt:
        print(f"[WARNING] Step {step_num} interrupted by user")
        return False

def main():
    parser = argparse.ArgumentParser(description='Run Food Chatbot Dataset Pipeline')
    parser.add_argument('--step', type=int, help='Run specific step only (1-4)')
    parser.add_argument('--skip', type=str, help='Skip specific steps (comma-separated, e.g., 1,2)')
    parser.add_argument('--list', action='store_true', help='List all steps')
    
    args = parser.parse_args()
    
    print_header()
    
    # List steps
    if args.list:
        print("Pipeline Steps:")
        for num, step in STEPS.items():
            print(f"Step {num}: {step['name']}")
            print(f"  Description: {step['description']}")
            print(f"  Script: {step['script']}")
            print(f"  Requires: {', '.join(step['requires']) if step['requires'] else 'None'}")
        sys.exit(0)
    
    # Determine which steps to run
    if args.step:
        # Run specific step
        if args.step not in STEPS:
            print(f"[ERROR] Invalid step number: {args.step}")
            print(f"   Valid steps: 1-{len(STEPS)}")
            sys.exit(1)
        
        steps_to_run = [args.step]
        print(f"Running Step {args.step} only")
        
    else:
        # Run all steps (with optional skip)
        steps_to_run = list(STEPS.keys())
        
        if args.skip:
            skip_steps = [int(s.strip()) for s in args.skip.split(',')]
            steps_to_run = [s for s in steps_to_run if s not in skip_steps]
            print(f"Running all steps except: {', '.join(map(str, skip_steps))}")
        else:
            print("Running all steps")
    
    print(f"Steps to run: {', '.join(map(str, steps_to_run))}")
    
    # Confirm
    confirm = input("Continue? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Cancelled.")
        sys.exit(0)
    
    # Run steps
    success_count = 0
    failed_count = 0
    
    for step_num in steps_to_run:
        success = run_step(step_num)
        
        if success:
            success_count += 1
        else:
            failed_count += 1
            
            # Ask if want to continue
            if step_num != steps_to_run[-1]:  # Not last step
                cont = input(f"\nStep {step_num} failed. Continue to next step? (y/n): ").strip().lower()
                if cont != 'y':
                    print("Pipeline stopped by user")
                    break
    
    # Summary
    print("PIPELINE SUMMARY")
    print(f"Successful: {success_count}/{len(steps_to_run)} steps")
    print(f"Failed: {failed_count}/{len(steps_to_run)} steps")
    
    if failed_count == 0:
        print("All steps completed successfully!")
        print("Output: data/chatbot_food_dataset.csv")
        print("Dataset ready for model training.")
    else:
        print("Some steps failed. Check errors above.")
        print("You can resume by running specific steps with --step")
    

if __name__ == "__main__":
    main()
