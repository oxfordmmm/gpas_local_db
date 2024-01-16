# Entity Relationship Diagram

```mermaid
erDiagram
    OWNER
    RUN
    SPECIMEN
    SAMPLE
    ANALYSIS
    SPECIATION
    DRUG_RESISTANCE
    OTHER

    RUN ||--o{ SAMPLE : contains
    OWNER ||--o{ SPECIMEN : owns
    SPECIMEN ||--o{ SAMPLE : taken_from
    SAMPLE ||--o{ ANALYSIS : analysed
    ANALYSIS ||--o{ SPECIATION : is
    ANALYSIS ||--o{ DRUG_RESISTANCE : treated_by
    ANALYSIS ||--o{ OTHER : results
```
