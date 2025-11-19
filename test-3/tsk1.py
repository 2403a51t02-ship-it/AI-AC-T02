def find_min_max(arr, low, high):
    # If only one element
    if low == high:
        return arr[low], arr[low]

    # If two elements
    if high == low + 1:
        if arr[low] < arr[high]:
            return arr[low], arr[high]
        else:
            return arr[high], arr[low]

    # More than two elements → divide
    mid = (low + high) // 2

    left_min, left_max = find_min_max(arr, low, mid)
    right_min, right_max = find_min_max(arr, mid + 1, high)

    # Combine (conquer)
    return min(left_min, right_min), max(left_max, right_max)


# ---------------- TEST CODE ----------------
arr = [23, 1, 45, 12, 7, 89, 34, 2, 56, 78, 10, 5]   # 12 elements

minimum, maximum = find_min_max(arr, 0, len(arr) - 1)

print("Array:", arr)
print("Minimum =", minimum)
print("Maximum =", maximum)
