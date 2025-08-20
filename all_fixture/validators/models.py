from decimal import Decimal

from django.core.validators import MaxValueValidator, MinValueValidator

MIN_0_MAX_99K = [
    MinValueValidator(Decimal("0.01")),
    MaxValueValidator(Decimal("99999.99")),
]
MIN_0_MAX_9KK = [
    MinValueValidator(Decimal("0.00")),
    MaxValueValidator(Decimal("9999999.99")),
]
