# Database layout

```{.mermaid format=svg}
erDiagram
    OWNER {
        int id PK
        string(50) site
        user(50) user
    }

    RUN {
        int id PK
        string(50) code "unique"
        date run_date
        string(20) site
        string(20) sequencing_method
        string(20) machine
        string(5) user
        int number_samples
        string(20) flowcell
        bool passed_qc
        text comment
    }

    SPECIMEN {
        int owner_id FK
        int id PK
        string(20) accession "unique with date"
        date collection_date "unique with accession"
        string(3) country_sample_taken "iso 3 letter code"
        string(20) collection_site
        string(20) sample_type 
    }

    SAMPLE {
        int run_id FK
        int specimen_id FK
        int id PK
        string(50) guid "unique"
        string(20) extraction_method
        string(20) extraction_protocol
        date extraction_date
        string(5) extraction_user
        bool phl_amplifaction
        float pre_sequence_concentration
        bool dilution_post_initial_concentration
        float input_volume
        string(50) prep_kit
        string(20) illumina_index
        string(50) ont_barcode
        int phix_spike_in
        float library_pool_concentration
        text comment
    }

    SAMPLE_DETAIL {
        int sample_id FK "unique with sample_value_type_code"
        string(20) sample_value_type_code FK "unique with sample_id"
        int id PK
        string(50) value_str
        int value_int
        float value_float
        bool value_bool
    }

    SAMPLE_VALUE_TYPE {
        string(20) code PK
        text description
        enum value_type "either string, int, float or bool"
    }

    ANALYSIS {
        int id PK
        int sample_id FK
        string(20) assay_system
    }

    SPECIATION {
        int analysis_id FK "unique with species_number"
        int id PK
        int species_number "unique with analysis_id"
        string(50) species
        string(20) sub_species
        date analysis_date
        json data
    }

    DRUG_RESISTANCE {
        int analysis_id FK "unique with antibiotic"
        int id PK
        string(20) antibiotic "unique with analysis_id"
        string(1) drug_resistance_result_type_code FK
    }

    DRUG_RESISTANCE_RESULT_TYPE {
        string(1) code PK "SRUF-"
        string(50) description
    }

    RUN ||--o{ SAMPLE : contains
    OWNER ||--o{ SPECIMEN : owns
    SPECIMEN ||--o{ SAMPLE : taken_from
    SAMPLE ||--o{ ANALYSIS : analysed
    ANALYSIS ||--o{ SPECIATION : is
    ANALYSIS ||--o{ DRUG_RESISTANCE : treated_by
    DRUG_RESISTANCE_RESULT_TYPE ||--o{ DRUG_RESISTANCE : is
    SAMPLE ||--o{ SAMPLE_DETAIL: contains
    SAMPLE_VALUE_TYPE ||--o{ SAMPLE_DETAIL: is
```
