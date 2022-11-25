import os
import platform
import string
import uuid
from hashlib import md5
from pathlib import Path

from PIL import Image
from prefect import task, get_run_logger
from prefect.orion.schemas.states import Failed
from pyzbar.pyzbar import decode

from torch.collections.specimens import Specimen
from torch.prefect_flows.tasks.save_specimen import save_specimen

# File extensions that are scanned and logged
INPUT_FILE_TYPES = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.tif', '.TIF', '.TIFF', '.tiff']
# File type extensions that are logged when filename matches a scanned input file
ARCHIVE_FILE_TYPES = ['.CR2', '.cr2', '.RAW', '.raw', '.NEF', '.nef', '.DNG', '.dng']
# Barcode symbologies accepted, others ignored
ACCEPTED_SYMBOLOGIES = ['CODE39']
# this allows downstream processing to generate a new JPG from the raw file without name conflicts
UNIQUE_QUALIFIERS = list(string.ascii_uppercase)  # list of characters added to file names to make unique


@task
def test_task(source: str):
    logger = get_run_logger()
    logger.info(f'source {source}')


def md5hash(fname):
    # from https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    # using this approach to ensure larger files can be read into memory
    # hash_md5 = hashlib.md5()
    hash_md5 = md5()
    try:
        with open(fname, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except OSError as e:
        print('ERROR:', e)
        return None


def get_barcodes(file_path=None):
    # read barcodes from JPG
    barcodes = decode(Image.open(file_path))
    matching_barcodes = []
    if barcodes:
        for barcode in barcodes:
            # Keep only codes that match accepted symbologies
            if str(barcode.type) in ACCEPTED_SYMBOLOGIES:
                symbology_type = str(barcode.type)
                data = barcode.data.decode('UTF-8')
                matching_barcodes.append({'type': symbology_type, 'data': data})
                print(symbology_type, data)
        return matching_barcodes
    else:
        print('No barcodes found:', file_path)
        return None


def creation_date(path_to_file):
    # From https://stackoverflow.com/a/39501288
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See https://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(path_to_file)
    else:
        stat = os.stat(path_to_file)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime


def get_default_barcode(barcodes=None, default_prefix=None):
    # print('barcodes:', barcodes)
    if default_prefix:
        # return first barcode which matches default prefix
        # not cases sensitive
        for barcode in barcodes:
            if barcode['data'].lower().startswith(default_prefix.lower()):
                return barcode['data']
        # if no match, return first barcode        return barcodes[0]['data']
    else:
        # return first barcode if no default prefix is specified
        return barcodes[0]['data']


def get_unique_path(path=None, qualifiers=None):
    if qualifiers is None:
        qualifiers = UNIQUE_QUALIFIERS

    if path.exists():
        # print('path exists:', path)
        # get stem
        stem = path.stem
        suffix = path.suffix
        path_parent = path.parent
        # remove previous qualifier
        if stem[-2:-1] == '_':
            original_stem = stem[:-2]
            # print('original_stem:',original_stem)
            failed_qualifier = stem[-1:]
            # print('failed_qualifier:',failed_qualifier)
            failed_qualifier_index = qualifiers.index(failed_qualifier)
            # print('failed_qualifier_index:',failed_qualifier_index)
            try:
                new_qualifier = qualifiers[failed_qualifier_index + 1]
            except IndexError:
                # ran out of qualifiers
                # using UUID instead
                new_qualifier = str(uuid.uuid4())
        else:
            # No previous qualifier established
            original_stem = stem
            new_qualifier = qualifiers[0]

        # add unique to stem
        new_name = original_stem + '_' + new_qualifier + suffix
        # new_path = Path(new_name)
        new_path = path_parent / new_name

        return get_unique_path(path=new_path, qualifiers=qualifiers)
    else:
        return path


def rename(file_path=None, new_stem=None, no_rename=None):
    parent_path = file_path.parent
    file_extension = file_path.suffix
    new_file_name = new_stem + file_extension
    new_path = parent_path.joinpath(new_file_name)
    # check if current filename is already correct
    if file_path == new_path:
        # print('Paths are same.')
        return {'success': True, 'details': 'file already named correctly', 'new_path': new_path}

    if file_path.exists():
        # generate unique filename for new path
        new_path = get_unique_path(path=new_path)
        # A last check to ensure it is unique
        if new_path.exists():
            print('ALERT - file exists, can not overwrite:', new_path)
            # return False, None
            return {'success': False, 'details': 'file name exists', 'new_path': None}
        else:
            try:
                if no_rename:
                    # don't rename but return True to simulate for logging
                    # return True, file_path
                    return {'success': True, 'details': 'dry-run - file not renamed', 'new_path': file_path}
                else:
                    file_path.rename(new_path)
                    # return True, new_path
                    return {'success': True, 'details': None, 'new_path': new_path}
            except OSError:
                # Possible problem with character in new filename
                print('ALERT - OSError. new_path:', new_path, 'file_path:', file_path)
                # return False, None
                return {'success': False, 'details': 'file not renamed, possible problem character in path',
                        'new_path': None}
            except Exception as e:
                print("Unexpected error:", e)
                raise


def process(file_path=None, new_stem=None, prepend_code=None, no_rename=None):
    if prepend_code:
        new_stem = prepend_code + new_stem
    rename_result = rename(file_path=file_path, new_stem=new_stem, no_rename=no_rename)

    if rename_result['success']:
        new_path = rename_result['new_path']

        print('rename success', new_path)

        return new_path
    else:
        print('Rename failed:', file_path)
        ValueError("Rename failed:" + file_path)


@task
def herbar(specimen: Specimen, app_config, flow_config):
    try:
        # file_path_string = os.path.join(root, specimen.upload_path)
        file_path = Path(specimen.upload_path)

        if file_path.suffix in INPUT_FILE_TYPES:
            # Get barcodes
            barcodes = get_barcodes(file_path)

            if barcodes:
                print('barcodes')
                specimen.barcode = get_default_barcode(barcodes)
                save_specimen(specimen, app_config)

                # find archive files matching stem

                # todo migrate config to db
                default_prefix = flow_config["DEFAULT_PREFIX"]
                jpeg_rename = flow_config["JPEG_RENAME"]

                # assume first barcode
                # TODO check barcode pattern
                # Get first barcode value for file name
                # barcode = barcodes[0]['data']
                barcode = get_default_barcode(barcodes=barcodes, default_prefix=default_prefix)
                # Handle multiple barcodes
                if default_prefix:
                    # if a default prefix is designated, don't capture multiple barcodes
                    multi_string = ''
                else:
                    if len(barcodes) > 1:
                        # print(barcodes)
                        barcode_values = [b['data'] for b in barcodes]
                        multi_string = '_BARCODES[' + ','.join(barcode_values) + ']'
                        print('ALERT - multiple barcodes found. Using default barcode of', len(barcodes), ':', barcode)
                    else:
                        # only one barcode, use empty multi value
                        multi_string = ''
                # process JPEG
                # print('multi_string:', multi_string, type(multi_string))
                # print('barcode:', barcode, type(barcode))
                if jpeg_rename:
                    # append JPEG string
                    jpeg_stem = barcode + multi_string + '_' + jpeg_rename
                else:
                    jpeg_stem = barcode + multi_string
                    # pass
                # TODO add derived from uuid
                new_path = process(file_path=file_path, new_stem=jpeg_stem)

                old_path_name = Path(specimen.upload_path).name
                specimen.upload_path = specimen.upload_path.replace(old_path_name, new_path.name)

                save_specimen(specimen, app_config)
            else:
                save_specimen(specimen, app_config, flow_run_state='Failed', failed_task='herbar')
                return Failed(message="No barcode found")
    except Exception as e:
        save_specimen(specimen, app_config, flow_run_state='Failed', failed_task='herbar')
        return Failed(message=f"Error processing herbar task: {e}")
