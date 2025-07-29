import os
from ciscoconfparse2 import Diff

def compare_configs(file1, file2):
    diff_lines = Diff(file1, file2).get_diff()
    print(os.linesep.join(diff_lines))



def main():
    base_file = "/mnt/c/Users/devon.d.youngblood/OneDrive - US Army/Desktop/youngblood_netops/dev_configs_backup/"
    # file1 = f"{base_file}/archive/20250314/FAK-01-RTR.nasw.ds.army.mil.conf"
    file1 = f"{base_file}FAK-07-RTR.nasw.ds.army.mil.conf"
    file2 = f"{base_file}FAK-01-RTR.nasw.ds.army.mil.conf"
    # output_file = f"{base_file}compare_configs/FAK-01-RTR.txt"  # Set to None if you don't want to save to a file

    compare_configs(file1, file2)

if __name__ == "__main__":
    main()