# Dependency sanitization report

## Strategy

| Field | Value |
| --- | --- |
| SOURCE_REPO_PATH | public/BTCFuturesReopenResidualFairValueV4.cs |
| PUBLIC_PACKAGE_PATH | NinjaTrader/Strategies/EOF/MR/BTCFuturesReopenResidualFairValueV4.cs |
| SOURCE_SHA256 | 1605b3af0eba86679e05f2ef6ce4f17126ea36a0bc0ad55c7ab0e1aa31f0dafa |
| PUBLIC_SHA256 | 1605b3af0eba86679e05f2ef6ce4f17126ea36a0bc0ad55c7ab0e1aa31f0dafa |
| SANITIZATION_REQUIRED | NO |

Executable body unchanged from the already-public sanitized forum copy.

## Core dependencies

### V4ResidualFairValueCore.cs

| Field | Value |
| --- | --- |
| SOURCE_REPO_PATH | ninja/EOF/MR/V4ResidualFairValueCore.cs |
| PUBLIC_PACKAGE_PATH | NinjaTrader/Core/V4ResidualFairValueCore.cs |
| SANITIZATION_REQUIRED | NO |

### BtcReopenBasisMrSignalCore.cs

| Field | Value |
| --- | --- |
| SOURCE_REPO_PATH | ninja/EOF/MR/BtcReopenBasisMrSignalCore.cs |
| PUBLIC_PACKAGE_PATH | NinjaTrader/Core/BtcReopenBasisMrSignalCore.cs |
| SANITIZATION_REQUIRED | NO |

### BtcReopenEventGate.cs

| Field | Value |
| --- | --- |
| SOURCE_REPO_PATH | ninja/EOF/MR/BtcReopenEventGate.cs |
| PUBLIC_PACKAGE_PATH | NinjaTrader/Core/BtcReopenEventGate.cs |
| SANITIZATION_REQUIRED | NO |

### GeneratedV1Calendars.cs

| Field | Value |
| --- | --- |
| SOURCE_REPO_PATH | ninja/EOF/MR/GeneratedV1Calendars.cs |
| PUBLIC_PACKAGE_PATH | NinjaTrader/Core/GeneratedV1Calendars.cs |
| SANITIZATION_REQUIRED | NO |

### Spot24x7DiagnosticCore.cs

| Field | Value |
| --- | --- |
| SOURCE_REPO_PATH | core/Spot24x7DiagnosticCore.cs |
| PUBLIC_PACKAGE_PATH | NinjaTrader/Core/Spot24x7DiagnosticCore.cs |
| SANITIZATION_REQUIRED | YES |

Change:

- CATEGORY = ABSOLUTE_PRIVATE_PATH
- FIELD = Spot24x7DiagnosticConstants.CanonicalOutputDirectory
- ACTION = REPLACED_WITH_GENERIC_PLACEHOLDER `C:\Data\BTCREOPENMR\results\nt_spot24x7_diagnostic`
- V4 IMPACT = NONE (constant unused by Spot24x7IdentityValidator / V4 trading path)

Exact SOURCE_SHA256 / PUBLIC_SHA256 for each file are listed in PACKAGE_MANIFEST.txt.

## Semantic gates

- TRADING_LOGIC_CHANGED = NO
- SIGNAL_LOGIC_CHANGED = NO
- ORDER_LOGIC_CHANGED = NO
- TIMING_LOGIC_CHANGED = NO

## Exact hashes

### NinjaTrader/Core/BtcReopenBasisMrSignalCore.cs
- SOURCE_SHA256 = 33b5e74b77495c37f85da399d1a1da25bb3ec480b69ef1564fc37d73a1887edc
- PUBLIC_SHA256 = 33b5e74b77495c37f85da399d1a1da25bb3ec480b69ef1564fc37d73a1887edc
- SANITIZATION_REQUIRED = NO

### NinjaTrader/Core/BtcReopenEventGate.cs
- SOURCE_SHA256 = c27b500c0933d836cb661abd5ea890dd535bd0016be2bc956d0e97bcffc7c244
- PUBLIC_SHA256 = c27b500c0933d836cb661abd5ea890dd535bd0016be2bc956d0e97bcffc7c244
- SANITIZATION_REQUIRED = NO

### NinjaTrader/Core/GeneratedV1Calendars.cs
- SOURCE_SHA256 = ad61265654c5566da38026dca52f2c07f98e66ff7b18d4b99538ac24054b6634
- PUBLIC_SHA256 = ad61265654c5566da38026dca52f2c07f98e66ff7b18d4b99538ac24054b6634
- SANITIZATION_REQUIRED = NO

### NinjaTrader/Core/Spot24x7DiagnosticCore.cs
- SOURCE_SHA256 = ab4fd0434dd428d8dfa7efa672b574e3a9021f24ea2fca9538eb42a6c3e62a8a
- PUBLIC_SHA256 = 85eaa6dba8e2d76ef874b2c752f18117381c5f8147d56a4fb356228d6cc18c5a
- SANITIZATION_REQUIRED = YES

### NinjaTrader/Core/V4ResidualFairValueCore.cs
- SOURCE_SHA256 = d079f8ae9a4ac8f3aae5460dde61d07699bd6f70df626565f65501cc7b001818
- PUBLIC_SHA256 = d079f8ae9a4ac8f3aae5460dde61d07699bd6f70df626565f65501cc7b001818
- SANITIZATION_REQUIRED = NO

### NinjaTrader/Strategies/EOF/MR/BTCFuturesReopenResidualFairValueV4.cs
- SOURCE_SHA256 = 1605b3af0eba86679e05f2ef6ce4f17126ea36a0bc0ad55c7ab0e1aa31f0dafa
- PUBLIC_SHA256 = 1605b3af0eba86679e05f2ef6ce4f17126ea36a0bc0ad55c7ab0e1aa31f0dafa
- SANITIZATION_REQUIRED = NO
