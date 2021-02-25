### OT based multiplication Protocol
# Bob and Alice generate random values
#Alice sends bit 0 or 1 to function third_party_to_calculate_mutiplication to caclulate for the sum
import random

max_size = 2**(32+1)


class Alice:
    x = 0
    sum = 0

    def __init__(self):
        self.x = random.randint(1, 2**16)
        print('Alice  share of value is ' + str(self.x))

    def bit_at_position(self ,i):
        length = self.x.bit_length()
        if i>=length:
            return -1
        return 2**i & self.x

    def add_number(self, value):
        self.sum = (value + self.sum) % max_size

    def return_sum(self):
        return self.sum


class Bob:
    y = 0
    sum = 0

    def __init__(self):
        self.y = random.randint(1, 2**16)
        print('Bob  share of value is ' + str(self.y))

    def two_random_value(self, i):
        rand_value1 = random.randint(0, max_size-1)
        rand_value2 = (self.y * (2 ** i) - rand_value1) % max_size
        value3 = (- rand_value1) %max_size
        self.sum =(rand_value1 +self.sum)%max_size
        return value3, rand_value2

    def return_sum(self):
        return self.sum


def third_party_to_calculate_mutiplication(alice, bob):
    i = 0
    while True:
        next_bit = alice.bit_at_position(i)
        if next_bit == -1:
            break
        rand_value1, rand_value2 = bob.two_random_value(i)
        if next_bit == 0:
            alice.add_number(rand_value1)
        else:
            alice.add_number(rand_value2)
        i += 1


alice = Alice()
bob = Bob()
third_party_to_calculate_mutiplication(alice, bob)
alice_sum = alice.return_sum()
bob_sum = bob.return_sum()
sum = (bob_sum + alice_sum)%max_size
print('Multiplication of Alice and Bob Value is ' + str(sum))
