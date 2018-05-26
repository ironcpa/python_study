
def binsearch(data, target):
    cur_idx = len(data) // 2
    print('start cur_idx', cur_idx)

    min_idx = 0
    max_idx = len(data) - 1
    while True:
        curr = data[cur_idx]
        if curr == target:
            return curr
        elif curr < target:
            min_idx = cur_idx + 1
        else:
            max_idx = cur_idx - 1

        if min_idx == max_idx:
            return data[min_idx]

        cur_idx = (max_idx + min_idx) // 2

        print(cur_idx)

    return None
