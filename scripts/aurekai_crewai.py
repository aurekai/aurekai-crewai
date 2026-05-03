"""
aurekai_crewai.py — CrewAI crews for Aurekai capability families.
6 crews: Client Delivery, Model Memory, Wire Report, Reasoning Proof, Release Validation, Commerce Ops.
"""
from __future__ import annotations

import json
import subprocess
from typing import Any

from crewai import Agent, Crew, Process, Task
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


def _run_akai(args: list[str], timeout: int = 300) -> str:
    result = subprocess.run(
        ["akai", *args, "--json"],
        capture_output=True, text=True, timeout=timeout,
    )
    return result.stdout or result.stderr


# ── Tools ─────────────────────────────────────────────────────────────────────

class AkaiDoctorTool(BaseTool):
    name: str = "akai_doctor"
    description: str = "Run Akai doctor --deep diagnostics. Returns JSON."

    def _run(self, deep: bool = True) -> str:
        return _run_akai(["doctor", "--deep"] if deep else ["doctor"])


class AkaiTranscribeTool(BaseTool):
    name: str = "akai_transcribe"
    description: str = "Transcribe audio file. Input: audio_path. Returns JSON transcript."

    def _run(self, audio_path: str, language: str = "en") -> str:
        return _run_akai(["transcribe", "audio", "--input", audio_path, "--language", language], timeout=600)


class AkaiBriefTool(BaseTool):
    name: str = "akai_brief"
    description: str = "Generate a brief from artifact_id. Returns JSON brief."

    def _run(self, artifact_id: str) -> str:
        return _run_akai(["brief", "generate", "--artifact", artifact_id])


class AkaiProofBundleTool(BaseTool):
    name: str = "akai_proof_bundle"
    description: str = "Export proof bundle. Returns JSON with proof_uri."

    def _run(self, run_id: str = "") -> str:
        args = ["proof", "bundle"]
        if run_id:
            args += ["--run-id", run_id]
        return _run_akai(args)


class AkaiFPQTool(BaseTool):
    name: str = "akai_fpq_compress"
    description: str = "FPQ compress a model. Input: model_tag, bits. Returns JSON."

    def _run(self, model_tag: str, bits: int = 8) -> str:
        return _run_akai(["fpq", "compress", "--model", model_tag, "--bits", str(bits)], timeout=600)


class AkaiSAETool(BaseTool):
    name: str = "akai_sae_audit"
    description: str = "SAE feature audit. Returns JSON features."

    def _run(self, artifact_id: str = "") -> str:
        args = ["sae", "audit"]
        if artifact_id:
            args += ["--artifact", artifact_id]
        return _run_akai(args)


class AkaiWireReportTool(BaseTool):
    name: str = "akai_wire_report"
    description: str = "Generate wire report for a PCAP capture_id. Returns JSON report."

    def _run(self, capture_id: str) -> str:
        return _run_akai(["wire", "report", "--capture", capture_id])


class AkaiInvoiceTool(BaseTool):
    name: str = "akai_invoice"
    description: str = "Generate client invoice. Input: client_id, period. Returns JSON."

    def _run(self, client_id: str, period: str = "current") -> str:
        return _run_akai(["pay", "invoice", "--client", client_id, "--period", period])


class AkaiReleaseGateTool(BaseTool):
    name: str = "akai_release_gate"
    description: str = "Run release gate check. Returns JSON gate result."

    def _run(self, strict: bool = True) -> str:
        return _run_akai(["release", "gate", "--strict"] if strict else ["release", "gate"])


class AkaiVecSearchTool(BaseTool):
    name: str = "akai_vec_search"
    description: str = "Vec search over model memory. Input: query, top_k. Returns JSON results."

    def _run(self, query: str, top_k: int = 10) -> str:
        return _run_akai(["vec", "search", "--query", query, "--top-k", str(top_k)])


# ── Crew 1: Client Delivery ───────────────────────────────────────────────────

def build_client_delivery_crew(audio_path: str = "audio.wav") -> Crew:
    transcriber = Agent(
        role="Transcriptionist",
        goal="Transcribe raw audio to clean text with proof",
        backstory="Specialized in audio intake and normalization via Akai",
        tools=[AkaiTranscribeTool()],
        verbose=True,
    )
    writer = Agent(
        role="Brief Writer",
        goal="Generate a client-ready brief from transcribed artifact",
        backstory="Specialized in brief generation and packaging",
        tools=[AkaiBriefTool()],
        verbose=True,
    )
    proofer = Agent(
        role="Proof Archivist",
        goal="Bundle proofs for the completed client delivery",
        backstory="Ensures all deliverables have cryptographic proof records",
        tools=[AkaiProofBundleTool()],
        verbose=True,
    )

    t1 = Task(description=f"Transcribe {audio_path} and return artifact_id", agent=transcriber, expected_output="JSON with artifact_id and proof_uri")
    t2 = Task(description="Generate brief from the artifact_id returned by transcription", agent=writer, expected_output="JSON brief with artifact_id")
    t3 = Task(description="Export proof bundle for the completed brief", agent=proofer, expected_output="JSON with proof_uri")

    return Crew(agents=[transcriber, writer, proofer], tasks=[t1, t2, t3], process=Process.sequential)


# ── Crew 2: Model Memory ──────────────────────────────────────────────────────

def build_model_memory_crew(model_tag: str = "latest") -> Crew:
    compressor = Agent(
        role="FPQ Compressor",
        goal=f"Compress model {model_tag} using FPQ",
        backstory="Specialist in floating point quantization",
        tools=[AkaiFPQTool()],
        verbose=True,
    )
    auditor = Agent(
        role="SAE Auditor",
        goal="Audit SAE features after compression",
        backstory="Interprets sparse autoencoder activations for model safety",
        tools=[AkaiSAETool()],
        verbose=True,
    )
    searcher = Agent(
        role="Vec Retrieval Specialist",
        goal="Validate memory index after FPQ compression",
        backstory="Expert in vector search over Akai model memory",
        tools=[AkaiVecSearchTool()],
        verbose=True,
    )

    t1 = Task(description=f"FPQ compress model {model_tag} at 8-bit", agent=compressor, expected_output="JSON with compressed model artifact_id")
    t2 = Task(description="SAE audit the compressed artifact", agent=auditor, expected_output="JSON feature activation report")
    t3 = Task(description="Run vec search 'test model memory integrity' to validate index", agent=searcher, expected_output="JSON search results")

    return Crew(agents=[compressor, auditor, searcher], tasks=[t1, t2, t3], process=Process.sequential)


# ── Crew 3: Wire Report ───────────────────────────────────────────────────────

def build_wire_report_crew(capture_id: str = "latest") -> Crew:
    analyst = Agent(
        role="Wire Analyst",
        goal="Generate wire report from PCAP capture",
        backstory="Specialized in network capture analysis via AkaiWire",
        tools=[AkaiWireReportTool()],
        verbose=True,
    )
    proofer = Agent(
        role="Proof Archivist",
        goal="Bundle proofs for the wire report",
        backstory="Ensures wire reports are cryptographically archived",
        tools=[AkaiProofBundleTool()],
        verbose=True,
    )

    t1 = Task(description=f"Generate wire report for capture {capture_id}", agent=analyst, expected_output="JSON wire report")
    t2 = Task(description="Export proof bundle for the wire report", agent=proofer, expected_output="JSON with proof_uri")

    return Crew(agents=[analyst, proofer], tasks=[t1, t2], process=Process.sequential)


# ── Crew 4: Reasoning Proof ───────────────────────────────────────────────────

def build_reasoning_proof_crew() -> Crew:
    diagnostician = Agent(
        role="Runtime Diagnostician",
        goal="Ensure runtime health before reasoning",
        backstory="Validates Akai runtime before reasoning sessions",
        tools=[AkaiDoctorTool()],
        verbose=True,
    )
    proofer = Agent(
        role="Proof Archivist",
        goal="Bundle proofs after reasoning",
        backstory="Archives reasoning session proofs",
        tools=[AkaiProofBundleTool()],
        verbose=True,
    )

    t1 = Task(description="Run doctor --deep and confirm runtime health", agent=diagnostician, expected_output="JSON diagnostics with ok=true")
    t2 = Task(description="Export proof bundle for the reasoning session", agent=proofer, expected_output="JSON with proof_uri")

    return Crew(agents=[diagnostician, proofer], tasks=[t1, t2], process=Process.sequential)


# ── Crew 5: Release Validation ────────────────────────────────────────────────

def build_release_validation_crew() -> Crew:
    diagnostician = Agent(
        role="Runtime Diagnostician",
        goal="Deep diagnostics before release",
        backstory="Ensures all runtime checks pass",
        tools=[AkaiDoctorTool()],
        verbose=True,
    )
    gate_keeper = Agent(
        role="Release Gate Keeper",
        goal="Run strict release gate and confirm pass",
        backstory="Final authority on release decisions",
        tools=[AkaiReleaseGateTool()],
        verbose=True,
    )
    proofer = Agent(
        role="Proof Archivist",
        goal="Archive release proof",
        backstory="Ensures releases have cryptographic proof records",
        tools=[AkaiProofBundleTool()],
        verbose=True,
    )

    t1 = Task(description="Run doctor --deep", agent=diagnostician, expected_output="JSON diagnostics ok=true")
    t2 = Task(description="Run release gate --strict", agent=gate_keeper, expected_output="JSON gate passed=true")
    t3 = Task(description="Export release proof bundle", agent=proofer, expected_output="JSON with proof_uri")

    return Crew(agents=[diagnostician, gate_keeper, proofer], tasks=[t1, t2, t3], process=Process.sequential)


# ── Crew 6: Commerce Ops ──────────────────────────────────────────────────────

def build_commerce_ops_crew(client_id: str, period: str = "current") -> Crew:
    biller = Agent(
        role="Commerce Billing Agent",
        goal=f"Generate invoice for client {client_id}",
        backstory="Handles all Akai metering and invoice generation",
        tools=[AkaiInvoiceTool()],
        verbose=True,
    )
    proofer = Agent(
        role="Proof Archivist",
        goal="Archive billing proof",
        backstory="Ensures invoices have audit proof records",
        tools=[AkaiProofBundleTool()],
        verbose=True,
    )

    t1 = Task(description=f"Generate invoice for client {client_id} period {period}", agent=biller, expected_output="JSON invoice")
    t2 = Task(description="Export proof bundle for invoice", agent=proofer, expected_output="JSON with proof_uri")

    return Crew(agents=[biller, proofer], tasks=[t1, t2], process=Process.sequential)
