import sys
import os

patch_code = {0x108947 : b'\x83\xFE\x3C\x74\x3E\xEB\x62',
              0x108984 : b'\x01\x00',
              0x108989 : b'\xBC'
              }


def patcher(binFileName):

    if not os.path.isfile(binFileName):
        print("Patcher: File \'{0}\' not found.".format(binFileName))
        return

    with open(binFileName, 'r+b') as file:
        for rawaddr in patch_code:
            file.seek(rawaddr, 0)
            file.write(patch_code[rawaddr])

            print('[{0}] write: \'{1}\''.format(rawaddr, patch_code[rawaddr]))

        file.close()

        print("patched.")


if __name__ == '__main__':
    binFileName = 'qemu-x86_64'

    if len(sys.argv) >= 2:
        binFileName = sys.argv[1]

    patcher(binFileName)