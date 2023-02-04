__app_name__ = 'functional flows'
__version__ = '0.1.0'

(
    SUCCESS,
    FILE_ERROR,
    DATA_ERROR,
) = range(3)

ERRORS = { 
    FILE_ERROR: 'Data file not found.',
    DATA_ERROR: 'Data in file caused an error.'
}