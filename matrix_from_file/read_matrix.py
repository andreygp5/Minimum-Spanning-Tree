def read_matrix_from_file(path, isWeight=False):
    ''' This function reads matrix from file with txt_handler() function
    and handles all errors with error_handler() function.
    '''

    matrix = []
    nX_count = 0
    try:
        txt_handler(path, matrix)
    except ValueError:
        return matrix, nX_count, "Невалидный файл"
    error = error_handler(matrix)
    nX_count = get_nX_count(matrix)
    return nX_count, matrix, error

def error_handler(matrix):
    ''' This function handles all errors, which
    can occur while reading the matrix.
    '''

    error = ''
    if check_symmetry(matrix) is False:
        error += '\nНенулевая главная диагональ'
    if check_amount_vertex(matrix) is False:
        error += '\nКол-во вершин графа должно быть в диапазоне от 1 до 100'
    return error

def txt_handler(path, matrix):
    ''' This function reads matrix from txt file.'''

    with open(path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            row = []
            line_without_n_end = line.rstrip()
            row_ = line_without_n_end.split(' ')
            for el in row_:
                try:
                    row.append(int(el))
                except ValueError:
                    raise
            matrix.append(row)

def check_symmetry(matrix):
    ''' This function checks symmetry in matrix(null main diagonal). '''

    i = 0
    for row in matrix:
        if len(row) != len(matrix):
            return False
        if row[i] != 0:
            return False
        i += 1
    return True

def check_orgraph(matrix):
    ''' This function says is it or graph or not. '''

    for element in range(len(matrix)):
        row = matrix[element]
        col = []
        for row_ in matrix:
            col.append(row_[element])
        if row != col:
            return True
    return False


def check_amount_vertex(matrix):
    ''' This function checks for necessary amount of vertexes in matrix. '''

    return bool(len(matrix)>0 and len(matrix)<101)

def get_nX_count(matrix):
    ''' This function returns amount of vertexes in matrix. '''

    return len(matrix[0])