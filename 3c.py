#from numpy.linalg import inv
from ffield import FField, FFieldElement
import numpy as np
import requests
import json

# computes determinant of 2*2 matrix
def det2(A):
    first = A[0][0].__mul__(A[1][1])
    second = A[0][1].__mul__(A[1][0])
    result = first.__sub__(second)
    return result

# computes determinant of 3*3 matrix
def det3(A):

    first_det_2 = det2([[A[1][1], A[1][2]], [A[2][1], A[2][2]]])
    second_det_2 = det2([[A[0][1], A[0][2]], [A[2][1], A[2][2]]])
    third_det_2 = det2([[A[0][1], A[0][2]], [A[1][1], A[1][2]]])

    first_element = A[0][0].__mul__(first_det_2)
    second_element = A[1][0].__mul__(second_det_2)
    third_element = A[2][0].__mul__(third_det_2)

    result =  first_element.__sub__(second_element).__add__(third_element)
    return result

# transpose matrix
def transpose(A):
    result = [[0 for j in range(len(A[0]))] for i in range(len(A))]
    for i in range(len(A)):
        for j in range(len(A[0])):
            result[j][i] = A[i][j]
    return result

# find minors of matrix
def find_minor_matrix(A):

    result = [[0 for j in range(len(A[0]))] for i in range(len(A))]

    for i in range(len(A)):
        for j in range(len(A[0])):
            sub_matrix = [[A[x][y] for y in range(len(A[0])) if y != j ] for x in range(len(A)) if x != i]
            sub_det = det2(sub_matrix)
            result[i][j] = sub_det
    return result

# add alternating signs
def change_sign(A):

    result = [[0 for j in range(len(A[0]))] for i in range(len(A))]
    for i in range(len(A)):
        for j in range(len(A[0])):

            #add positive sign
            if (i + j) % 2 == 0:
                result[i][j] = A[i][j]

            #add negative sign
            else:
                element = A[i][j]
                result[i][j] = FFieldElement(element.ffield, -element.value)
    return result


# calculates the inverse of matrix
def invert_matrix(A):

    determinant = det3(A)
    transpose_A = transpose(A)
    minor_A = find_minor_matrix(transpose_A)
    flipped_A = change_sign(minor_A)

    result = [[0 for j in range(len(A[0]))] for i in range(len(A))]
    for i in range(len(A)):
        for j in range(len(A[0])):
            element = flipped_A[i][j]
            result[i][j] = element.__div__(determinant)
    return result


def multiply_element(element, times):
    new_element = FFieldElement(element.ffield, element.value)
    for i in range(times):
        new_element = new_element.__mul__(new_element)
    return new_element

def dot_multiply(A, b):

    result = [0 for i in range(len(b))]

    for i in range(len(A)):
        total_sum = FFieldElement(b[i].ffield, 0)
        for j in range(len(b)):
            element = A[i][j]
            total_sum = total_sum.__add__(element.__mul__(b[j]))

        result[i] = total_sum
    return result



if __name__ == '__main__':


    #response = requests.get("http://127.0.0.1:3000/")
    response = requests.get("http://6857blakley.csail.mit.edu/")
    content =  response.content.decode()
    data =  json.loads(content)
    shares = data[1]


    ffield = FField(11953696440786470837)

    print "This is the ID: ", data[0]
    print "These are the shares: ", shares


    shared_a = []
    shared_b = []
    for i in range(len(shares)):
        shared_a.append(FFieldElement(ffield, shares[i][0]))
        shared_b.append(FFieldElement(ffield, shares[i][1]))

    #compute A matrix
    A = [[0 for j in range(len(shares))] for i in range(len(shares))]

    for i in range(len(shares)):
        for j in range(len(shares)):
            element = multiply_element(shared_a[i], j)
            A[i][j] = element


    #inverse of A
    A_inverse = invert_matrix(A)
    result = dot_multiply(A_inverse, shared_b)

    #check if solution is correct
    calculated_b = dot_multiply(A, result)

    print "Original b: ", shared_b
    print "Calculated b: ", calculated_b

    for i in range(len(result)):
        assert shared_b[i].value == calculated_b[i].value

    print "Secret: ", result[0]
