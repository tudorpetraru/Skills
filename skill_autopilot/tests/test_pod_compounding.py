from __future__ import annotations

import pytest

from skill_autopilot.pods import (
    ALL_ATTACHABLE_PODS,
    B_KERNELS,
    INDUSTRY_KERNEL_MAP,
    INDUSTRY_POD_MAP,
    select_kernels,
    select_pods,
)


class TestSelectPods:
    """Verify pod compounding from industry, keywords, and hints."""

    def test_always_includes_core_and_discovery(self) -> None:
        pods = select_pods(intent_text="Build a thing.")
        assert "core" in pods
        assert "discovery" in pods

    def test_keyword_attaches_legal_risk(self) -> None:
        pods = select_pods(intent_text="We need regulatory compliance and GDPR checks.")
        assert "legal_risk" in pods

    def test_keyword_attaches_data_insight(self) -> None:
        pods = select_pods(intent_text="Build a dashboard with analytics reporting.")
        assert "data_insight" in pods

    def test_industry_attaches_pods_pharma(self) -> None:
        pods = select_pods(
            intent_text="Build a clinical data collection app.",
            industry="Pharmaceuticals",
        )
        assert "legal_risk" in pods
        assert "finance_governance" in pods

    def test_industry_attaches_pods_banking(self) -> None:
        pods = select_pods(
            intent_text="Build a customer onboarding flow.",
            industry="Banking (retail/commercial)",
        )
        assert "legal_risk" in pods
        assert "finance_governance" in pods

    def test_industry_attaches_pods_ecommerce(self) -> None:
        pods = select_pods(
            intent_text="Build a storefront.",
            industry="E-commerce / Marketplaces",
        )
        assert "commercial" in pods
        assert "data_insight" in pods

    def test_industry_attaches_pods_defense(self) -> None:
        pods = select_pods(
            intent_text="Build a communication system.",
            industry="Defense",
        )
        assert "legal_risk" in pods
        assert "ops_supply" in pods

    def test_industry_fuzzy_match(self) -> None:
        """Industry matching is case-insensitive substring."""
        pods = select_pods(
            intent_text="Build something.",
            industry="pharmaceuticals",  # lowercase
        )
        assert "legal_risk" in pods

    def test_explicit_hints_override(self) -> None:
        pods = select_pods(
            intent_text="Build a SaaS app.",
            pod_hints=["people_talent", "ops_supply"],
        )
        assert "people_talent" in pods
        assert "ops_supply" in pods

    def test_no_duplicate_pods(self) -> None:
        """If keyword + industry both suggest the same pod, no duplicates."""
        pods = select_pods(
            intent_text="Need regulatory compliance for drug development.",
            industry="Pharmaceuticals",
        )
        pod_ids = list(pods.keys())
        assert len(pod_ids) == len(set(pod_ids))

    def test_industry_with_no_mapping_only_uses_keywords(self) -> None:
        pods = select_pods(
            intent_text="Build a thing with no special keywords.",
            industry="NonexistentIndustry",
        )
        # Should still have core + discovery, but no industry-based additions.
        assert "core" in pods
        assert "discovery" in pods
        assert len(pods) == 2


class TestSelectKernels:
    """Verify kernel selection from industry and text signals."""

    def test_industry_selects_correct_kernel(self) -> None:
        kernels = select_kernels(industry="Pharmaceuticals")
        kernel_ids = [k.kernel_id for k in kernels]
        assert "life_sciences" in kernel_ids

    def test_fallback_to_digital_product(self) -> None:
        kernels = select_kernels(industry="", intent_text="something generic")
        kernel_ids = [k.kernel_id for k in kernels]
        assert "digital_product" in kernel_ids

    def test_text_signal_selects_kernel(self) -> None:
        kernels = select_kernels(
            industry="",
            intent_text="We need to build security detections and incident response.",
        )
        kernel_ids = [k.kernel_id for k in kernels]
        assert "cyber_secops" in kernel_ids


class TestCompoundSelection:
    """Verify pods + kernels work together for realistic briefs."""

    def test_pharma_gets_full_compound(self) -> None:
        pods = select_pods(
            intent_text="Build a clinical trial data platform for drug candidates.",
            industry="Pharmaceuticals",
        )
        kernels = select_kernels(industry="Pharmaceuticals")

        # Pods: core, discovery, legal_risk, finance_governance
        assert "legal_risk" in pods
        assert "finance_governance" in pods

        # Kernel: life_sciences
        kernel_ids = [k.kernel_id for k in kernels]
        assert "life_sciences" in kernel_ids

    def test_software_saas_gets_commercial(self) -> None:
        pods = select_pods(
            intent_text="Build a SaaS platform for project management.",
            industry="Software / SaaS",
        )
        kernels = select_kernels(industry="Software / SaaS")

        assert "commercial" in pods
        kernel_ids = [k.kernel_id for k in kernels]
        assert "digital_product" in kernel_ids


class TestIndustryPodMapCoverage:
    """Ensure INDUSTRY_POD_MAP covers all 40 industries."""

    def test_all_40_industries_have_pod_mappings(self) -> None:
        missing = set(INDUSTRY_KERNEL_MAP.keys()) - set(INDUSTRY_POD_MAP.keys())
        assert not missing, f"Industries missing from INDUSTRY_POD_MAP: {missing}"

    def test_all_mapped_pods_exist(self) -> None:
        for industry, pod_ids in INDUSTRY_POD_MAP.items():
            for pid in pod_ids:
                assert pid in ALL_ATTACHABLE_PODS, (
                    f"Industry '{industry}' references unknown pod '{pid}'"
                )
