---
name: device-fingerprinting
description: Flags unrecognized devices and devices shared across many accounts, a common account-takeover pattern. WHEN: "check device", "device fingerprint", "new device", "shared device", "device takeover", "unknown device risk".
---

# Device Fingerprinting

## Overview

Assesses the device used for the transaction. A device with no prior history for
the account, or one shared across many distinct accounts, elevates risk.

## When to Use

- During the detection phase, whenever the transaction carries a device
  identifier and enrichment has run.

## Inputs

| Input | Required | Description |
| --- | --- | --- |
| `transaction.device_id` | yes | Device fingerprint identifier. |
| `enrichment.device_known` | no | Whether the device has prior history for the account. |
| `enrichment.device_account_count` | no | Distinct accounts seen on the device. |

## Process

1. If `device_known` is false, add severity for a first-seen device.
2. If `device_account_count` is three or more, add severity that scales with the
   count, reflecting a device shared across many accounts.
3. Emit a `device_risk` signal with the supporting evidence.

## Outputs

Zero or one `RiskSignal`.

## Reference Implementation

`src/fraud_investigator/skills/device_fingerprint.py`.

## Rationalizations

| Excuse | Rebuttal |
| --- | --- |
| "Users buy new phones all the time." | A new device is low severity alone; corroboration drives the decision. |
| "Shared devices happen in families." | Sharing across many unrelated accounts is the pattern, not two. |

## Red Flags

- The skill runs without enrichment having populated device features.
- A missing device identifier is treated as a known device.

## Verification

- A shared-device or first-seen-device case produces a signal with evidence.
