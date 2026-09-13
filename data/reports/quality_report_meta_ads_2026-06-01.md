# Delivery Quality Report: `meta_ads_2026-06-01`
**Health Status:** `CRITICAL`  
**Processed At:** 2026-09-12T12:38:54.010641

## Summary Metrics
- **Total Rows:** 21
- **Valid Rows:** 0
- **Errors:** 21 (100.0%)
- **Duplicates:** 0
- **Total Spend:** $0.00

## Executed Quality Checks
| Check ID | Scope | Status | Message |
| --- | --- | --- | --- |
| `FILE_COMPLETENESS` | FILE | **PASSED** | File contains 21 total records. |
| `ROW_VALIDITY` | ROW | **FAILED** | High failure rate detected! Exceeds threshold of 5.0%. |
| `DELIVERY_DUPLICATION` | DELIVERY | **PASSED** | No duplicate records found across campaign metrics. |

## Sample Diagnostics (First 5 Failures)
| Line | Error Type | Reason | Raw Record |
| --- | --- | --- | --- |
| 1 | `ValidationError` | 5 validation errors for CampaignMetric
campaign
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/string_type
date_
  Input should be a valid date [type=date_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/date_type
spend_usd
  Input should be a valid number [type=float_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/float_type
impressions
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type
clicks
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type | `{'campaign': 'ABM Tier 1', 'date_ts': 1780272000000, 'spend': {'amount': '92.37', 'currency': 'EUR'}, 'impressions': 41097, 'clicks': 1283}` |
| 2 | `ValidationError` | 5 validation errors for CampaignMetric
campaign
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/string_type
date_
  Input should be a valid date [type=date_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/date_type
spend_usd
  Input should be a valid number [type=float_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/float_type
impressions
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type
clicks
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type | `{'campaign': 'ABM Tier 1', 'date_ts': 1780358400000, 'spend': {'amount': '152.88', 'currency': 'EUR'}, 'impressions': 68551, 'clicks': 2338}` |
| 3 | `ValidationError` | 5 validation errors for CampaignMetric
campaign
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/string_type
date_
  Input should be a valid date [type=date_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/date_type
spend_usd
  Input should be a valid number [type=float_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/float_type
impressions
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type
clicks
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type | `{'campaign': 'ABM Tier 1', 'date_ts': 1780444800000, 'spend': {'amount': '161.21', 'currency': 'EUR'}, 'impressions': 46624, 'clicks': 1368}` |
| 4 | `ValidationError` | 5 validation errors for CampaignMetric
campaign
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/string_type
date_
  Input should be a valid date [type=date_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/date_type
spend_usd
  Input should be a valid number [type=float_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/float_type
impressions
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type
clicks
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type | `{'campaign': 'ABM Tier 1', 'date_ts': 1780531200000, 'spend': {'amount': '79.22', 'currency': 'EUR'}, 'impressions': 26418, 'clicks': 535}` |
| 5 | `ValidationError` | 5 validation errors for CampaignMetric
campaign
  Input should be a valid string [type=string_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/string_type
date_
  Input should be a valid date [type=date_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/date_type
spend_usd
  Input should be a valid number [type=float_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/float_type
impressions
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type
clicks
  Input should be a valid integer [type=int_type, input_value=None, input_type=NoneType]
    For further information visit https://errors.pydantic.dev/2.13/v/int_type | `{'campaign': 'ABM Tier 1', 'date_ts': 1780617600000, 'spend': {'amount': '147.56', 'currency': 'EUR'}, 'impressions': 54399, 'clicks': 1293}` |