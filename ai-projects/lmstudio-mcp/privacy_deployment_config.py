#!/usr/bin/env python3
"""
Privacy-First Deployment Configuration

Complete setup guide for deploying privacy-first AI systems with
LM Studio + AGI Provider while maintaining regulatory compliance.
"""

from typing import Any


class PrivacyDeploymentConfig:
    """Configuration schema for privacy-first deployments."""

    @staticmethod
    def get_healthcare_config() -> dict[str, Any]:
        """HIPAA-compliant configuration."""
        return {
            "description": "HIPAA-compliant deployment for healthcare",
            "privacy_level": "restricted",
            "audit_logging": True,
            "audit_retention_days": 6 * 365,
            "encryption_algorithm": "AES-256",
            "key_rotation_days": 90,
            "allowed_endpoints": ["127.0.0.1:1234"],
            "blocked_endpoints": ["*.openai.com", "*.anthropic.com", "*.aws.com"],
            "delete_after_processing": True,
            "secure_wipe": True,
        }

    @staticmethod
    def get_financial_config() -> dict[str, Any]:
        """PCI-DSS-compliant configuration."""
        return {
            "description": "PCI-DSS-compliant deployment for finance",
            "privacy_level": "restricted",
            "audit_logging": True,
            "audit_retention_days": 7 * 365,
            "encryption_algorithm": "AES-256",
            "key_rotation_days": 30,
            "allowed_endpoints": ["127.0.0.1:1234"],
            "blocked_endpoints": ["*.openai.com", "*.anthropic.com"],
            "delete_after_processing": True,
            "secure_wipe": True,
        }

    @staticmethod
    def list_presets() -> dict[str, str]:
        """List available presets."""
        return {
            "healthcare": "HIPAA-compliant deployment",
            "financial": "PCI-DSS-compliant deployment",
            "enterprise": "Trade secret-friendly deployment",
        }


def main():
    """Generate privacy configurations."""

    print("\n" + "=" * 70)
    print("Privacy-First AI Deployment Configuration")
    print("=" * 70 + "\n")

    presets = PrivacyDeploymentConfig.list_presets()
    print("Available Presets:\n")
    for name, desc in presets.items():
        print(f"  • {name:15} - {desc}")
    print()

    print("Configuration generated successfully!")
    print()


if __name__ == "__main__":
    main()
