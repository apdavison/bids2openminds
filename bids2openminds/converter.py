from warnings import warn
from bids import BIDSLayout, BIDSValidator
from openminds import Collection
import os
import click
from . import main
from . import utility


def convert(input_path, save_output=False, output_path=None, multiple_files=False, include_empty_properties=False):
    if not (os.path.isdir(input_path)):
        raise NotADirectoryError(
            f"The input directory is not valid, you have specified {input_path} which is not a directory."
        )
    # if not(BIDSValidator().is_bids(input_path)):
    #  raise NotADirectoryError(f"The input directory is not valid, you have specified {input_path} which is not a BIDS directory.")
    collection = Collection()
    bids_layout = BIDSLayout(input_path)

    layout_df = bids_layout.to_df()

    subjects_id = bids_layout.get_subjects()

    tasks = bids_layout.get_task()

    # imprting the dataset description file containing some of the
    dataset_description_path = utility.table_filter(layout_df, "description")

    dataset_description = utility.read_json(dataset_description_path.iat[0, 0])

    [subjects_dict, subject_state_dict, subjects_list] = main.create_subjects(
        subjects_id, layout_df, bids_layout, collection)

    [files_list, file_repository] = main.create_file(
        layout_df, input_path, collection)

    dataset_version = main.create_dataset_version(
        bids_layout, dataset_description, layout_df, subjects_list, file_repository, collection)

    dataset = main.create_dataset(
        dataset_description, dataset_version, collection)

    failures = collection.validate(ignore=["required", "value"])
    assert len(failures) == 0

    if save_output:
        if output_path is None:
            if multiple_files:
                output_path = os.path.join(input_path, "openminds")
            else:
                output_path = os.path.join(input_path, "openminds.jsonld")

        collection.save(output_path, individual_files=multiple_files,
                        include_empty_properties=include_empty_properties)
        print(
            f"Conversion was successful, the openMINDS file is in {output_path}")
        return collection
    else:
        print("Conversion was successful")
        return collection


@click.command()
@click.argument("input-path", type=click.Path(file_okay=False, exists=True))
@click.option("-o", "--output-path", default=None, type=click.Path(file_okay=True, writable=True), help="The output path or filename for OpenMINDS file/files.")
@click.option("--single-file", "multiple_files", flag_value=False, default=False, help="Save the entire collection into a single file (default).")
@click.option("--multiple-files", "multiple_files", flag_value=True, help="Each node is saved into a separate file within the specified directory. 'output-path' if specified, must be a directory.")
@click.option("-e", "--include-empty-properties", is_flag=True, default=False, help="Whether to include empty properties in the final file.")
def convert_click(input_path, output_path, multiple_files, include_empty_properties):
    convert(input_path, save_output=True, output_path=output_path,
            multiple_files=multiple_files, include_empty_properties=include_empty_properties)


if __name__ == "__main__":
    input_path = input("Enter the BIDS directory path: ")
    convert(input_path, save_output=True)
