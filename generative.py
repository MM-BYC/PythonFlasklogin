# from cgi import test


def compare_lists(list1, list2):
    for num1, num2 in zip(list1, list2):
        if num1 != num2:
            return False
    return True

    # Tests that the function returns False when comparing two lists with elements in different order

def test_different_order():
    list1 = [2, 3, 1]
    list2 = [2, 3, 1, 1]
    if compare_lists(list1, list2):
        msg = 'identical list'
        return msg
    else:
        msg = 'NOT identical list'
        return msg


print(test_different_order())
