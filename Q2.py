import crypten
from multiprocess_test_case import get_random_test_tensor


def test_sum():
    input_values = []
    rand_values = []
    encrypted_value = []
    rand_values_sum = 0
    encrypted_value_sum = 0
    for i in range(10):  # creating  values of 10 Party
        input_values.append(get_random_test_tensor(size=(1, 1), is_float=False))
        print('Value of party ' + str(i + 1) + ' ' + str(input_values[i].numpy()[0]))

    for i in range(10):             # 10 parties create another random values for encryption
        rand_values.append(get_random_test_tensor(size=(1, 1), is_float=False))

    for i in range(10):             # 10 parties encrypt their actual value with actual value - some_random_value
        encrypted_value.append(input_values[i] - rand_values[i])

    # Then they give these random value list to one of the party and that party computed summ of all random value
    # They give encrypted_value list to another party which computes sum of all encrypted values
    # Then these both sum values are transfer to server to compute summ of all values
    for i in range(10):
        rand_values_sum += rand_values[i].numpy()[0][0]
        encrypted_value_sum += encrypted_value[i].numpy()[0][0]

    print('Print random value sum ' + str(rand_values_sum))
    print('Print encrypted value sum ' + str(encrypted_value_sum))
    sum = rand_values_sum + encrypted_value_sum
    return sum


crypten.init()
sum = test_sum()

print('sum of values of adding all the values after secure addition ' + str(sum))
