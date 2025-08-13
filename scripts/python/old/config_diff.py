import difflib

def compare_configs(file1, file2, output_file=None):
    try:
        # Read the configuration files
        with open(file1, 'r') as f1, open(file2, 'r') as f2:
            config1 = f1.readlines()
            config2 = f2.readlines()

        # Generate the diff
        diff = difflib.unified_diff(
            config1, config2,
            fromfile=file1,
            tofile=file2,
            lineterm=''
        )

        # Output the diff
        if output_file:
            with open(output_file, 'w') as out_file:
                out_file.writelines(line + '\n' for line in diff)
            print(f"Diff saved to {output_file}")
        else:
            print("\n".join(diff))

    except FileNotFoundError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

# Example usage
base_file = "/mnt/c/Users/devon.d.youngblood/OneDrive - US Army/Desktop/youngblood_netops/dev_configs_backup/"
file1 = f"{base_file}/archive/20250314/FAK-01-RTR.nasw.ds.army.mil.conf"
file2 = f"{base_file}FAK-01-RTR.nasw.ds.army.mil.conf"
output_file = f"{base_file}compare_configs/FAK-01-RTR.txt"  # Set to None if you don't want to save to a file

compare_configs(file1, file2, output_file)
