import json
import os


def concatenate_json_files(file_paths, output_folder, output_file):
    concatenated_data = []

    # Read data from each input file
    for file_path in file_paths:
        with open(file_path, 'r') as file:
            data = json.load(file)
            concatenated_data.extend(data)

    # Create the output folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Construct the full path for the output file
    output_path = os.path.join(output_folder, output_file)

    # Write the concatenated data to the output file
    with open(output_path, 'w') as output:
        json.dump(concatenated_data, output, indent=2)

    print(f"JSON files concatenated and saved to {output_path}")


if __name__ == "__main__":

    # Replace the path
    path = 'data'

    # List of corrected file names
    file_names = ['dumpEntitiesGeneVariety.json',
                  'dumpEntitiesNCBITaxon.json', 'dumpEntitiesWTO.json']

    # Constructing absolute paths using os.path.join()
    input_files = [os.path.join(path, file_name) for file_name in file_names]

    # Specify the destination folder and the output file name
    destination_folder = 'data'
    output_file = 'dumpEntities.json'

    concatenate_json_files(input_files, destination_folder, output_file)
