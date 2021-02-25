#!/usr/bin/env python3

# Copyright (c) Facebook, Inc. and its affiliates.
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.
from hashlib import sha256

import unittest
from multiprocess_test_case import MultiProcessTestCase
import random
from hashlib import sha256
from typing import List
import crypten.communicator as comm

class BaseOT:
    """
    hardcoded public parameter
    log2(__prime) > 128
    __generator is a primitive root of __prime
    """

    __prime = 631276824160446938136046282957027762913
    __generator = 3
    __inverse__generator = pow(__generator, (__prime - 2), __prime)

    @staticmethod
    def string_xor(s1, s2):
        """
        XOR of two strings
        """
        return "".join(chr(ord(a) ^ ord(b)) for a, b in zip(s1, s2))

    def __init__(self, partner_rank):
        self.partner_rank = partner_rank
        return

    def send(self, message0s: List[str], message1s: List[str]):
        """
        sender's input is two message lists
        """
        # print(str((self.partner_rank + 1) % 2) + ' send message')
        # print('partner rank'+ self.partner_rank)
        # print(str((self.partner_rank + 1) % 2) + str(message0s))
        print('Input strings for message 1')
        for i in message1s:
            print(i)
        print('Input strings for message 0')
        for i in message0s:
            print(i)

        if len(message0s) != len(message1s):
            raise ("inconsistent input l!")

        alphas = []
        masks_for_message1s = []
        for _i in range(len(message1s)):
            # pick a random element from Z_p
            alpha = random.randint(0, self.__prime - 1)
            alphas.append(alpha)

            # g^\alpha
            mask_for_message1 = pow(self.__generator, alpha, self.__prime)
            masks_for_message1s.append(mask_for_message1)
        # mask or messages
        # send mask_for_message1
        for i in range(len(message1s)):
            # print(str((self.partner_rank + 1) % 2) + 'masks_for_message1s[0]' + str(masks_for_message1s[0]))
            comm.get().send_obj(masks_for_message1s[i], self.partner_rank)

        # compute (g^\alpha)^-\alpha when waiting for response
        # (g^-1)^(\alpha^2) = (g^-1)^(\alpha^2 mod (p-1))
        dividers = []
        for i in range(len(message1s)):
            divider = pow(
                self.__inverse__generator,
                alphas[i] * alphas[i] % (self.__prime - 1),
                self.__prime,
            )
            dividers.append(divider)

        masks_for_choices = []

        # recv mask_for_choice
        for _i in range(len(message1s)):
            mask_for_choice = comm.get().recv_obj(self.partner_rank)
            # print(str((self.partner_rank + 1) % 2) + 'mask_for_choice' + str(mask_for_choice))
            masks_for_choices.append(mask_for_choice)

        for i in range(len(message1s)):
            masks_for_choices[i] = pow(masks_for_choices[i], alphas[i], self.__prime)

            # hash
            # print('hashh')
            # print(masks_for_choices[i])
            # print(str((self.partner_rank + 1) % 2) + 'masks_for_choices[0]' + str(masks_for_choices[0]))

            pad0 = sha256(str(masks_for_choices[i]).encode("utf-8")).hexdigest()
            # print(str((self.partner_rank + 1) % 2) + 'pad0' + pad0)
            pad1 = sha256(
                str(masks_for_choices[i] * dividers[i] % self.__prime).encode("utf-8")
            ).hexdigest()
            # print(pad0)
            if len(pad0) < len(message0s[i]):
                raise (str(i) + "-th message0 is too long")
            # print(pad1)
            if len(pad1) < len(message1s[i]):
                raise (str(i) + "-th message1 is too long")
            # encrypt with one time pad
            message0_enc = self.string_xor(pad0, message0s[i])
            message1_enc = self.string_xor(pad1, message1s[i])
            # send message0, message1
            # print(str((self.partner_rank + 1) % 2) + 'message0_enc' + message0_enc)
            # print(str((self.partner_rank + 1) % 2) + 'message1_enc' + message1_enc)

            comm.get().send_obj(message0_enc, self.partner_rank)
            comm.get().send_obj(message1_enc, self.partner_rank)

    def receive(self, choices: List[bool]):
        """
        choice:
            false: pick message0
            true: pick message1
        """

        # print(str((self.partner_rank + 1) % 2) + ' recieve message')
        # print('partner rank' + self.partner_rank)
        # print(str((self.partner_rank + 1) % 2) + str(choices))

        print('Choices of bit entered')
        for i in choices:
            print(i)

        betas = []
        masks_for_choices = []
        for _i in range(len(choices)):
            # pick a random element from Z_p
            beta = random.randint(0, self.__prime - 1)
            mask_for_choice = pow(self.__generator, beta, self.__prime)
            betas.append(beta)
            masks_for_choices.append(mask_for_choice)

        masks_for_message1s = []
        for i in range(len(choices)):
            # recv mask_for_message1
            mask_for_message1 = comm.get().recv_obj(self.partner_rank)
            # print(str((self.partner_rank + 1) % 2) + 'mask_for_message1' + str(mask_for_message1))

            masks_for_message1s.append(mask_for_message1)
            if choices[i]:
                masks_for_choices[i] = (
                                               masks_for_choices[i] * mask_for_message1
                                       ) % self.__prime

        for i in range(len(choices)):
            # send mask_for_choice
            # print(str((self.partner_rank + 1) % 2) + 'masks_for_choices[i]' + str(masks_for_choices[i]))

            comm.get().send_obj(masks_for_choices[i], self.partner_rank)

        keys = []
        for i in range(len(choices)):
            # compute the hash when waiting for response
            key = sha256(
                str(pow(masks_for_message1s[i], betas[i], self.__prime)).encode("utf-8")
            ).hexdigest()
            keys.append(key)

        rst = []
        # print(str((self.partner_rank + 1) % 2) + 'masks_for_message1s' + str(pow(masks_for_message1s[0],betas[0],self.__prime)))
        for i in range(len(choices)):
            # recv message0, message1
            message0_enc = comm.get().recv_obj(self.partner_rank)
            message1_enc = comm.get().recv_obj(self.partner_rank)
            # print(str((self.partner_rank + 1) % 2) + 'message0_enc' + message0_enc)
            # print(str((self.partner_rank + 1) % 2) + 'message1_enc' + message1_enc)
            # print(str((self.partner_rank + 1) % 2) + 'keys[0]' + str(keys[0]))
            if choices[i]:
                rst.append(self.string_xor(keys[i], message1_enc))
            else:
                rst.append(self.string_xor(keys[i], message0_enc))
        # print(str((self.partner_rank + 1) % 2) + str(rst))
        print("Output String based on bit entered where choice is ")
        print(rst)
        return rst


class TestObliviousTransfer(MultiProcessTestCase):
    def test_BaseOT(self):
        ot = BaseOT((self.rank + 1) % self.world_size)
        if self.rank == 0:
            # play the role of sender first
            msg0s = ["abc"]
            msg1s = ["xyz"]
            ot.send(msg0s, msg1s)
        else:
            # play the role of receiver first with choice bit [1, 0]
            choices = [1]
            msgcs = ot.receive(choices)
            self.assertEqual(msgcs, ['xyz'])


if __name__ == "__main__":
    unittest.main()
