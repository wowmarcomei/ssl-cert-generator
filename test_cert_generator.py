import os
import traceback
import subprocess
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
        
        # Verify DNS Names in the generated certificate
        verify_dns_names(os.path.join(output_dir, result['sub_crt']))
    except Exception as e:
        print(f"Error generating certificates: {str(e)}")
        print("Traceback:")
        print(traceback.format_exc())

    print("\nFiles in the output directory:")
    for file in os.listdir(output_dir):
        print(file)

def verify_dns_names(cert_path):
    print("\nVerifying DNS Names in the generated certificate:")
    try:
        output = subprocess.check_output(['openssl', 'x509', '-in', cert_path, '-text', '-noout'], 
                                         stderr=subprocess.STDOUT, universal_newlines=True)
        
        # Extract the Subject Alternative Name section
        san_section = output.split("X509v3 Subject Alternative Name:")[1].split("\n\n")[0]
        
        # List of expected DNS Names
        expected_dns_names = [
            "*.datafabric.svc.cluster.local",
            "*.headless-datafabric.datafabric.svc.cluster.local",
            "*.datafabric",
            "*.headless-datafabric.datafabric",
            "*.tenant-eureka.his-iam.svc.cluster.local",
            "*.gaia",
            "*.gaia-log",
            "*.gaia-monitoring",
            "*.his-iam",
            "*.his-observe",
            "*.jalor",
            "*.liveflow",
            "*.livefunction",
            "*.liveconnector",
            "*.monitoring",
            "*.starling",
            "*.flashsync",
            "*.csb",
            "*.edm",
            "*.bds"
        ]
        
        # Check if all expected DNS Names are present
        missing_dns_names = [name for name in expected_dns_names if name not in san_section]
        
        if not missing_dns_names:
            print("All expected DNS Names are present in the certificate.")
        else:
            print("The following DNS Names are missing from the certificate:")
            for name in missing_dns_names:
                print(f"  - {name}")
        
    except subprocess.CalledProcessError as e:
        print(f"Error verifying DNS Names: {e.output}")

# Run test without keytool path
run_test()

# Run test with a dummy keytool path (this will fail to generate the truststore)
run_test("/path/to/keytool")

print("\nScript execution completed.")