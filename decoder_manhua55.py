import logging
from urllib import parse
import base64
from Crypto.Cipher import AES

_version = "jsjiami.com.v7"

array_list = [
    'W6NcJ8oVAG',
    'W63cJIf9W7a',
    'W4r9W4PHW5hcOCoGDxO',
    'W4ZcMSo7isa',
    'WQ86WOxcO8kUhqS',
    'gCoeyc9un8kNWOasWQf1WRpdQq',
    'brVdLmoTWP4',
    'WOddJmk/W7tcPmkX',
    'WO/dICk8zxddO8keBKddUmkCW5a',
    't8k+cCogzCooDrvndY7dTCoy',
    'W745WPLkd8oEmCkVp0G',
    'W5hcN8kzDmovoJ/dKa',
    'lSo7vqFdV2/dNCoSWR/cOwldQrC',
    'ELhdO8oAW59KhCktp8k0WPJcGq',
    'nmocru82kmodvmkfW5zGWOKZa8kRsW',
    'ySonDG',
    'ACkKW5xcOKldQCkCAmo4',
    'vSoqWOG7WOZdH34n',
    'jKZdPCohjmk8W7XE',
    'W5tcT3m',
    'Fmk5bfdcVdW',
    'W6NdUCkLtmk7WOVdQMZdTSoq',
    'W5RcLYFdSKWqq8kbW5FcJMJcUa',
    'WOtcN1VcOXtcQSoTyCkWxSkRW4a1',
    'WOBdKmk5',
    'W4BcTMldG8ok',
    'W6hcMmoykLC',
    'W6JcUCowWONdP24pW5zGq8oUqmoI',
    'ESk7W6jYWOJdHfO',
    'WQZdN2C4WQiqWPZcOJRdUSofWOVcGq',
    'W5/cJIbRWQms',
    'WQfOW4T2W7BcNCou',
    'mmo8W7Prp8opW5C/',
    'tmoulG',
    'tSkCnG',
    'W5lcKSoy',
    'k8k3ve3dUIxdKSodW7tcMIJdNuXvWPRcHCo3',
    'W4/cJ8o7oYVcT8kerNa',
    'W7BcNSoc',
    'A8oiW6G',
    'yaFcSaS',
    'W4PHsmoBkG'
]
class decoder_manhua55:
    def __init__(self):
        self.array_list = array_list
        self.param_dist = {}
        pass

    def decoder_val(self, s_str:str):
        char_str = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/="
        out_str = ''
        # prarm_init
        _str_l1 = ''
        _str_l2 = ''
        _val_l1 = 0
        _val_l2 = 0
        for n_index in range(0, len(s_str)):
            n_find_index = char_str.find(s_str[n_index])
            if(~n_find_index != 0):
                if(_val_l1 % 0x4):
                    _val_l2 = _val_l2 * 0x40 + n_find_index
                else:
                    _val_l2 = n_find_index
                _val_l1 += 1
                if ((_val_l1 - 1) % 0x4 != 0):
                    val = 0xff & (_val_l2 >> ((-0x2 * (_val_l1)) & 0x6))

                    _str_l1 += chr(val)
        # logging.debug(f'_str_l1 {_str_l1}')
        for n_index in range(len(_str_l1)):
            _str_l2 += '%' + f"{ord(_str_l1[n_index]):02x}"
            pass
        # logging.debug(f'_str_l2 {_str_l2}')
        val = parse.unquote(_str_l2)
        return val

    def _decode(self, n_num:int, s_str:str):
        n_num = n_num - 0x144
        val = self.array_list[n_num]
        # logging.debug(f'val {val}')
        arr_list = []
        _str_l3 = ''
        _val_l3 = 0
        if(self.param_dist.get('ShYogl') == None):
            # logging.debug('ShYogl key not found in')
            _0x89d56d = self.decoder_val(val)
            # logging.debug(f'_0x89d56d:{_0x89d56d}')
            # 数组赋值
            for n_index in range(0x100):
                arr_list.append(n_index)
            for n_index in range(0x100):
                _val_l3 = (_val_l3 + arr_list[n_index] + ord(s_str[n_index % len(s_str)])) % 0x100
                n_tmp = arr_list[n_index]
                arr_list[n_index] = arr_list[_val_l3]
                arr_list[_val_l3] = n_tmp
            _val_l3 = 0
            n_index_tmp = 0
            for n_index in range(len(_0x89d56d)):
                n_index_tmp = (n_index_tmp + 1) % 0x100
                _val_l3 = (_val_l3 + arr_list[n_index_tmp]) % 0x100
                n_tmp = arr_list[n_index_tmp]
                arr_list[n_index_tmp] = arr_list[_val_l3]
                arr_list[_val_l3] = n_tmp
                val = ord(_0x89d56d[n_index]) ^ arr_list[ (arr_list[n_index_tmp] + arr_list[_val_l3]) % 0x100 ]
                _str_l3 += chr(val)
            # logging.debug(_str_l3)
            return _str_l3

    def decryptParams(self, s_prarm:str):
        decoder_str = base64.b64decode(s_prarm)
        self.base64_decoder = decoder_str
        self.s_iv = self.base64_decoder[0:16]

        self.s_pram_data = self.base64_decoder[16:]
        self.aes_k = self._decode(0x152, ")X69")
        key_bytes = bytes(self.aes_k, encoding='utf-8')
        cipher = AES.new(key=key_bytes, mode=AES.MODE_CBC, IV=self.s_iv)
        aes_encode_bytes = cipher.decrypt(self.s_pram_data)
        r = str(aes_encode_bytes, encoding='utf-8')
        r = ''.join(reversed(r))
        n_index = r.find('}')
        if n_index != -1:
            r = r[n_index:]
        r = ''.join(reversed(r))
        return r

if __name__ == '__main__':
    pass