import os
import traceback
from cert_generator import generate_certificate

# Sample data
test_data = {
    "countryName": "CN",
    "orgName": "Myweb",
    "ouName": "Myweb Application",
    "cnRoot": "Application",
    "cnSub": "his-erp-lingqu.Mywebcloud.com",
    "password": "changeit",
    "durationDays": 3649
}

# Output directory
output_dir = "test_output"

# Ensure the output directory exists
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

def run_test(keytool_path=None):
    print(f"\nRunning test {'with' if keytool_path else 'without'} keytool path")
    try:
        result = generate_certificate(test_data, output_dir, keytool_path)
        print("Certificate generation successful!")
        print("Generated files:")
        for key, value in result.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error generating certificates: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())

    print("\nFiles in the output directory:")
    for file in os.listdir(output_dir):
        print(file)

# Run test without keytool path
run_test()

# Run test with a dummy keytool path (this will fail to generate the truststore)
run_test("/path/to/keytool")

print("\nScript execution completed.")