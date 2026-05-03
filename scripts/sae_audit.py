#!/usr/bin/env python3
"""Run a Sparse Autoencoder (SAE) audit on the given model via CrewAI tool."""
import subprocess
from crewai.tools import tool


@tool
def aurekai_sae_audit(model_id: str = "default") -> str:
    """Run a Sparse Autoencoder (SAE) audit on the given model"""
    out = subprocess.run(
        ["akai", "sae", "audit", "--model", model_id, "--json"],
        capture_output=True, text=True
    )
    return out.stdout + out.stderr


if __name__ == "__main__":
    print(aurekai_sae_audit(model_id="default"))
