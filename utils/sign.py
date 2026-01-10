import hashlib

def encrypt(param: str) -> str:
    k1 = {
        "0": 0, "1": 1, "2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9,
        "A": 10, "B": 11, "C": 12, "D": 13, "E": 14, "F": 15,
    }
    l1 = [212, 45, 80, 68, 195, 163, 163, 203, 157, 220, 254, 91, 204, 79, 104, 6]
    t = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/="

    md5_hash = hashlib.md5(param.encode('utf-8')).hexdigest().upper()

    t1 = select_chars(md5_hash, [21, 4, 9, 26, 16, 20, 27, 30])
    t3 = select_chars(md5_hash, [18, 11, 3, 2, 1, 7, 6, 25])

    ls2 = []
    for i in range(16):
        x1 = k1[md5_hash[i * 2]]
        x2 = k1[md5_hash[i * 2 + 1]]
        x3 = (x1 * 16 ^ x2) ^ l1[i]
        ls2.append(x3)

    ls3 = []
    for i in range(6):
        if i == 5:
            idx1 = ls2[len(ls2) - 1] >> 2
            idx2 = (ls2[len(ls2) - 1] & 3) << 4
            ls3.append(t[idx1] + t[idx2])
        else:
            x4 = ls2[i * 3] >> 2
            x5 = (ls2[i * 3 + 1] >> 4) ^ ((ls2[i * 3] & 3) << 4)
            x6 = (ls2[i * 3 + 2] >> 6) ^ ((ls2[i * 3 + 1] & 15) << 2)
            x7 = 63 & ls2[i * 3 + 2]
            ls3.append(t[x4] + t[x5] + t[x6] + t[x7])

    t2 = "".join(ls3)
    t2 = t2.replace("/", "").replace("+", "")
    sign = "zzb" + (t1 + t2 + t3).lower()
    return sign

def select_chars(s, indices):
    result = ""
    for index in indices:
        result += s[index]
    return result
