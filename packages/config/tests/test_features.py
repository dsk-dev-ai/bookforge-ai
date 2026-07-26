"""Tests for feature flags."""

from bookforge.config.features import FeatureFlags


class TestFeatureFlags:
    def test_defaults(self) -> None:
        flags = FeatureFlags()
        assert flags.nvidia_enabled is True
        assert flags.ollama_enabled is True
        assert flags.research_enabled is True
        assert flags.writer_enabled is True
        assert flags.publishing_enabled is True
        assert flags.dashboard_enabled is True
        assert flags.experimental_enabled is False
        assert flags.fallback_enabled is True
        assert flags.telemetry_enabled is False

    def test_override_via_init(self) -> None:
        flags = FeatureFlags(
            nvidia_enabled=False,
            experimental_enabled=True,
            telemetry_enabled=True,
        )
        assert flags.nvidia_enabled is False
        assert flags.experimental_enabled is True
        assert flags.telemetry_enabled is True
        assert flags.ollama_enabled is True
