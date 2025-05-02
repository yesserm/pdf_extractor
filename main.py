import argparse
import association

def main():
    parser = argparse.ArgumentParser(description="PDF Extractor Tool")
    parser.add_argument('-i', '--input', required=True, help="Path to the input PDF file")
    parser.add_argument('-o', '--output', required=False, help="Path to the output file")
    parser.add_argument('-p', '--pages', required=False, help="Pages to extract (e.g., 1,2,3 or 1-3)")
    
    args = parser.parse_args()
    if args.input:
        document_path = args.input
        processed_document = association.procesar_documento(document_path)
        print(f"Processed document: {processed_document}")
    
    if args.output:
        print(f"Output file: {args.output}")
    if args.pages:
        print(f"Pages to extract: {args.pages}")

if __name__ == "__main__":
    main()