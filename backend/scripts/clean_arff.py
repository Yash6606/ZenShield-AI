import os

def clean_arff(input_path, output_path):
    print(f"Cleaning ARFF file: {input_path}")
    with open(input_path, 'r') as f:
        lines = f.readlines()
    
    with open(output_path, 'w') as f:
        for line in lines:
            if line.startswith('@attribute'):
                # Strip spaces around commas and curly braces in attribute definitions
                # Example: {'tcp','udp', 'icmp'} -> {'tcp','udp','icmp'}
                parts = line.split('{')
                if len(parts) > 1:
                    attr_header = parts[0]
                    attr_values = parts[1].replace(' ', '').replace("'", "")
                    # Re-add single quotes if needed, but scipy/arff usually handle them
                    # Let's try simple comma-separated
                    clean_line = f"{attr_header}{{{attr_values}"
                    f.write(clean_line)
                else:
                    f.write(line)
            else:
                f.write(line)

if __name__ == "__main__":
    src = "c:\\Users\\SHAH VENIL\\OneDrive\\Desktop\\AMD\\data\\KDDTest+.arff"
    dst = "c:\\Users\\SHAH VENIL\\OneDrive\\Desktop\\AMD\\data\\KDDTest+_clean.arff"
    clean_arff(src, dst)
    print("Cleaned ARFF saved.")
