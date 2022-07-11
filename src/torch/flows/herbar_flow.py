from hashlib import md5
import platform
import string
import uuid
from pyzbar.pyzbar import decode
import os
from pathlib import Path
from PIL import Image
from prefect import Flow, Parameter, task
import prefect
from tqdm import tqdm
from datetime import datetime

# File extensions that are scanned and logged
INPUT_FILE_TYPES = ['.jpg', '.jpeg', '.JPG', '.JPEG', '.tif', '.TIF', '.TIFF', '.tiff']
# File type extensions that are logged when filename matches a scanned input file
ARCHIVE_FILE_TYPES = ['.CR2', '.cr2', '.RAW', '.raw', '.NEF', '.nef', '.DNG', '.dng']
# Barcode symbologies accepted, others ignored
ACCEPTED_SYMBOLOGIES = ['CODE39']
# this allows downstream processing to generate a new JPG from the raw file without name conflicts
UNIQUE_QUALIFIERS = list(string.ascii_uppercase) # list of characters added to file names to make unique

@task
def test_task(source:str):
    logger = prefect.context.get('logger')
    logger.info(f'source {source}')

def md5hash(fname):
    # from https://stackoverflow.com/questions/3431825/generating-an-md5-checksum-of-a-file
    # using this approach to ensure larger files can be read into memory
    #hash_md5 = hashlib.md5()
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
                matching_barcodes.append({'type':symbology_type, 'data':data})
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
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
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
    #print('barcodes:', barcodes)
    if default_prefix:
        # return first barcode which matches default prefix
        # not cases sensitive
        for barcode in barcodes:
            if barcode['data'].lower().startswith(default_prefix.lower()):
                return barcode['data']
        # if no match, return first barcode
        return barcodes[0]['data']
    else:
        # return first barcode if no default prefix is specified
        return barcodes[0]['data']

def get_unique_path(path=None, qualifiers=UNIQUE_QUALIFIERS):
    if path.exists():
        #print('path exists:', path)
        # get stem
        stem = path.stem
        suffix = path.suffix
        path_parent = path.parent
        # remove previous qualifier
        if stem[-2:-1]=='_':
            original_stem = stem[:-2]
            #print('original_stem:',original_stem)
            failed_qualifier = stem[-1:]
            #print('failed_qualifier:',failed_qualifier)
            failed_qualifier_index = qualifiers.index(failed_qualifier)
            #print('failed_qualifier_index:',failed_qualifier_index)
            try:
                new_qualifier = qualifiers[failed_qualifier_index+1]
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
        #new_path = Path(new_name)
        new_path = path_parent / new_name
        
        return(get_unique_path(path=new_path, qualifiers=qualifiers))
    else:
        return path

def rename(file_path=None, new_stem=None, no_rename=None):
    parent_path = file_path.parent
    file_extension = file_path.suffix
    new_file_name = new_stem + file_extension
    new_path = parent_path.joinpath(new_file_name)
    # check if current filename is already correct
    if file_path==new_path:
        #print('Paths are same.')
        return{'success': True, 'details': 'file already named correctly', 'new_path': new_path}

    if file_path.exists():
        # generate unique filename for new path
        new_path = get_unique_path(path=new_path)
        # A last check to ensure it is unique
        if new_path.exists():
            print('ALERT - file exists, can not overwrite:', new_path)
            #return False, None
            return{'success': False, 'details': 'file name exists', 'new_path': None}
        else:
            try:
                if no_rename:
                    # don't rename but return True to simulate for logging
                    #return True, file_path
                    return{'success': True, 'details': 'dry-run - file not renamed', 'new_path': file_path}
                else:
                    file_path.rename(new_path)
                    #return True, new_path
                    return{'success': True, 'details': None, 'new_path': new_path}
            except OSError:
                # Possible problem with character in new filename
                print('ALERT - OSError. new_path:', new_path, 'file_path:', file_path )
                #return False, None
                return{'success': False, 'details': 'file not renamed, possible problem character in path', 'new_path': None}
            except Exception as e:
                print("Unexpected error:", e)
                raise

def process(
    file_path=None, new_stem=None,
    uuid=None,
    derived_from_file=None, derived_from_uuid=None,
    barcode=None,
    barcodes=None,
    image_event_id=None,
    prepend_code=None,
    no_rename=None
        ):
    
    #todo remove or try to update values with prefect context(?)
    #global renames_failed, renames_attempted, files_processed
    
    #files_processed += 1 
    # Get file creation time
    file_creation_time = datetime.fromtimestamp(creation_date(file_path))
    # generate MD5 hash
    file_hash = md5hash(file_path)
    datetime_analyzed = datetime.now()

    #rename_status, new_path = rename(file_path=file_path, new_stem=new_stem)
    if prepend_code:
        new_stem = prepend_code + new_stem
    rename_result = rename(file_path=file_path, new_stem=new_stem, no_rename=no_rename)
    #renames_attempted += 1
    status_details = rename_result['details']
    #print('rename_result:', rename_result)
    #if rename_status:
    if rename_result['success']:
        new_path = rename_result['new_path']
        print('rename success', new_path)
    else:
        print('Rename failed:', file_path)
        #renames_failed += 1


@task
def walk(source,verbose,default_prefix,jpeg_rename,prepend_code,no_rename):
    analysis_start_time = datetime.now()
    
    files_analyzed = 0
    files_processed = 0
    renames_attempted = 0
    renames_failed = 0
    missing_barcodes = 0

    path = os.path.realpath(source)
    print('scanning:', path)
    
    for root, dirs, files in os.walk(path):
        for file in tqdm(files, ascii=True, desc='renaming images'):
            files_analyzed += 1
            #print('increment file count:', file)
            file_path_string = os.path.join(root, file)
            file_path = Path(file_path_string)
            if file_path.suffix in INPUT_FILE_TYPES:
                # Get barcodes
                barcodes = get_barcodes(file_path=file_path)
                if barcodes:
                    file_stem = file_path.stem
                    # find archive files matching stem
                    arch_file_path = None

                    for archive_extension in ARCHIVE_FILE_TYPES:
                        potential_arch_file_name = file_stem + archive_extension
                        potential_arch_file_path_string = os.path.join(file_path.parent, potential_arch_file_name)
                        potential_arch_file_path = Path(potential_arch_file_path_string)
                        # test if archive file exists
                        # TODO change filename comparison to be case-sensitive
                        if potential_arch_file_path.exists():
                            arch_file_path = potential_arch_file_path
                            # stop looking for archive file, go with first found
                            break
                    image_event_id = str(uuid.uuid4())
                    arch_file_uuid = str(uuid.uuid4())
                    derivative_file_uuid = str(uuid.uuid4())

                    # assume first barcode
                    # TODO check barcode pattern
                    # Get first barcode value for file name
                    #barcode = barcodes[0]['data']
                    barcode = get_default_barcode(barcodes=barcodes, default_prefix=default_prefix)
                    # Handle multiple barcodes
                    if default_prefix:
                        # if a default prefix is designated, don't capture multiple barcodes
                        multi_string = ''
                    else:
                        if len(barcodes) > 1:
                            #print(barcodes)
                            barcode_values = [b['data'] for b in barcodes]
                            multi_string = '_BARCODES[' + ','.join(barcode_values) + ']'
                            print('ALERT - multiple barcodes found. Using default barcode of', len(barcodes), ':', barcode)
                        else:
                            # only one barcode, use empty multi value
                            multi_string = ''
                    # process JPEG
                    #print('multi_string:', multi_string, type(multi_string))
                    #print('barcode:', barcode, type(barcode))
                    if jpeg_rename:
                        # append JPEG string
                        jpeg_stem = barcode + multi_string  + '_' + jpeg_rename
                    else:
                        jpeg_stem = barcode + multi_string
                        #pass
                    # TODO add derived from uuid
                    archival_stem = barcode + multi_string
                    process(
                        file_path=file_path,
                        new_stem=jpeg_stem,
                        uuid=derivative_file_uuid,
                        derived_from_uuid=arch_file_uuid,
                        derived_from_file=arch_file_path,
                        barcode=barcode,
                        barcodes=barcodes,
                        image_event_id=image_event_id,
                        prepend_code=prepend_code,
                        no_rename=no_rename)
                    if arch_file_path:
                        # process archival
                        process(
                            file_path=arch_file_path,
                            new_stem=archival_stem,
                            uuid=arch_file_uuid,
                            derived_from_uuid=None,
                            derived_from_file=None,
                            barcode=barcode,
                            barcodes=barcodes,
                            image_event_id=image_event_id,
                            prepend_code=prepend_code,
                            no_rename=no_rename)
                    else:
                        print('archival file not found for:', file_path)
                        #files_processed += 1 # not actually processed, but incremented for stats
                        datetime_analyzed = datetime.now()
                else:
                    # no barcodes found
                    missing_barcodes += 1
                    files_processed += 1 # not actually processed, but incremented for stats
                    datetime_analyzed = datetime.now()
                  
    
    analysis_end_time = datetime.now()

    print('Started:', analysis_start_time)
    print('Completed:', analysis_end_time)
    # files_analyzed is the total number of files encountered in directory which is scanned
    print('Files analyzed:', files_analyzed)
    # files_processed is number of files which match the expected extensions for image files
    print('Files processed:', files_processed)
    print('Renames attempted:', renames_attempted)
    if renames_attempted > 0:
        print('Renames failed:', renames_failed, '({:.1%})'.format(renames_failed/renames_attempted))
        print('Missing barcodes:', missing_barcodes, '({:.1%})'.format(missing_barcodes/files_analyzed))
    else:
        print('Input directory not found or contains no images matching search pattern.')
    print('Duration:', analysis_end_time - analysis_start_time)
    if files_analyzed > 0:
        print('Time per file:', (analysis_end_time - analysis_start_time) / files_analyzed)


with Flow("herbar-flow") as herbar_flow:
    #todo connect to database and create log table
    
    # Start scanning input directory
    #todo check parallel option to walk
    walk(source=Parameter("path", required=False),
        verbose = Parameter("verbose"),
        default_prefix = Parameter("default_prefix"),
        jpeg_rename = Parameter("jpeg_rename"),
        prepend_code = Parameter("code"),
        no_rename = Parameter("no_rename"))
    