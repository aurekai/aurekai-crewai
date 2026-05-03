<p align="center">
  <img src="https://raw.githubusercontent.com/aurekai/aurekai/main/assets/aurekai-logo.svg" alt="Aurekai" width="520" />
</p>

# `aurekai-crewai` · v0.8.0-alpha.5

Official CrewAI integration for Aurekai — 6 purpose-built crews covering client delivery, model memory, wire analysis, reasoning proof, release validation, and commerce ops.

## Crews

| Crew builder | Agents | Purpose |
|---|---|---|
| `build_client_delivery_crew()` | Transcriptionist, Brief Writer, Proof Archivist | Audio → brief → proof |
| `build_model_memory_crew()` | FPQ Compressor, SAE Auditor, Vec Retrieval Specialist | Compress → audit → validate memory |
| `build_wire_report_crew()` | Wire Analyst, Proof Archivist | PCAP → report → proof |
| `build_reasoning_proof_crew()` | Runtime Diagnostician, Proof Archivist | Diagnose → archive reasoning proof |
| `build_release_validation_crew()` | Runtime Diagnostician, Release Gate Keeper, Proof Archivist | Doctor → gate → proof |
| `build_commerce_ops_crew()` | Commerce Billing Agent, Proof Archivist | Invoice → proof |

## Tools (10)

`AkaiDoctorTool`, `AkaiTranscribeTool`, `AkaiBriefTool`, `AkaiProofBundleTool`, `AkaiFPQTool`, `AkaiSAETool`, `AkaiWireReportTool`, `AkaiInvoiceTool`, `AkaiReleaseGateTool`, `AkaiVecSearchTool`

## Quick Start

```python
from aurekai_crewai import build_client_delivery_crew

crew = build_client_delivery_crew(audio_path="recording.wav")
result = crew.kickoff()
print(result)
```


Aurekai integration surface for Crewai.

Status: active
Type: agent

## Core Template Set

- doctor-deep
- manifest-verify
- model-memory-pack
- sae-audit
- semantic-cache-bench
- proof-bundle-export
- release-gate

## Canonical References

- Platform: https://github.com/aurekai/aurekai
- Native runtime: https://github.com/aurekai/native-runtime
- Integration registry: https://github.com/aurekai/aurekai/blob/main/registry/integrations.json
- Ecosystem map: https://github.com/aurekai/aurekai/blob/main/ECOSYSTEM_NAMES.md
