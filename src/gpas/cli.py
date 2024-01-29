import defopt # type: ignore

def import_sample_data() -> None:
    print("Importing sample data...")

def main() -> None:
    defopt.run(
        {
            "upload_samples": import_sample_data,
        }
    )
    
if __name__ == '__main__':
    main()