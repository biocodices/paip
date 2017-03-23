def percentage(n, total, decimal_places=0):
    if total == 0:
        return 0

    return round(100 * n / total, decimal_places)

